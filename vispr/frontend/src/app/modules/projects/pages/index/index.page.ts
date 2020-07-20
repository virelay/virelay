
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
import { HoverEvent, DataPoint } from 'src/app/components/embedding-visualizer/embedding-visualizer.component';
import { Embedding } from 'src/services/analyses/embedding';
import { saveAs } from 'file-saver';
import * as THREE from 'three';

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
    public isLoadingAttributions: boolean;

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
    public firstDimension = 0;

    /**
     * Contains the index of the dimension of the embedding that is to be displayed in the plot.
     */
    public secondDimension = 1;

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
            this.selectedDataPoints = null;
            this.selectedCategory = this.selectedAnalysisMethod.categories[0];
            const initialClustering = this.selectedAnalysisMethod.clusterings.filter(clustering => parseInt(clustering, 10) === 10);
            if (initialClustering.length > 0) {
                this.selectedClustering = initialClustering[0];
            } else {
                this.selectedClustering = this.selectedAnalysisMethod.clusterings[0];
            }
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

        // Sets the new value
        this._selectedEmbedding = value;

        // Resets the dimensions that are to be displayed
        this.firstDimension = 0;
        this.secondDimension = 1;

        // Refreshes the analysis
        if (value) {
            this.refreshAnalysisAsync();
        }
    }

    /**
     * Contains the number of clusters in the embedding in the analysis.
     */
    private numberOfClusters: number;

    /**
     * Gets a list of all the clusters with their respective colors.
     */
    public availableClusters: Array<{ index: number; color: string; }>;

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

        // Stores the new value
        this._analysis = value;

        // Determines the total number of clusters, which is needed to determine the number of colors that are needed
        // for the visualization
        if (this.analysis.embedding) {
            const clusters = new Array<number>();
            for (const cluster of this.analysis.embedding.map(dataPoint => dataPoint.cluster)) {
                if (clusters.indexOf(cluster) === -1) {
                    clusters.push(cluster);
                }
            }
            clusters.sort();
            this.numberOfClusters = clusters.length;
            this.availableClusters = clusters.map(cluster => {
                return {
                    index: cluster,
                    color: new THREE.Color().setHSL((360 / this.numberOfClusters * cluster) / 360, 0.5, 0.5).getStyle()
                };
            });
        }

        // Refreshes the plot that displays the eigen values
        this.refreshEigenValuePlot();
    }

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
            dtick: 5,
            fixedrange: true
        },
        yaxis: {
            fixedrange: true
        },
        paper_bgcolor: '#00000000',
        plot_bgcolor: '#00000000'
    };

    /**
     * Contains the data points that were selected by the user.
     */
    private _selectedDataPoints: Array<DataPoint>;

    /**
     * Gets the data points that were selected by the user.
     */
    public get selectedDataPoints(): Array<DataPoint> {
        return this._selectedDataPoints;
    }

    /**
     * Sets the data points that were selected by the user.
     */
    public set selectedDataPoints(value: Array<DataPoint>) {
        this._selectedDataPoints = value;
        this.refreshAttributionsOfSelecteddataPointsAsync();
    }

    /**
     * Contains the attributions for the data points selected by the user.
     */
    public selectedAttributions: Array<{
        attribution: Attribution,
        color: string,
        clusterIndex: number
    }>;

    /**
     * Refreshes the eigen value plot.
     */
    private refreshEigenValuePlot(): void {

        if (!this.analysis) {
            return;
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
        const initialClustering = this.selectedAnalysisMethod.clusterings.filter(clustering => parseInt(clustering, 10) === 10);
        if (initialClustering.length > 0) {
            this.selectedClustering = initialClustering[0];
        } else {
            this.selectedClustering = this.selectedAnalysisMethod.clusterings[0];
        }
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
     * Is invoked when the user selects data points. Updates the attributions that are displayed
     */
    private async refreshAttributionsOfSelecteddataPointsAsync(): Promise<void> {

        // Checks if any data points were selected, if not, then the attributions can be removed
        if (!this.selectedDataPoints || this.selectedDataPoints.length === 0) {
            this.selectedAttributions = null;
            return;
        }

        // Gets the attributions of the data points that were selected
        this.isLoadingAttributions = true;
        const dataPoints = this.selectedDataPoints as Array<Embedding>;
        const attributionIndices = dataPoints.map(dataPoint => dataPoint.attributionIndex).slice(0, 20);

        const attributions = await Promise.all(attributionIndices.map(
            index => this.attributionsService.getAsync(this.project.id, index, this.imageMode)
        ));

        // Assigns the dataset sample to their respective attribution
        this.selectedAttributions = [];
        for (let index = 0; index < attributions.length; index++) {
            this.selectedAttributions.push({
                attribution: attributions[index],
                color: this.availableClusters.filter(cluster => cluster.index === dataPoints[index].cluster)[0].color,
                clusterIndex: dataPoints[index].cluster
            });
        }
        this.isLoadingAttributions = false;
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
     * @param event The event object that contains the information about the embedding that the user hovered over.
     */
    public async onHoverAsync(event: HoverEvent): Promise<void> {

        this.isHovering = true;
        const embedding = event.dataPoint as Embedding;
        const attribution = await this.attributionsService.getAsync(this.project.id, embedding.attributionIndex, 'attribution');
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
     * Selects the data points of the cluster with the specified index.
     * @param index The index of the cluster that is to be selected.
     */
    public selectCluster(index: number) {
        const dataPointsOfCluster = this.analysis.embedding.filter(dataPoint => dataPoint.cluster === index);
        this.selectedDataPoints = dataPointsOfCluster;
    }

    /**
      * Is invoked when user clicks the Export button. Exports selected data points as JSON file.
      */
    public onExportClick(): void {
        const selectedDataPoints = this.selectedDataPoints as Array<Embedding>;
        const selectedPointsIndices = selectedDataPoints.map(
            dataPoint => dataPoint.attributionIndex
        );
        const selectedPointsClusters = selectedDataPoints.map(
            dataPoint => dataPoint.cluster
        );

        const allDataPoints = this.analysis.embedding as Array<Embedding>;
        const allPointsIndices = allDataPoints.map(
            dataPoint => dataPoint.attributionIndex
        );
        const allPointsClusters = allDataPoints.map(
            dataPoint => dataPoint.cluster
        );

        const data = {
            projectID: this.project.id,
            projectName: this.project.name,
            modelName: this.project.model,
            datasetName: this.project.dataset,
            selectedAnalysisName: this.selectedAnalysisMethod.name,
            selectedCategory: this.selectedCategory.name,
            selectedCategoryHumanReadable: this.selectedCategory.humanReadableName,
            selectedEmbeddingName: this.selectedEmbedding,
            selectedClustering: this.selectedClustering,
            numberOfClusters: this.numberOfClusters,
            selectedColorMap: this.selectedColorMap.name,
            selectedImageMode: this.imageMode,
            selectedDataPointIndices: selectedPointsIndices,
            selectedDataPointClusters: selectedPointsClusters,
            allDataPointIndices: allPointsIndices,
            allDataPointClusters: allPointsClusters
        }
        const fileName = `${this.project.name} - `
        + `${this.selectedCategory.humanReadableName} (${this.selectedCategory.name}) - `
        + `${this.selectedAnalysisMethod.name} - ${this.selectedClustering}.json`;
        const jsonExport = new Blob(
            [JSON.stringify(data, undefined, 2)],
            {type: 'application/json'}
        );
        saveAs(jsonExport, fileName);
    }


    private async readFileContent(file: File): Promise<string | ArrayBuffer> {
        return new Promise<string | ArrayBuffer>((resolve, reject) => {
            const reader: FileReader = new FileReader();

            reader.onloadend = (e) => {
                resolve(reader.result);
            };
            reader.onerror = (e) => {
                reject(e);
            };

            reader.readAsText(file);
        });
    }


    public async onImportChange(files: File[]) {
        const rawContent = await this.readFileContent(files[0]);
        const data = JSON.parse(<string>rawContent);

        this.isLoading = true;
        this.project = await this.projectsService.getByIdAsync(data.projectID);

        const analysisMethods = this.project.analysisMethods.filter(analysis => analysis.name === data.selectedAnalysisName);
        if (analysisMethods.length) {
            this._selectedAnalysisMethod = analysisMethods[0];
        }
        const categories = this.selectedAnalysisMethod.categories.filter(category => category.name === data.selectedCategory);
        if (categories.length) {
            this._selectedCategory = categories[0];
        }

        if (this.selectedAnalysisMethod.clusterings.filter(clustering => clustering === data.selectedClustering).length) {
            this._selectedClustering = data.selectedClustering;
        }

        if (this.selectedAnalysisMethod.embeddings.filter(embedding => embedding === data.selectedEmbeddingName).length) {
            this._selectedEmbedding = data.selectedEmbeddingName;
        }

        const colorMap = this.colorMaps.filter(cmap => cmap.name === data.selectedColorMap);
        if (colorMap.length) {
            this.selectedColorMap = colorMap[0];
        }

        this.imageMode = data.selectedImageMode;

        await this.refreshAnalysisAsync();

        const allDataPoints = this.analysis.embedding as Array<Embedding>;
        this.selectedDataPoints = allDataPoints.filter(point => point.attributionIndex in data.selectedDataPointIndices);
        await this.refreshAttributionsOfSelecteddataPointsAsync();

        this.isLoading = false;
    }


    /**
     * The image visualization mode
     */
    private _imageMode = "input";

    /**
     * Gets the image visualization mode
     */
    public get imageMode(): string {
        return this._imageMode;
    }

    /**
     * Sets the image visualization mode
     */
    public set imageMode(value: string) {
        this._imageMode = value;
        this.refreshAttributionsOfSelecteddataPointsAsync();
    }
}
