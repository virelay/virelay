
import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';

import { Attribution } from '@services/attributions/attribution';
import { configuration } from '@config/configuration';
import { ServiceException } from '@services/service-exception';

/**
 * Represents a service for managing attributions of a project.
 */
@Injectable({ providedIn: 'root' })
export class AttributionsService {

    /**
     * Contains the HTTP client, which is used to interface with the backend REST API.
     */
    private readonly httpClient: HttpClient = inject(HttpClient);

    /**
     * Gets the attribution with the specified index.
     *
     * @param projectId The ID of the project from which the attribution is to be retrieved.
     * @param index The index of the attribution that is to be retrieved.
     * @param imageMode Determines whether the heatmap URLs of the retrieved attributions
     *   point to the heatmaps or to heatmaps that are superimposed onto the dataset sample
     *   from which the heatmap was generated. Modes are 'input', 'overlay' and 'attribution'
     *
     * @returns {Promise<Attribution>} Returns a promise that resolves when the attribution was retrieved from the backend REST API. The result of the
     *   promise contains the attribution that was retrieved from the backend REST API.
     */
    public async getAsync(projectId: number, index: number, imageMode: string): Promise<Attribution> {
        return await lastValueFrom(this.httpClient
            .get<Attribution>(`${configuration.apiBaseUrl}/api/projects/${projectId}/attributions/${index}`, {
                headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
                params: new HttpParams().set('imageMode', imageMode)
            })
            .pipe(map(attribution => new Attribution(attribution, configuration.apiBaseUrl))));
    }
}
