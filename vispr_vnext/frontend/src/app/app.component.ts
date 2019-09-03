
import { Component, OnInit } from '@angular/core';

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
     */
    public constructor(private projectsService: ProjectsService) { }

    /**
     * Contains the projects of the current workspace.
     */
    public projects: Array<Project> = new Array<Project>();

    /**
     * Is invoked when the app component is being initialized. Loads the projects from the server.
     */
    public async ngOnInit(): Promise<any> {

        this.projects = await this.projectsService.get();
    }
}
