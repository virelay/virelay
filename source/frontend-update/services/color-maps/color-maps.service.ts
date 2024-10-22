
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';

import { ColorMap } from '@services/color-maps/color-map';
import { configuration } from '@config/configuration';

/**
 * Represents a service for managing color maps.
 */
@Injectable({ providedIn: 'root' })
export class ColorMapsService {

    /**
     * Initializes a new ColorMapsService instance.
     * @param httpClient The HTTP client, which is used to interface with the backend REST API.
     */
    public constructor(private httpClient: HttpClient) { }

    /**
     * Gets all color maps.
     */
    public async getAsync(): Promise<Array<ColorMap>> {
        return await lastValueFrom(this.httpClient
            .get<Array<ColorMap>>(`${configuration.apiBaseUrl}/api/color-maps`, {
                headers: new HttpHeaders({ 'Content-Type': 'application/json' })
            })
            .pipe(map(colorMaps => colorMaps.map(colorMap => new ColorMap(colorMap, configuration.apiBaseUrl)))));
    }
}
