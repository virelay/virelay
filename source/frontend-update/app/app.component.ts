
import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { ClarityModule } from "@clr/angular";
import { Project } from '@services/projects/project';

import {ProjectsService} from '@services/projects/projects.service';

/**
 * Represents the app component, which is the entry-point to the ViRelAy application.
 */
@Component({
    selector: 'virelay-app',
    standalone: true,
    imports: [
        CommonModule,
        RouterOutlet,
        ClarityModule
    ],
    templateUrl: 'app.component.html',
    styleUrl: 'app.component.scss'
})
export class AppComponent implements OnInit {

    /**
     * Contains the projects service, which is used to load the projects of the current workspace.
     */
    private readonly projectsService: ProjectsService = inject(ProjectsService);

    /**
     * Contains the router, which is used to navigate to the projects.
     */
    private readonly router: Router = inject(Router);

    /**
     * Contains a value that determines whether the projects are currently being loaded.
     */
    public isLoadingProjects: boolean = true;

    /**
     * Contains the projects of the current workspace.
     */
    public projects?: Array<Project>;

    /**
     * Is invoked when the app component is being initialized. Loads the projects from the server.
     *
     * @returns {Promise<void>} Returns a promise that resolves when the projects have been loaded.
     */
    public async ngOnInit(): Promise<void> {

        // Loads the projects from the RESTful API
        this.projects = await this.projectsService.getAsync();
        this.isLoadingProjects = false;

        // Navigates the user to the first project
        if (this.router.url === '/') {
            this.router.navigate(['projects', this.projects[0].id]);
        }
    }
}
