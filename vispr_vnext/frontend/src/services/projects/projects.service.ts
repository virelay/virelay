
import { map } from 'rxjs/operators';
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from 'src/environments/environment';

import { Project } from './project';

/**
 * Represents a service for managing projects in the current workspace.
 */
@Injectable()
export class ProjectsService {

    /**
     * Initializes a new ProjectsService instance.
     * @param httpClient The HTTP client, which is used to interface with the RESTful API.
     */
    public constructor(private httpClient: HttpClient) { }

    /**
     * Gets all projects from the current workspace.
     */
    public async getAsync(): Promise<Array<Project>> {
        return await this.httpClient
            .get<Array<Project>>(`${environment.apiBaseUrl}/projects`, {
                headers: new HttpHeaders({ 'Content-Type': 'application/json' })
            })
            .pipe(map(projects => projects.map(project => new Project(project))))
            .toPromise();
    }

    /**
     * Gets the project with the specified ID.
     * @param id The ID of the project that is to be retrieved.
     */
    public async getByIdAsync(id: number): Promise<Project> {
        return await this.httpClient
            .get<Project>(`${environment.apiBaseUrl}/projects/${id}`, {
                headers: new HttpHeaders({ 'Content-Type': 'application/json' })
            })
            .pipe(map(project => new Project(project)))
            .toPromise();
    }
}
