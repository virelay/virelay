import { type HttpErrorResponse, HttpStatusCode } from '@angular/common/http';

/**
 * Represents an enumeration for the different kinds of errors that a service exception can be caused by.
 */
export enum ServiceExceptionKind {

    /**
     * It is unknown what caused the error.
     */
    Unknown = 'Unknown',

    /**
     * The service is not available.
     */
    ServiceUnavailable = 'ServiceUnavailable',

    /**
     * A requested entity could not be found.
     */
    NotFound = 'NotFound',

    /**
     * An action could not be performed because of insufficient permissions.
     */
    PermissionDenied = 'PermissionDenied',

    /**
     * An action could not be performed because of an unhandled error.
     */
    InternalServerError = 'InternalServerError',

    /**
     * An error occurred during validation.
     */
    ValidationError = 'ValidationError'
}

/**
 * Represents an exception that is thrown when a service encounters an error.
 */
export class ServiceException extends Error {

    // #region Constructors

    /**
     * Initializes a new ServiceException instance.
     *
     * @param {string} serviceName The name of the service in which the error occurred.
     * @param {Object | undefined} errorDetails An object that contains extra information about the error.
     * @param {HttpErrorResponse | undefined} errorDetails.httpErrorResponse An optional HTTP error response that was returned by the HTTP client. If
     *  specified, the error details of the HTTP error will be  an HTTP error response is specified, then the service exception will be adopted by the
     *  service exception.
     * @param {string | undefined} errorDetails.message An optional error message, which will be added to the error message of the service exception,
     *  if specified.
     */
    public constructor(serviceName: string, errorDetails?: { httpErrorResponse?: HttpErrorResponse; message?: string }) {

        // If no HTTP error response was specified, then the cause of the error is unknown
        if (typeof errorDetails?.httpErrorResponse === 'undefined') {
            if (typeof errorDetails?.message === 'undefined') {
                super(`An unknown error occurred in the ${serviceName} service.`);
            } else {
                super(errorDetails.message);
            }
            this.kind = ServiceExceptionKind.Unknown;
            return;
        }

        // Uses the error message from the HTTP error response as the message for the exception
        if (typeof errorDetails.message === 'undefined') {
            super(errorDetails.httpErrorResponse.message);
        } else {
            super(
                `${errorDetails.message} ${errorDetails.httpErrorResponse.message}`
            );
        }

        // Sets the extra data of the error
        this.errorData = errorDetails.httpErrorResponse.error;

        // Checks if the error code is 0, in that case the service is unavailable
        if (errorDetails.httpErrorResponse.status === 0) {
            this.kind = ServiceExceptionKind.ServiceUnavailable;
            return;
        }

        // Checks the status code of the HTTP response to determine the kind of error that occurred
        const statusCode: HttpStatusCode = errorDetails.httpErrorResponse.status
        switch (statusCode) {
            case HttpStatusCode.Unauthorized:
                this.kind = ServiceExceptionKind.PermissionDenied;
                break;
            case HttpStatusCode.NotFound:
                this.kind = ServiceExceptionKind.NotFound;
                break;
            case HttpStatusCode.InternalServerError:
                this.kind = ServiceExceptionKind.InternalServerError;
                break;
            case HttpStatusCode.UnprocessableEntity:
                this.kind = ServiceExceptionKind.ValidationError;
                break;
            default:
                this.kind = ServiceExceptionKind.Unknown;
        }
    }

    // #endregion

    // #region Public Properties

    /**
     * Gets or sets the kind of error that the service exception was caused by.
     */
    public accessor kind: ServiceExceptionKind;

    /**
     * Gets or sets extra details about the error.
     */
    public accessor errorData: unknown;

    // #endregion
}
