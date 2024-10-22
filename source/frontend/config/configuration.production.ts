
import { InjectionToken } from '@angular/core';

/**
 * Represents the configuration of the application.
 */
export interface Configuration {

    /**
     * Indicates whether the application is running in production mode.
     */
    production: boolean,

    /**
     * The base URL of the ViRelAy backend REST API.
     */
    apiBaseUrl: string
}

/**
 * Contains the configuration for the development environment.
 */
const configuration: Configuration = {
    production: true,
    apiBaseUrl: ''
};

/**
 * An injection token that provides the configuration of the application.
 */
export const CONFIGURATION = new InjectionToken<Configuration>(
    'Configuration',
    {
        providedIn: 'root',
        factory: () => configuration
    }
);
