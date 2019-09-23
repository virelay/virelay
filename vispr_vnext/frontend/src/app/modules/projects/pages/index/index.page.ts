
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
import { ColorMapsService } from 'src/services/colorMaps/color-maps.service';
import { ColorMap } from 'src/services/colorMaps/color-map';
import * as d3 from 'd3';

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
     * @param analysesService The service which is used to manage analyses.
     * @param attributionsService The service which is used to manage attributions.
     * @param datasetService The service which is used to manage the datasets.
     * @param colorMapsService The service which is used to manage color maps.
     * @param route The currently activated route.
     */
    public constructor(
        private projectsService: ProjectsService,
        private analysesService: AnalysesService,
        private attributionsService: AttributionsService,
        private datasetService: DatasetService,
        private colorMapsService: ColorMapsService,
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
     * Contains a value that determines whether the user is currently hovering the mouse over a data point.
     */
    public isHovering: boolean;

    /**
     * Contains the dataset sample of the embedding that the user is currently hovering its mouse over.
     */
    public datasetSampleHoverPreview: Sample;

    /**
     * Gets a list of all the dimensions that are available in the currently selected embedding.
     */
    public get embeddingDimensions(): Array<number> {
        if (!this.analysis || this.analysis.embedding.length === 0) {
            return new Array();
        }
        return new Array(this.analysis.embedding[0].value.length).fill(0).map((_, index) => index);
    }

    /**
     * Contains the index of the dimension of the embedding that is to be displayed in the plot.
     */
    private _horizontalAxisDimensionIndex = 0;

    /**
     * Gets the index of the dimension of the embedding that is to be displayed in the plot.
     */
    public get horizontalAxisDimensionIndex(): number {
        return this._horizontalAxisDimensionIndex;
    }

    /**
     * Sets the index of the dimension of the embedding that is to be displayed in the plot.
     */
    public set horizontalAxisDimensionIndex(value: number) {
        this._horizontalAxisDimensionIndex = value;
        this.refreshPlot();
    }

    /**
     * Contains the index of the dimension of the embedding that is to be displayed in the plot.
     */
    private _verticalAxisDimensionIndex = 1;

    /**
     * Gets the index of the dimension of the embedding that is to be displayed in the plot.
     */
    public get verticalAxisDimensionIndex(): number {
        return this._verticalAxisDimensionIndex;
    }

    /**
     * Sets the index of the dimension of the embedding that is to be displayed in the plot.
     */
    public set verticalAxisDimensionIndex(value: number) {
        this._verticalAxisDimensionIndex = value;
        this.refreshPlot();
    }

    /**
     * Contains the color maps from which the user can choose one for rendering the heatmaps.
     */
    public colorMaps: Array<ColorMap>;

    /**
     * Contains the color map that was selected by the user for rendering the heatmaps.
     */
    public selectedColorMap: ColorMap;

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
        this._horizontalAxisDimensionIndex = 0;
        this._verticalAxisDimensionIndex = 1;
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
        this.refreshPlot();
    }

    /**
     * Contains the data of the PlotlyJS graph.
     */
    public embeddingGraphData: Array<Plotly.Data>;

    /**
     * Contains the layout of the PlotlyJS graph.
     */
    public embeddingGraphLayout: Partial<Plotly.Layout> = {
        autosize: true,
        dragmode: 'lasso',
        hovermode: 'closest',
        hoverdistance: 1,
        showlegend: false,
        margin: {
            l: 0,
            r: 0,
            t: 0,
            b: 0,
            pad: 0
        },
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

    /**
     * Contains the data for the plot of the eigen values.
     */
    public eigenValuesGraphData: Array<Plotly.Data>;

    /**
     * Contains the layout of the plot of the eigen values.
     */
    public eigenValuesGraphLayout: Partial<Plotly.Layout> = {
        title: 'Eigen Values',
        margin: {
            l: 32,
            r: 16,
            t: 32,
            b: 48,
            pad: 0
        },
        xaxis: {
            autotick: false,
            ticks: 'outside',
            tick0: 0,
            dtick: 5
        },
        paper_bgcolor: '#00000000',
        plot_bgcolor: '#00000000'
    };

    /**
     * Contains the data points that were selected by the user.
     */
    public selectedDataPoints: Array<{
        attribution: Attribution,
        sample: Sample,
        color: string,
        clusterIndex: number
    }>;

    /**
     * Generates a unique color for the specified cluster (ploty.js, unfortunately only uses 10 different colors by
     * default, but there are options for more clusters in VISPR).
     * @param index The index of the cluster for which the color is to be generated.
     * @param total The total number of clusters.
     */
    private generateClusterColor(index: number, total: number): string {
        return d3.hsl(360 / total * index, 0.8, 0.5).toString();
    }

    /**
     * Refreshes the plot.
     */
    private refreshPlot(): void {

        if (!this.analysis) {
            return;
        }

        const clusters = new Array<number>();
        for (const cluster of this.analysis.embedding.map(embedding => embedding.cluster)) {
            if (clusters.indexOf(cluster) === -1) {
                clusters.push(cluster);
            }
        }

        this.embeddingGraphData = new Array<Plotly.Data>();
        for (const cluster of clusters) {
            const embeddingsInCluster = this.analysis.embedding.filter(embedding => embedding.cluster === cluster);
            this.embeddingGraphData.push({
                name: `Cluster ${cluster}`,
                x: embeddingsInCluster.map(embedding => embedding.value[this.horizontalAxisDimensionIndex]),
                y: embeddingsInCluster.map(embedding => embedding.value[this.verticalAxisDimensionIndex]),
                type: 'scatter',
                mode: 'markers',
                marker: {
                    size: 12,
                    color: this.generateClusterColor(cluster, clusters.length)
                },
                hoverinfo: 'none',
                attributionIndices: embeddingsInCluster.map(embedding => embedding.attributionIndex),
                clusterIndex: cluster
            });
        }

        this.eigenValuesGraphData = new Array<Plotly.Data>();
        this.eigenValuesGraphData.push({
            name: 'Eigen Values',
            x: this.analysis.eigenValues.map((_, index) => index).reverse(),
            y: this.analysis.eigenValues,
            type: 'bar',
            width: 0.25,
            hoverinfo: 'x',
            color: 'y'
        });
    }

    /**
     * Reloads the project and all its information.
     */
    private async refreshProjectAsync(): Promise<void> {
        this.isLoading = true;
        this.project = await this.projectsService.getByIdAsync(this.id);

        this.selectedDataPoints = null;
        this._selectedAnalysisMethod = this.project.analysisMethods[0];
        this._selectedCategory = this.selectedAnalysisMethod.categories[0];
        this._selectedClustering = this.selectedAnalysisMethod.clusterings[0];
        if (this.selectedAnalysisMethod.embeddings.filter(embedding => embedding === 'tsne').length > 0) {
            this._selectedEmbedding = 'tsne';
        } else {
            this._selectedEmbedding = this.selectedAnalysisMethod.embeddings[0];
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
        this.selectedDataPoints = null;
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
    public async ngOnInit(): Promise<void> {

        // Subscribes for changes of the route, when the route has changed, then the project ID is retrieved from the
        // URL and the project is loaded
        this.route.paramMap.subscribe(paramMap => {
            if (paramMap.has('id') && paramMap.get('id')) {
                this.id = parseInt(paramMap.get('id'), 10);
                this.refreshProjectAsync();
            }
        });

        // Loads the color maps from the RESTful API
        this.colorMaps = await this.colorMapsService.getAsync();
        const defaultColorMaps = this.colorMaps.filter(colorMap => colorMap.name === 'black-fire-red');
        if (defaultColorMaps.length > 0) {
            this.selectedColorMap = defaultColorMaps[0];
        } else {
            this.selectedColorMap = this.colorMaps[0];
        }
    }

    /**
     * Is invoked when the user hovers the mouse over an embedding.
     * @param eventInfo The event object that contains the information about the embedding that the user hovered over.
     */
    public async onHoverAsync(eventInfo: any): Promise<void> {

        this.isHovering = true;
        const attributionIndex = eventInfo.points[0].data.attributionIndices[eventInfo.points[0].pointIndex];
        const attribution = await this.attributionsService.getAsync(this.project.id, attributionIndex);
        this.datasetSampleHoverPreview = await this.datasetService.getAsync(this.project.id, attribution.index);
    }

    /**
     * Is invoked when the user moves the mouse away from a sample.
     */
    public onUnhover(): void {
        this.isHovering = false;
        this.datasetSampleHoverPreview = null;
    }

    /**
     * Is invoked when the user selects embeddings.
     * @param eventInfo The event object that contains the information about the embeddings that were selected.
     */
    public async onSelectedAsync(eventInfo?: any): Promise<void> {

        // When nothing was selected, then nothing needs to be loaded (this sometimes happens when deselecting)
        if (!eventInfo) {
            return;
        }

        // Gets the attributions of the data points that were selected
        this.isLoadingSelection = true;
        console.log(eventInfo.points.map(p => p.data.marker.color));
        let attributionIndices: Array<number> = eventInfo.points.map(
            dataPoint => dataPoint.data.attributionIndices[dataPoint.pointIndex]
        );
        attributionIndices = attributionIndices.slice(0, 20);
        const attributions = await Promise.all(attributionIndices.map(
            index => this.attributionsService.getAsync(this.project.id, index)
        ));

        // Gets the dataset samples for which the attributions were generated
        const datasetSamples: Array<Sample> = await Promise.all(attributions.map(
            attribution => this.datasetService.getAsync(this.project.id, attribution.index)
        ));

        // Assigns the dataset sample to their respective attribution
        this.selectedDataPoints = [];
        for (let index = 0; index < attributions.length; index++) {
            this.selectedDataPoints.push({
                attribution: attributions[index],
                sample: datasetSamples.filter(sample => sample.index === attributions[index].index)[0],
                color: eventInfo.points[index].data.marker.color,
                clusterIndex: eventInfo.points[index].data.clusterIndex
            });
        }
        this.isLoadingSelection = false;
    }

    /**
     * Is invoked, when the user deselects everything.
     */
    public onDeselect(): void {
        this.selectedDataPoints = null;
    }
}
