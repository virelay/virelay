
import { Component, OnInit } from '@angular/core';

import { Plotly } from 'plotly.js/dist/plotly.js';
import { ProjectsService } from 'src/services/projects/projects.service';
import { ActivatedRoute } from '@angular/router';
import { Project } from 'src/services/projects/project';
import { AnalysisMethod } from 'src/services/projects/analysis-method';
import { AnalysesService } from 'src/services/analyses/analyses.service';
import { Analysis } from 'src/services/analyses/analysis';
import { Embedding } from 'src/services/analyses/embedding';

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
    public constructor(
        private projectsService: ProjectsService,
        private analysesService: AnalysesService,
        private route: ActivatedRoute
    ) { }

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

    /**
     * Contains the current analysis.
     */
    private _analysis: Analysis;

    /**
     * Gets the current analysis.
     */
    public get analysis(): Analysis {
        return this._analysis;
    }

    /**
     * Sets the current analysis.
     * @param value The
     */
    public set analysis(value: Analysis) {
        this._analysis = value;

        const clusters = new Array<number>();
        for (const cluster of this.analysis.embedding.map(embedding => embedding.cluster)) {
            if (clusters.indexOf(cluster) === -1) {
                clusters.push(cluster);
            }
        }

        this.graphData = new Array<Plotly.Data>();
        for (const cluster of clusters) {
            const embeddingsInCluster = this.analysis.embedding.filter(embedding => embedding.cluster === cluster);
            this.graphData.push({
                name: `Cluster ${cluster}`,
                x: embeddingsInCluster.map(embedding => embedding.value[0]),
                y: embeddingsInCluster.map(embedding => embedding.value[1]),
                type: 'scatter',
                mode: 'markers',
                marker: { size: 12 }
            });
        }
    }

    /**
     * Contains the data of the PlotlyJS graph.
     */
    public graphData: Array<Plotly.Data>;

    /**
     * Contains the layout of the PlotlyJS graph.
     */
    public graphLayout: Partial<Plotly.Layout> = {
        autosize: true,
        paper_bgcolor: '#00000000',
        plot_bgcolor: '#00000000',
        xaxis: {
            autorange: true,
            showgrid: false,
            zeroline: false,
            showline: false,
            autotick: false,
            ticks: '',
            showticklabels: false
        },
        yaxis: {
            autorange: true,
            showgrid: false,
            zeroline: false,
            showline: false,
            autotick: false,
            ticks: '',
            showticklabels: false
        }
    };

    public graph = {
        data: [
            { x: [1, 2, 3], y: [2, 6, 3], type: 'scatter', mode: 'markers', marker: { size: 12 } }
        ],
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

        this.analysis = await this.analysesService.getAsync(
            this.project.id,
            this.selectedAnalysisMethod.name,
            this.selectedCategory,
            this.selectedClustering,
            this.selectedEmbedding
        );

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
