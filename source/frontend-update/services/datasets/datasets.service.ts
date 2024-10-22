
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';

import { configuration } from '@config/configuration';
import { Sample } from '@services/datasets/sample';

/**
 * Represents a service for managing dataset samples of a project.
 */
@Injectable({ providedIn: 'root' })
export class DatasetsService {

    /**
     * Initializes a new DatasetService instance.
     * @param httpClient The HTTP client, which is used to interface with the backend REST API.
     */
    public constructor(private httpClient: HttpClient) { }

    /**
     * Gets the dataset sample with the specified index.
     * @param projectId The ID of the project from which the dataset sample is to be retrieved.
     * @param index The index of the dataset sample that is to be retrieved.
     */
    public async getAsync(projectId: number, index: number): Promise<Sample> {
        return await lastValueFrom(this.httpClient
            .get<Sample>(`${configuration.apiBaseUrl}/api/projects/${projectId}/dataset/${index}`, {
                headers: new HttpHeaders({ 'Content-Type': 'application/json' })
            })
            .pipe(map(sample => new Sample(sample, configuration.apiBaseUrl))));
    }
}
