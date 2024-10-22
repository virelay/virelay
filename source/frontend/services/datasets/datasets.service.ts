
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';
import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { Configuration, CONFIGURATION } from '@config/configuration';
import { Sample, SampleJson } from '@services/datasets/sample';
import { ServiceException } from '@services/service-exception';
import { UrlBuilder } from '@services/url-builder';

/**
 * Represents a service for managing dataset samples of a project.
 */
@Injectable({ providedIn: 'root' })
export class DatasetsService {

    // #region Private Fields

    /**
     * Contains the configuration of the application.
     */
    private readonly configuration: Configuration = inject(CONFIGURATION);

    /**
     * Contains the HTTP client, which is used to interface with the backend REST API.
     */
    private readonly httpClient: HttpClient = inject(HttpClient);

    // #endregion

    // #region Public Methods

    /**
     * Gets the dataset sample with the specified index.
     *
     * @param {number} projectId The ID of the project from which the dataset sample is to be retrieved.
     * @param {number} index The index of the dataset sample that is to be retrieved.
     *
     * @throws {ServiceException} The dataset sample could not be retrieved from the backend REST API.
     *
     * @returns {Promise<Sample>} Returns a promise that resolves when the dataset sample was retrieved from the backend REST API. The result of the
     *  promise contains the dataset sample that was retrieved from the backend REST API.
     */
    public async getAsync(projectId: number, index: number): Promise<Sample> {

        try {
            const url = UrlBuilder
                .for(this.configuration.apiBaseUrl)
                .withPath(
                    'api',
                    'projects',
                    projectId.toString(),
                    'dataset',
                    index.toString()
                )
                .build();

            return await lastValueFrom(this.httpClient
                .get<SampleJson>(url, { headers: new HttpHeaders({ 'Content-Type': 'application/json' }) })
                .pipe(map(sample => new Sample(sample, this.configuration.apiBaseUrl)))
            );
        } catch (httpErrorResponse: unknown) {
            if (httpErrorResponse instanceof HttpErrorResponse) {
                throw new ServiceException('Datasets Service', { httpErrorResponse });
            } else {
                throw new ServiceException(
                    'Datasets Service',
                    { message: `The dataset sample with the index ${index} of the project with the ID ${projectId} could not be retrieved.` }
                );
            }
        }
    }

    // #endregion
}
