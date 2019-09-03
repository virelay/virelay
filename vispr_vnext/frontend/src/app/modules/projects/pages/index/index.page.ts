
import { Component, OnInit } from '@angular/core';

import { ProjectsService } from 'src/services/projects/projects.service';
import { ActivatedRoute } from '@angular/router';

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
     * Contains the ID of the project.
     */
    public id: number;

    /**
     * Is invoked when the component is initialized. Retrieves the ID of the project from the URL and loads it
     */
    public async ngOnInit(): Promise<any> {

        // Subscribes for changes of the route, when the route has changed, then the project ID is retrieved from the
        // URL and the project is loaded
        this.route.paramMap.subscribe(paramMap => {
            if (paramMap.has('id') && paramMap.get('id')) {
                this.id = parseInt(paramMap.get('id'), 10);
            }
        });
    }
}
