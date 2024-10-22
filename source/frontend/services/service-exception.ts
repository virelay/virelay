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
 * Represents an enumeration for non-standard HTTP status codes.
 */
enum NonStandardHttpStatusCode {

    /**
     * The HTTP status code 0 is not defined by the HTTP standard but is often used by browsers to signal that the server did not respond to the
     * request.
     */
    NoResponse = 0,
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

        // Checks the status code of the HTTP response to determine the kind of error that occurred
        switch (errorDetails.httpErrorResponse.status) {
            case Number(NonStandardHttpStatusCode.NoResponse):
                this.kind = ServiceExceptionKind.ServiceUnavailable;
                break;
            case Number(HttpStatusCode.Unauthorized):
                this.kind = ServiceExceptionKind.PermissionDenied;
                break;
            case Number(HttpStatusCode.NotFound):
                this.kind = ServiceExceptionKind.NotFound;
                break;
            case Number(HttpStatusCode.InternalServerError):
                this.kind = ServiceExceptionKind.InternalServerError;
                break;
            case Number(HttpStatusCode.UnprocessableEntity):
                this.kind = ServiceExceptionKind.ValidationError;
                break;
            default:
                this.kind = ServiceExceptionKind.Unknown;
        }

        // Sets the extra data of the error.
        this.errorData = errorDetails.httpErrorResponse.error;
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
