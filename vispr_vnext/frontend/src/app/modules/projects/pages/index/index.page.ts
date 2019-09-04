
import { Component, OnInit } from '@angular/core';

import { ProjectsService } from 'src/services/projects/projects.service';
import { ActivatedRoute } from '@angular/router';
import { Project } from 'src/services/projects/project';
import { AnalysisMethod } from 'src/services/projects/analysis-method';

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

    /**
     * Contains the analysis method that was selected by the user.
     */
    public selectedAnalysisMethod: AnalysisMethod = null;

    /**
     * Contains the name of the selected category.
     */
    public selectedCategory: string;

    /**
     * Contains the name of the selected clustering.
     */
    public selectedClustering: string;

    /**
     * Contains the name of the selected embedding.
     */
    public selectedEmbedding: string;

    public graph = {
        data: [
            { x: [1, 2, 3], y: [2, 6, 3], type: 'scatter', mode: 'lines+points', marker: {color: 'red'} },
            { x: [1, 2, 3], y: [2, 5, 3], type: 'bar' },
        ],
        layout: { title: 'A Fancy Plot', paper_bgcolor: '#00000000', plot_bgcolor: '#00000000' },
        responsive: true
    };

    /**
     * Reloads the project and all its information.
     */
    private async refresh() {
        this.isLoadingProject = true;
        this.project = await this.projectsService.getByIdAsync(this.id);

        this.selectedAnalysisMethod = this.project.analysisMethods[0];
        this.selectedCategory = this.selectedAnalysisMethod.categories[0];
        this.selectedClustering = this.selectedAnalysisMethod.clusterings[0];
        if (this.selectedAnalysisMethod.embeddings.filter(embedding => embedding === 'tsne').length > 0) {
            this.selectedEmbedding = 'tsne';
        } else {
            this.selectedEmbedding = this.selectedAnalysisMethod.embeddings[0];
        }

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
