
import { Component, type OnInit, inject } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { ClarityModule } from '@clr/angular';
import { CommonModule } from '@angular/common';

import type { Project } from '@services/projects/project';
import { ProjectsService } from '@services/projects/projects.service';
import { ResourceState } from '@services/resource-state';
import { ErrorMessageComponent } from '@components/error-message/error-message.component';

/**
 * Represents the app component, which is the entry-point to the ViRelAy application.
 */
@Component({
    selector: 'virelay-app',
    imports: [
        CommonModule,
        RouterModule,
        ClarityModule,
        ErrorMessageComponent
    ],
    templateUrl: 'app.component.html',
    styleUrl: 'app.component.scss'
})
export class AppComponent implements OnInit {

    // #region Private Fields

    /**
     * Contains the projects service, which is used to load the projects of the current workspace.
     */
    private readonly projectsService: ProjectsService = inject(ProjectsService);

    /**
     * Contains the router, which is used to navigate to the projects.
     */
    private readonly router: Router = inject(Router);

    // #endregion

    // #region Public Properties

    /**
     * Contains the type of the enumeration that is used to represent the state of the loading of the projects. This is required, so that the
     * enumeration type can be referenced in the HTML template of the app component.
     */
    public readonly ResourceState: typeof ResourceState = ResourceState;

    /**
     * Gets or sets the current state of the loading of the projects.
     */
    public accessor projectsLoadingState: ResourceState = ResourceState.Loading;

    /**
     * Gets or sets the error message that is displayed when the projects could not be loaded.
     */
    public accessor projectsLoadingErrorMessage: string | null = null;

    /**
     * Gets or sets the projects of the current workspace.
     */
    public accessor projects: Project[] = [];

    // #endregion

    // #region OnInit Implementation

    /**
     * Is invoked when the app component is being initialized. Loads the projects from the server.
     */
    public ngOnInit(): void {

        this.projectsService
            .getAsync()
            .then((projects: Project[]) => {
                this.projects = projects;
                this.projectsLoadingState = ResourceState.Finished;

                if (this.router.url === '/') {
                    void this.router.navigate(['projects', this.projects[0].id]);
                }
            })
            .catch((exception: unknown) => {
                if (exception instanceof Error) {
                    this.projectsLoadingErrorMessage = exception.message.endsWith('.') ? exception.message : `${exception.message}.`;
                } else {
                    this.projectsLoadingErrorMessage = 'An unknown error occurred while loading the projects.';
                }
                this.projectsLoadingState = ResourceState.Failed;
            });
    }

    // #endregion
}
