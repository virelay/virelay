
import { bootstrapApplication } from '@angular/platform-browser';
import { provideRouter } from '@angular/router';
import { provideZoneChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import {
    ClarityIcons,
    bubbleChartIcon,
    checkIcon,
    errorStandardIcon,
    exportIcon,
    heatMapIcon,
    imageIcon,
    importIcon,
    layersIcon,
    libraryIcon,
    organizationIcon,
    pictureIcon,
    shareIcon,
    storageIcon,
    timesIcon,
    wandIcon
} from '@cds/core/icon';
import '@cds/core/icon/register.js';

import { routes } from '@app/app.routes';
import { AppComponent } from '@app/app.component';
import { provideAnimations } from '@angular/platform-browser/animations';

/**
 * Handles errors that occur during the bootstrapping of the app component.
 *
 * @param {unknown} exception The exception that was thrown during the bootstrapping of the app component.
 */
const handleBootstrappingError = (exception: unknown): void => {

    // There is no sensible way in which an error that occurs during the bootstrapping of the app component can be addressed, because at this point
    // the application itself did not manage to start; therefore, the only option left is to to inform the user that the application failed to start
    // up properly while bootstrapping; during the bootstrapping process, a load spinner is displayed and there is a hidden alert message that is
    // hidden; these are retrieved here, the load spinner is hidden, the alert is filled with the error message, and the alert is displayed
    const appComponentBootstrappingLoadSpinnerContainer = document
        .querySelector('#app-component-bootstrapping-load-spinner-container');
    const appComponentBootstrappingFailedAlertContainer = document
        .querySelector('#app-component-bootstrapping-failed-alert-container');
    const appComponentBootstrappingFailedAlertHeadline = document
        .querySelector('#app-component-bootstrapping-failed-alert-container .alert-heading');
    const appComponentBootstrappingFailedAlertMessage = document
        .querySelector('#app-component-bootstrapping-failed-alert-container .alert-message');

    // Hides the load spinner
    if (appComponentBootstrappingLoadSpinnerContainer !== null) {
        appComponentBootstrappingLoadSpinnerContainer.classList.add('hidden');
    }

    // Retrieves the error message from the exception that was thrown and inserts it into the alert
    if (appComponentBootstrappingFailedAlertHeadline !== null) {
        appComponentBootstrappingFailedAlertHeadline.textContent = 'Loading ViRelAy Failed';
    }
    if (appComponentBootstrappingFailedAlertMessage !== null) {
        if (exception !== null && exception instanceof Object && 'message' in exception && typeof exception.message === 'string') {
            appComponentBootstrappingFailedAlertMessage.textContent = exception.message;
        } else if (exception !== null && typeof exception === 'string') {
            appComponentBootstrappingFailedAlertMessage.textContent = exception;
        }
    }

    // Shows the alert
    if (appComponentBootstrappingFailedAlertContainer !== null) {
        appComponentBootstrappingFailedAlertContainer.classList.remove('hidden');
    }
};

// Sets the theme based on the user's preference, which is determined by evaluating the "prefers-color-scheme" media query; then an event listener is
// added to the media query, which listens for changes in the user's preference and updates the theme accordingly
const colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)');
document.body.setAttribute('cds-theme', colorSchemeQuery.matches ? 'dark' : 'light');
colorSchemeQuery.addEventListener('change', event => {
    document.body.setAttribute('cds-theme', event.matches ? 'dark' : 'light');
});

// Loads the Clarity icons that are used in the application
ClarityIcons.addIcons(
    bubbleChartIcon,
    checkIcon,
    errorStandardIcon,
    exportIcon,
    heatMapIcon,
    imageIcon,
    importIcon,
    layersIcon,
    libraryIcon,
    organizationIcon,
    pictureIcon,
    shareIcon,
    storageIcon,
    timesIcon,
    wandIcon
);

// When an Angular application is started, i.e., a user navigated to the website, then the index.html file will be loaded, which references the
// necessary JavaScript files for the application, these are then loaded and executed by the browser; the main.js (compiled from this main.ts) is the
// entrypoint to the application, which bootstraps the app component; the bootstrapApplication method compiles the AppComponent using the JIT
// compiler; it then creates the root zone for zone.js, which is used by Angular to determine when change-detection needs to be invoked; after that,
// the AppComponent is instantiated and its template gets processed and rendered, which may cause other components to the bootstrapped; finally, when
// the bootstrapping of the AppComponent has finished, it is inserted into the DOM; for this, the bootstrapping process finds the tag in the DOM that
// matches the selector of the AppComponent and inserts its rendered template into it, in this case, the tag is in the body of the index.html file
bootstrapApplication(
    AppComponent,
    {
        // Providers are used to provide services to the application via dependency injection, which are used by the components of the application
        providers: [

            // Provides the zone change detection by creating the root zone for zone.js
            provideZoneChangeDetection({ eventCoalescing: true }),

            // Provides the router for the application for which the routes are defined app.routes.ts
            provideRouter(routes),

            // Provides the HTTP client for the application, which is used to communicate with the backend REST API of ViRelAy
            provideHttpClient(),

            // Provides animation support for the application
            provideAnimations()
        ]
    }
).catch(handleBootstrappingError);
