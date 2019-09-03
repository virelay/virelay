
import { Component, OnInit } from '@angular/core';

import { ProjectsService } from 'src/services/projects/projects.service';
import { ActivatedRoute } from '@angular/router';
import { Project } from 'src/services/projects/project';

/**
 * Represents the index page of a project
 */
@Component({
    selector: 'page-projects-index',
    styleUrls: ['index.page.scss'],
    templateUrl: 'index.page.html'
})
export class IndexPage implements OnInit {

    /**
     * Initializes a new IndexPage instance.
     * @param projectsService The service which is used to manage projects.
     */
    public constructor(private projectsService: ProjectsService, private route: ActivatedRoute) { }

    /**
     * Contains a value that determine whether the project is currently being loaded.
     */
    public isLoadingProject: boolean;

    /**
     * Contains the ID of the project.
     */
    public id: number;

    /**
     * Contains the project that is being displayed.
     */
    public project: Project;

    public graph = {
        data: [
            { x: [1, 2, 3], y: [2, 6, 3], type: 'scatter', mode: 'lines+points', marker: {color: 'red'} },
            { x: [1, 2, 3], y: [2, 5, 3], type: 'bar' },
        ],
        layout: { autosize: true, title: 'A Fancy Plot', paper_bgcolor: '#00000000', plot_bgcolor: '#00000000' },
        responsive: true
    };

    /**
     * Reloads the project and all its information.
     */
    private async refresh() {
        this.isLoadingProject = true;
        this.project = await this.projectsService.getByIdAsync(this.id);
        this.isLoadingProject = false;
    }

    /**
     * Is invoked when the component is initialized. Retrieves the ID of the project from the URL and loads it
     */
    public ngOnInit(): void {

        // Subscribes for changes of the route, when the route has changed, then the project ID is retrieved from the
        // URL and the project is loaded
        this.route.paramMap.subscribe(paramMap => {
            if (paramMap.has('id') && paramMap.get('id')) {
                this.id = parseInt(paramMap.get('id'), 10);
                this.refresh();
            }
        });
    }
}
