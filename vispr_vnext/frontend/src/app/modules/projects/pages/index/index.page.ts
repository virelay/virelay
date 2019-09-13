
import { Component, OnInit } from '@angular/core';

import { Plotly } from 'plotly.js/dist/plotly.js';
import { ProjectsService } from 'src/services/projects/projects.service';
import { ActivatedRoute } from '@angular/router';
import { Project } from 'src/services/projects/project';
import { AnalysisMethod } from 'src/services/projects/analysis-method';
import { AnalysesService } from 'src/services/analyses/analyses.service';
import { Analysis } from 'src/services/analyses/analysis';
import { AnalysisCategory } from 'src/services/projects/analysis-category';
import { AttributionsService } from 'src/services/attributions/attributions.service';
import { Sample } from 'src/services/dataset/sample';
import { DatasetService } from 'src/services/dataset/dataset.service';
import { Attribution } from 'src/services/attributions/attribution';

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
        private attributionsService: AttributionsService,
        private datasetService: DatasetService,
        private route: ActivatedRoute
    ) { }

    /**
     * Contains a value that determines whether the component is currently loading data from the RESTful API.
     */
    public isLoading: boolean;

    /**
     * Contains a value that determines whether the selected attributions and dataset samples are currently being loaded
     * from the RESTful API.
     */
    public isLoadingSelection: boolean;

    /**
     * Contains the ID of the project.
     */
    public id: number;

    /**
     * Contains the project that is being displayed.
     */
    public project: Project;

    /**
     * Contains the dataset sample of the embedding that the user is currently hovering its mouse over.
     */
    public datasetSampleHoverPreview: Sample;

    /**
     * Contains the analysis method that was selected by the user.
     */
    private _selectedAnalysisMethod: AnalysisMethod;

    /**
     * Gets the analysis method that was selected by the user.
     */
    public get selectedAnalysisMethod(): AnalysisMethod {
        return this._selectedAnalysisMethod;
    }

    /**
     * Sets the analysis method that was selected by the user.
     */
    public set selectedAnalysisMethod(value: AnalysisMethod) {
        this._selectedAnalysisMethod = value;
        if (value) {
            this.selectedCategory = this.selectedAnalysisMethod.categories[0];
            this.selectedClustering = this.selectedAnalysisMethod.clusterings[0];
            if (this.selectedAnalysisMethod.embeddings.filter(embedding => embedding === 'tsne').length > 0) {
                this.selectedEmbedding = 'tsne';
            } else {
                this.selectedEmbedding = this.selectedAnalysisMethod.embeddings[0];
            }
            this.refreshAnalysisAsync();
        }
    }

    /**
     * Contains the name of the selected category.
     */
    private _selectedCategory: AnalysisCategory;

    /**
     * Gets the name of the selected category.
     */
    public get selectedCategory(): AnalysisCategory {
        return this._selectedCategory;
    }

    /**
     * Sets the name of the selected category.
     */
    public set selectedCategory(value: AnalysisCategory) {
        this._selectedCategory = value;
        if (value) {
            this.refreshAnalysisAsync();
        }
    }

    /**
     * Contains the name of the selected clustering.
     */
    private _selectedClustering: string;

    /**
     * Gets the name of the selected clustering.
     */
    public get selectedClustering(): string {
        return this._selectedClustering;
    }

    /**
     * Sets the name of the selected clustering.
     */
    public set selectedClustering(value: string) {
        this._selectedClustering = value;
        if (value) {
            this.refreshAnalysisAsync();
        }
    }

    /**
     * Contains the name of the selected embedding.
     */
    private _selectedEmbedding: string;

    /**
     * Gets the name of the selected embedding.
     */
    public get selectedEmbedding(): string {
        return this._selectedEmbedding;
    }

    /**
     * Sets the name of the selected embedding.
     */
    public set selectedEmbedding(value: string) {
        this._selectedEmbedding = value;
        if (value) {
            this.refreshAnalysisAsync();
        }
    }

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
                marker: { size: 12 },
                hoverinfo: 'none',
                attributionIndices: embeddingsInCluster.map(embedding => embedding.attributionIndex)
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
        dragmode: 'lasso',
        hovermode: 'closest',
        hoverdistance: 1,
        showlegend: false,
        xaxis: {
            showgrid: false,
            zeroline: false,
            showticklabels: false
        },
        yaxis: {
            showgrid: false,
            zeroline: false,
            showticklabels: false
        },
        paper_bgcolor: '#00000000',
        plot_bgcolor: '#00000000'
    };

    public selectedAttributions: Array<Attribution>;

    /**
     * Reloads the project and all its information.
     */
    private async refreshProjectAsync() {
        this.isLoading = true;
        this.project = await this.projectsService.getByIdAsync(this.id);

        this.selectedAttributions = null;
        this.selectedAnalysisMethod = this.project.analysisMethods[0];
        this.selectedCategory = this.selectedAnalysisMethod.categories[0];
        this.selectedClustering = this.selectedAnalysisMethod.clusterings[0];
        if (this.selectedAnalysisMethod.embeddings.filter(embedding => embedding === 'tsne').length > 0) {
            this.selectedEmbedding = 'tsne';
        } else {
            this.selectedEmbedding = this.selectedAnalysisMethod.embeddings[0];
        }
        await this.refreshAnalysisAsync();
        this.isLoading = false;
    }

    /**
     * Reloads the analysis and all its information.
     */
    private async refreshAnalysisAsync() {

        if (!this.selectedAnalysisMethod ||
            !this.selectedCategory ||
            !this.selectedClustering ||
            !this.selectedEmbedding
        ) {
            return;
        }

        this.isLoading = true;
        this.selectedAttributions = null;
        this.analysis = await this.analysesService.getAsync(
            this.project.id,
            this.selectedAnalysisMethod.name,
            this.selectedCategory.name,
            this.selectedClustering,
            this.selectedEmbedding
        );
        this.isLoading = false;
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
                this.refreshProjectAsync();
            }
        });
    }

    /**
     * Is invoked when the user hovers the mouse over an embedding.
     * @param eventInfo The event object that contains the information about the embedding that the user hovered over.
     */
    public async onHoverAsync(eventInfo: any): Promise<any> {

        const attributionIndex = eventInfo.points[0].data.attributionIndices[eventInfo.points[0].pointIndex];
        const attribution = await this.attributionsService.getAsync(this.project.id, attributionIndex);
        this.datasetSampleHoverPreview = await this.datasetService.getAsync(this.project.id, attribution.index);
    }

    /**
     * Is invoked when the user moves the mouse away from a sample.
     */
    public onUnhover(): void {
        this.datasetSampleHoverPreview = null;
    }

    /**
     * Is invoked when the user starts selecting. During the selection, the dataset sample preview is removed, so that
     * the user is able to properly see the data points.
     */
    public onSelecting(): void {
        this.datasetSampleHoverPreview = null;
    }

    /**
     * Is invoked when the user selects embeddings.
     * @param eventInfo The event object that contains the information about the embeddings that were selected.
     */
    public async onSelectedAsync(eventInfo?: any): Promise<any> {

        // When nothing was selected, then nothing needs to be loaded (this sometimes happens when deselecting)
        if (!eventInfo) {
            return;
        }

        // Gets the attributions of the data points that were selected
        this.isLoadingSelection = true;
        let attributionIndices: Array<number> = eventInfo.points.map(
            dataPoint => dataPoint.data.attributionIndices[dataPoint.pointIndex]
        );
        attributionIndices = attributionIndices.slice(0, 20);
        this.selectedAttributions = await Promise.all(attributionIndices.map(
            index => this.attributionsService.getAsync(this.project.id, index)
        ));

        // Gets the dataset samples for which the attributions were generated
        const selectedDatasetSamples: Array<Sample> = await Promise.all(this.selectedAttributions.map(
            attribution => this.datasetService.getAsync(this.project.id, attribution.index)
        ));

        // Assigns the dataset sample to their respective attribution
        for (const attribution of this.selectedAttributions) {
            attribution.sample = selectedDatasetSamples.filter(sample => sample.index === attribution.index)[0];
        }
        this.isLoadingSelection = false;
    }

    /**
     * Is invoked, when the user deselects everything.
     */
    public onDeselect(): void {
        this.selectedAttributions = null;
    }
}
