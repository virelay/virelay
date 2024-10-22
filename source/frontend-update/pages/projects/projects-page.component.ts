
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ClarityModule } from "@clr/angular";

/**
 * Represents the projects page component, which is the main page of the application that hosts the projects that are currently open in the workspace.
 */
@Component({
    selector: 'virelay-projects-page',
    standalone: true,
    imports: [],
    templateUrl: 'projects-page.component.html',
    styleUrl: 'projects-page.component.scss'
})
export class ProjectsPageComponent { }
