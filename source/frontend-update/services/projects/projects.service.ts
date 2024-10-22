
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';

import { configuration } from '@config/configuration';
import { Project } from '@services/projects/project';

/**
 * Represents a service for managing projects in the current workspace.
 */
@Injectable({ providedIn: 'root' })
export class ProjectsService {

    /**
     * Initializes a new ProjectsService instance.
     * @param httpClient The HTTP client, which is used to interface with the backend REST API.
     */
    public constructor(private httpClient: HttpClient) { }

    /**
     * Gets all projects from the current workspace.
     */
    public async getAsync(): Promise<Array<Project>> {
        return await lastValueFrom(this.httpClient
            .get<Array<Project>>(`${configuration.apiBaseUrl}/api/projects`, {
                headers: new HttpHeaders({ 'Content-Type': 'application/json' })
            })
            .pipe(map(projects => projects.map(project => new Project(project)))));
    }

    /**
     * Gets the project with the specified ID.
     * @param id The ID of the project that is to be retrieved.
     */
    public async getByIdAsync(id: number): Promise<Project> {
        return await lastValueFrom(this.httpClient
            .get<Project>(`${configuration.apiBaseUrl}/api/projects/${id}`, {
                headers: new HttpHeaders({ 'Content-Type': 'application/json' })
            })
            .pipe(map(project => new Project(project))));
    }
}
