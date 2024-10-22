
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';
import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { Analysis, AnalysisJson } from '@services/analyses/analysis';
import { Configuration, CONFIGURATION } from '@config/configuration';
import { ServiceException } from '@services/service-exception';
import { UrlBuilder } from '@services/url-builder';

/**
 * Represents a service for managing analyses of a project.
 */
@Injectable({ providedIn: 'root' })
export class AnalysesService {

    // #region Private Fields

    /**
     * Contains the configuration of the application.
     */
    private readonly configuration: Configuration = inject(CONFIGURATION);

    /**
     * Contains the HTTP client that is used to communicate with the REST API.
     */
    private readonly httpClient: HttpClient = inject(HttpClient);

    // #endregion

    // #region Public Methods

    /**
     * Gets the specified analysis from the project.
     *
     * @param {number} projectId The ID of the project from which the analysis is to be retrieved.
     * @param {string} analysisMethod The name of the analysis method from which the analysis is to be retrieved.
     * @param {string} category The name of the category from which the analysis is to be retrieved.
     * @param {string} clustering The name of the clustering that was applied to the analysis.
     * @param {string} embedding The name of the embedding that was applied to the analysis.
     *
     * @throws {ServiceException} The analysis could not be retrieved from the backend REST API.
     *
     * @returns {Promise<Analysis>} Returns a promise that resolves when the analysis was retrieved from the backend REST API. The result of the
     *  promise contains the analysis that was retrieved from the backend REST API.
     */
    public async getAsync(
        projectId: number,
        analysisMethod: string,
        category: string,
        clustering: string,
        embedding: string
    ): Promise<Analysis> {

        try {
            const url = UrlBuilder
                .for(this.configuration.apiBaseUrl)
                .withPath(
                    'api',
                    'projects',
                    projectId,
                    'analyses',
                    analysisMethod
                )
                .withQueryParameter('category', category)
                .withQueryParameter('clustering', clustering)
                .withQueryParameter('embedding', embedding)
                .build();

            return await lastValueFrom(
                this.httpClient
                    .get<AnalysisJson>(url, { headers: new HttpHeaders({ 'Content-Type': 'application/json' }) })
                    .pipe(map(analysis => new Analysis(analysis)))
            );
        } catch (httpErrorResponse: unknown) {
            if (httpErrorResponse instanceof HttpErrorResponse) {
                throw new ServiceException('Analyses Service', { httpErrorResponse });
            } else {
                throw new ServiceException(
                    'Analyses Service',
                    {
                        message:
                            `The analysis ${analysisMethod} from the category ${category} of the project with the ID ${projectId} could not be ` +
                            'retrieved.'
                    }
                );
            }
        }
    }

    // #endregion
}
