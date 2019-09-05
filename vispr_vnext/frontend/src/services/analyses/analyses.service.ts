
import { map } from 'rxjs/operators';
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from 'src/environments/environment';

import { Analysis } from './analysis';
import { AnalysisMethod } from '../projects/analysis-method';

/**
 * Represents a service for managing analyses of a project.
 */
@Injectable()
export class AnalysesService {

    /**
     * Initializes a new AnalysesService instance.
     * @param httpClient The HTTP client, which is used to interface with the RESTful API.
     */
    public constructor(private httpClient: HttpClient) { }

    /**
     * Gets the specified analysis from the project.
     * @param projectId The ID of the project from which the analysis is to be retrieved.
     * @param analysisMethod The name of the analysis method from which the analysis is to be retrieved.
     * @param category The name of the category from which the analysis is to be retrieved.
     * @param clustering The name of the clustering that was applied to the analysis.
     * @param embedding The name of the embedding that was applied to the analysis.
     */
    public async getAsync(
        projectId: number,
        analysisMethod: string,
        category: string,
        clustering: string,
        embedding: string
    ): Promise<Analysis> {
        return await this.httpClient
            .get<Analysis>(`${environment.apiBaseUrl}/api/projects/${projectId}/analyses/${analysisMethod}?category=${category}&clustering=${clustering}&embedding=${embedding}`, {
                headers: new HttpHeaders({ 'Content-Type': 'application/json' })
            })
            .pipe(map(analysis => new Analysis(analysis)))
            .toPromise();
    }
}
