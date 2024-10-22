
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';
import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { Attribution, AttributionJson } from '@services/attributions/attribution';
import { Configuration, CONFIGURATION } from '@config/configuration';
import { ServiceException } from '@services/service-exception';
import { AttributionImageMode } from '@services/attributions/attribution-image-mode';
import { UrlBuilder } from '@services/url-builder';

/**
 * Represents a service for managing attributions of a project.
 */
@Injectable({ providedIn: 'root' })
export class AttributionsService {

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
     * Gets the attributions with the specified indices.
     *
     * @param {number} projectId The ID of the project from which the attribution is to be retrieved.
     * @param {number[]} indices The indices of the attributions that are to be retrieved.
     * @param {AttributionImageMode} imageMode Determines whether the heatmap URLs of the retrieved attributions point to the heatmaps or to heatmaps
     *  that are superimposed onto the dataset sample from which the heatmap was generated. Modes are 'input', 'overlay' and 'attribution'
     *
     * @throws {ServiceException} One or more attributions could not be retrieved from the backend REST API.
     *
     * @returns {Promise<Attribution>} Returns a promise that resolves when the attributions were retrieved from the backend REST API. The result of
     *  the promise contains the attributions that were retrieved from the backend REST API.
     */
    public async getAsync(projectId: number, indices: number[], imageMode: AttributionImageMode): Promise<Attribution[]> {

        try {
            const url = UrlBuilder
                .for(this.configuration.apiBaseUrl)
                .withPath(
                    'api',
                    'projects',
                    projectId.toString(),
                    'attributions'
                )
                .withQueryParameter('indices', indices.join(','))
                .withQueryParameter('imageMode', imageMode)
                .build();

            return await lastValueFrom(this.httpClient
                .get<AttributionJson[]>(url, { headers: new HttpHeaders({ 'Content-Type': 'application/json' }) })
                .pipe(map(attributions => attributions.map(attribution => new Attribution(attribution, this.configuration.apiBaseUrl))))
            );
        } catch (httpErrorResponse: unknown) {
            if (httpErrorResponse instanceof HttpErrorResponse) {
                throw new ServiceException('Attributions Service', { httpErrorResponse });
            } else {
                throw new ServiceException(
                    'Attributions Service',
                    { message: `One or more of the requested attributions of the project with the ID ${projectId} could not be retrieved.` }
                );
            }
        }
    }

    /**
     * Gets the attribution with the specified index.
     *
     * @param {number} projectId The ID of the project from which the attribution is to be retrieved.
     * @param {number} index The index of the attribution that is to be retrieved.
     * @param {AttributionImageMode} imageMode Determines whether the heatmap URLs of the retrieved attributions point to the heatmaps or to heatmaps
     *  that are superimposed onto the dataset sample from which the heatmap was generated. Modes are 'input', 'overlay' and 'attribution'
     *
     * @throws {ServiceException} The attribution could not be retrieved from the backend REST API.
     *
     * @returns {Promise<Attribution>} Returns a promise that resolves when the attribution was retrieved from the backend REST API. The result of the
     *  promise contains the attribution that was retrieved from the backend REST API.
     */
    public async getByIndexAsync(projectId: number, index: number, imageMode: AttributionImageMode): Promise<Attribution> {

        try {
            const url = UrlBuilder
                .for(this.configuration.apiBaseUrl)
                .withPath(
                    'api',
                    'projects',
                    projectId.toString(),
                    'attributions',
                    index.toString()
                )
                .withQueryParameter('imageMode', imageMode)
                .build();

            return await lastValueFrom(this.httpClient
                .get<AttributionJson>(url, { headers: new HttpHeaders({ 'Content-Type': 'application/json' }) })
                .pipe(map(attribution => new Attribution(attribution, this.configuration.apiBaseUrl)))
            );
        } catch (httpErrorResponse: unknown) {
            if (httpErrorResponse instanceof HttpErrorResponse) {
                throw new ServiceException('Attributions Service', { httpErrorResponse });
            } else {
                throw new ServiceException(
                    'Attributions Service',
                    { message: `The attribution with the index ${index} of the project with the ID ${projectId} could not be retrieved.` }
                );
            }
        }
    }

    // #endregion
}
