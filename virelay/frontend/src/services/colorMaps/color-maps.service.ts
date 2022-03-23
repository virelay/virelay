
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { ColorMap } from './color-map';

/**
 * Represents a service for managing color maps.
 */
@Injectable()
export class ColorMapsService {

    /**
     * Initializes a new ColorMapsService instance.
     * @param httpClient The HTTP client, which is used to interface with the RESTful API.
     */
    public constructor(private httpClient: HttpClient) { }

    /**
     * Gets all color maps.
     */
    public async getAsync(): Promise<Array<ColorMap>> {
        return await lastValueFrom(this.httpClient
            .get<Array<ColorMap>>(`${environment.apiBaseUrl}/api/color-maps`, {
                headers: new HttpHeaders({ 'Content-Type': 'application/json' })
            })
            .pipe(map(colorMaps => colorMaps.map(colorMap => new ColorMap(colorMap, environment.apiBaseUrl)))));
    }
}
