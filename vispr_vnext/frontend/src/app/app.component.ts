
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { ProjectsService } from 'src/services/projects/projects.service';
import { Project } from 'src/services/projects/project';

/**
 * Represents the app component, which is the entry-point to the VISPR application.
 */
@Component({
    selector: 'app-root',
    templateUrl: 'app.component.html',
    styleUrls: ['app.component.scss']
})
export class AppComponent implements OnInit {

    /**
     * Initializes a new AppComponent instance.
     * @param projectsService The projects service, which is used to load the projects of the current workspace.
     * @param router The router, which is used to navigate to the projects.
     */
    public constructor(private projectsService: ProjectsService, private router: Router) { }

    /**
     * Contains a value that determines whether the projects are currently being loaded.
     */
    public isLoadingProjects: boolean;

    /**
     * Contains the projects of the current workspace.
     */
    public projects: Array<Project>;

    /**
     * Is invoked when the app component is being initialized. Loads the projects from the server.
     */
    public async ngOnInit(): Promise<void> {

        // Loads the projects from the RESTful API
        this.isLoadingProjects = true;
        this.projects = await this.projectsService.getAsync();
        this.isLoadingProjects = false;

        // Navigates the user to the first project
        this.router.navigate(['projects', this.projects[0].id]);
    }
}
