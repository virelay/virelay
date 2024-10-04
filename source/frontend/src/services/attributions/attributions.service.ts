
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { Attribution } from './attribution';

/**
 * Represents a service for managing attributions of a project.
 */
@Injectable()
export class AttributionsService {

    /**
     * Initializes a new AttributionsService instance.
     * @param httpClient The HTTP client, which is used to interface with the RESTful API.
     */
    public constructor(private httpClient: HttpClient) { }

    /**
     * Gets the attribution with the specified index.
     * @param projectId The ID of the project from which the attribution is to be retrieved.
     * @param index The index of the attribution that is to be retrieved.
     * @param imageMode Determines whether the heatmap URLs of the retrieved attributions
     * point to the heatmaps or to heatmaps that are superimposed onto the dataset sample
     * from which the heatmap was generated. Modes are 'input', 'overlay' and 'attribution'
     */
    public async getAsync(projectId: number, index: number, imageMode: string): Promise<Attribution> {
        return await lastValueFrom(this.httpClient
            .get<Attribution>(`${environment.apiBaseUrl}/api/projects/${projectId}/attributions/${index}`, {
                headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
                params: new HttpParams().set('imageMode', imageMode)
            })
            .pipe(map(attribution => new Attribution(attribution, environment.apiBaseUrl))));
    }
}
