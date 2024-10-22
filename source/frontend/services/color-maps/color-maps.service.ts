
import { map } from 'rxjs/operators';
import { lastValueFrom } from 'rxjs';
import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { ColorMap, ColorMapJson } from '@services/color-maps/color-map';
import { Configuration, CONFIGURATION } from '@config/configuration';
import { ServiceException } from '@services/service-exception';
import { UrlBuilder } from '@services/url-builder';

/**
 * Represents a service for managing color maps.
 */
@Injectable({ providedIn: 'root' })
export class ColorMapsService {

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
     * Gets all color maps.
     *
     * @throws {ServiceException} The color maps could not be retrieved from the backend REST API.
     *
     * @returns {Promise<Array<ColorMap>>} Returns a promise that resolves when the color maps were retrieved from the backend REST API. The result of
     *  the promise contains the color maps that were retrieved from the backend REST API.
     */
    public async getAsync(): Promise<ColorMap[]> {

        try {
            const url = UrlBuilder
                .for(this.configuration.apiBaseUrl)
                .withPath(
                    'api',
                    'color-maps'
                )
                .build();

            return await lastValueFrom(this.httpClient
                .get<ColorMapJson[]>(url, { headers: new HttpHeaders({ 'Content-Type': 'application/json' }) })
                .pipe(map(colorMaps => colorMaps.map(colorMap => new ColorMap(colorMap, this.configuration.apiBaseUrl))))
            );
        } catch (httpErrorResponse: unknown) {
            if (httpErrorResponse instanceof HttpErrorResponse) {
                throw new ServiceException('Color Maps Service', { httpErrorResponse });
            } else {
                throw new ServiceException('Color Maps Service', { message: 'The color maps could not be retrieved.' });
            }
        }
    }

    // #endregion
}
