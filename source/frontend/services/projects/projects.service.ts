
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';
import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { Configuration, CONFIGURATION } from '@config/configuration';
import { Project, ProjectJson } from '@services/projects/project';
import { ServiceException } from '@services/service-exception';
import { UrlBuilder } from '@services/url-builder';

/**
 * Represents a service for managing projects in the current workspace.
 */
@Injectable({ providedIn: 'root' })
export class ProjectsService {

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
     * Gets all projects from the current workspace.
     *
     * @throws {ServiceException} The projects could not be retrieved from the backend REST API.
     *
     * @returns {Promise<Array<Project>>} Returns a promise that resolves when the projects were retrieved from the backend REST API. The result of
     *  the promise contains the projects that were retrieved from the backend REST API.
     */
    public async getAsync(): Promise<Project[]> {

        try {
            const url = UrlBuilder
                .for(this.configuration.apiBaseUrl)
                .withPath(
                    'api',
                    'projects'
                )
                .build();

            return await lastValueFrom(this.httpClient
                .get<ProjectJson[]>(url, { headers: new HttpHeaders({ 'Content-Type': 'application/json' }) })
                .pipe(map(projects => projects.map(project => new Project(project))))
            );
        } catch (httpErrorResponse: unknown) {
            if (httpErrorResponse instanceof HttpErrorResponse) {
                throw new ServiceException('Projects Service', { httpErrorResponse });
            } else {
                throw new ServiceException('Projects Service', { message: `The projects could not be retrieved.` });
            }
        }
    }

    /**
     * Gets the project with the specified ID.
     *
     * @param {number} id The ID of the project that is to be retrieved.
     *
     * @throws {ServiceException} The project could not be retrieved from the backend REST API.
     *
     * @returns {Promise<Project>} Returns a promise that resolves when the project was retrieved from the backend REST API. The result of the promise
     *  contains the project that was retrieved from the backend REST API.
     */
    public async getByIdAsync(id: number): Promise<Project> {

        try {
            const url = UrlBuilder
                .for(this.configuration.apiBaseUrl)
                .withPath(
                    'api',
                    'projects',
                    id
                )
                .build();

            return await lastValueFrom(this.httpClient
                .get<ProjectJson>(url, { headers: new HttpHeaders({ 'Content-Type': 'application/json' }) })
                .pipe(map(project => new Project(project)))
            );
        } catch (httpErrorResponse: unknown) {
            if (httpErrorResponse instanceof HttpErrorResponse) {
                throw new ServiceException('Projects Service', { httpErrorResponse });
            } else {
                throw new ServiceException('Projects Service', { message: `The project with the ID ${id} could not be retrieved.` });
            }
        }
    }

    // #endregion
}
