
import { Subscription, fromEvent } from 'rxjs';
import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { ClarityModule, ClrModalModule } from '@clr/angular';
import * as PlotlyJS from 'plotly.js-basic-dist-min';
import { PlotlyModule } from 'angular-plotly.js';
import * as THREE from 'three'
import saveAs from 'file-saver';

import { Cluster } from '@pages/projects/cluster';
import { EmbeddingVectorAttribution } from '@pages/projects/embedding-vector-attribution';
import { EmbeddingVisualizerComponent } from '@components/embedding-visualizer/embedding-visualizer.component';
import { ErrorMessageComponent } from '@components/error-message/error-message.component';
import { ProjectsService } from '@services/projects/projects.service';
import { AnalysesService } from '@services/analyses/analyses.service';
import { AttributionsService } from '@services/attributions/attributions.service';
import { DatasetsService } from '@services/datasets/datasets.service';
import { ColorMapsService } from '@services/color-maps/color-maps.service';
import { Project } from '@services/projects/project';
import { ColorMap } from '@services/color-maps/color-map';
import { ResourceState } from '@services/resource-state';
import { EmbeddingVector } from '@services/analyses/embedding-vector';
import { Sample } from '@services/datasets/sample';
import { AttributionImageMode } from '@services/attributions/attribution-image-mode';
import { Analysis } from '@services/analyses/analysis';
import { AnalysisMethod } from '@services/projects/analysis-method';
import { AnalysisCategory } from '@services/projects/analysis-category';
import { Attribution } from '@services/attributions/attribution';
import { HoverEvent } from '@components/embedding-visualizer/hover-event';
import type { HTMLInputEvent } from '@pages/projects/html-input-event';

// Tells Angular PlotlyJS to use the PlotlyJS library
PlotlyModule.plotlyjs = PlotlyJS;

/**
 * Represents the project page component, which is the main page of the application that hosts the currently selected project from the projects that
 * are available in the workspace.
 */
@Component({
    selector: 'virelay-project-page',
    standalone: true,
    templateUrl: 'project-page.component.html',
    styleUrl: 'project-page.component.scss',
    imports: [
        CommonModule,
        FormsModule,
        RouterModule,
        ClarityModule,
        ClrModalModule,
        PlotlyModule,
        EmbeddingVisualizerComponent,
        ErrorMessageComponent
    ]
})
export class ProjectPageComponent implements OnInit, OnDestroy {

    // #region Private Fields

    /**
     * Contains the projects service, which is used to load the project that is being viewed on the page.
     */
    private readonly projectsService: ProjectsService = inject(ProjectsService);

    /**
     * Contains the datasets service, which is used to load the datasets of the project.
     */
    private readonly datasetsService: DatasetsService = inject(DatasetsService);

    /**
     * Contains the attributions service, which is used to load the attributions of the samples of the datasets.
     */
    private readonly attributionsService: AttributionsService = inject(AttributionsService);

    /**
     * Contains the color maps service, which is used to load the color maps that can be used to render heatmaps from the attributions.
     */
    private readonly colorMapsService: ColorMapsService = inject(ColorMapsService);

    /**
     * Contains the analyses service, which is used to load the analyses that were performed on the attributions.
     */
    private readonly analysesService: AnalysesService = inject(AnalysesService);

    /**
     * Contains the current route that is being viewed by the user. This is used to retrieve the ID of the project that is being viewed.
     */
    private readonly route: ActivatedRoute = inject(ActivatedRoute);

    /**
     * Contains the number of clusters in the embedding of the analysis.
     */
    private accessor numberOfClusters: number = 0;

    /**
     * Contains the subscription to the change event of the "prefers-color-scheme" media query, which is used to detect changes in the user's
     * preference for the color scheme (light or dark mode). The subscription is stored, so that it can be unsubscribed from when the component is
     * destroyed.
     */
    private colorSchemePreferenceChangeSubscription: Subscription | null = null;

    /**
     * Contains the subscription to the route parameters observable, which is used to detect when the ID of the project that is being viewed changes
     * in the URL. The subscription is stored, so that it can be unsubscribed from when the component is destroyed.
     */
    private routeParametersChangeSubscription: Subscription | null = null;

    // #endregion

    // #region Public Properties

    /**
     * Contains the type of the enumeration that is used to represent the state of the loading of the project, dataset samples, attributions, color
     * maps, or analyses. This is required, so that the enumeration type can be referenced in the HTML template of the project page.
     */
    public readonly ResourceState: typeof ResourceState = ResourceState;

    /**
     * Gets or sets the ID of the project.
     */
    public accessor projectId: number | null = null;

    /**
     * Gets or sets the current state of the loading of the project.
     */
    public accessor projectLoadingState: ResourceState = ResourceState.Loading;

    /**
     * Gets or sets the error message that is displayed when the project could not be loaded.
     */
    public accessor projectLoadingErrorMessage: string | null = null;

    /**
     * Gets or sets the project that is being displayed.
     */
    public accessor project: Project | null = null;

    /**
     * Contains the analysis method that was selected by the user.
     */
    private _selectedAnalysisMethod: AnalysisMethod | null = null;

    /**
     * Gets the analysis method that was selected by the user.
     *
     * @returns {AnalysisMethod | null} Returns the analysis method that was selected by the user.
     */
    public get selectedAnalysisMethod(): AnalysisMethod | null {
        return this._selectedAnalysisMethod;
    }

    /**
     * Sets the analysis method that was selected by the user.
     *
     * @param {AnalysisMethod} selectedAnalysisMethod The analysis method that was selected by the user that is to be set.
     */
    public set selectedAnalysisMethod(selectedAnalysisMethod: AnalysisMethod | null) {
        this._selectedAnalysisMethod = selectedAnalysisMethod;

        if (!selectedAnalysisMethod) {
            return;
        }

        this.selectedEmbeddingVectors = [];
        this.selectedAnalysisCategory = selectedAnalysisMethod.categories[0];
        const initialClustering = selectedAnalysisMethod.clusterings.filter(clustering => parseInt(clustering, 10) === 10);
        if (initialClustering.length > 0) {
            this.selectedClustering = initialClustering[0];
        } else {
            this.selectedClustering = selectedAnalysisMethod.clusterings[0];
        }
        if (selectedAnalysisMethod.embeddings.filter(embedding => embedding === 'tsne').length > 0) {
            this.selectedEmbedding = 'tsne';
        } else {
            this.selectedEmbedding = selectedAnalysisMethod.embeddings[0];
        }
        void this.refreshAnalysisAsync();
    }

    /**
     * Contains the selected analysis category.
     */
    private _selectedAnalysisCategory: AnalysisCategory | null = null;

    /**
     * Gets the selected analysis category.
     *
     * @returns {AnalysisCategory | null} Returns the selected analysis category.
     */
    public get selectedAnalysisCategory(): AnalysisCategory | null {
        return this._selectedAnalysisCategory;
    }

    /**
     * Sets the selected analysis category.
     *
     * @param {AnalysisCategory} selectedAnalysisCategory The selected analysis category that is to be set.
     */
    public set selectedAnalysisCategory(selectedAnalysisCategory: AnalysisCategory | null) {
        this._selectedAnalysisCategory = selectedAnalysisCategory;
        if (selectedAnalysisCategory) {
            void this.refreshAnalysisAsync();
        }
    }

    /**
     * Gets or sets the current state of the loading of the analysis.
     */
    public accessor analysisLoadingState: ResourceState = ResourceState.Pending;

    /**
     * Gets or sets the error message that is displayed when the analysis could not be loaded.
     */
    public accessor analysisLoadingErrorMessage: string | null = null;

    /**
     * Contains the current analysis.
     */
    private _analysis: Analysis | null = null;

    /**
     * Gets the current analysis.
     *
     * @returns {Analysis | null} Returns the analysis that is currently displayed.
     */
    public get analysis(): Analysis | null {
        return this._analysis;
    }

    /**
     * Sets the current analysis.
     *
     * @param {Analysis | null} analysis The analysis that is to be displayed.
     */
    public set analysis(analysis: Analysis | null) {

        // Stores the new value
        this._analysis = analysis;

        // Determines the total number of clusters, which is needed to determine the number of colors that are needed for the visualization
        if (analysis !== null) {
            const clusters = new Map<number, number>();
            for (const cluster of analysis.embedding.map(embeddingVector => embeddingVector.cluster)) {
                let numberOfEmbeddingVectorsInCluster = clusters.get(cluster);
                if (!numberOfEmbeddingVectorsInCluster) {
                    numberOfEmbeddingVectorsInCluster = 0;
                }
                clusters.set(cluster, numberOfEmbeddingVectorsInCluster + 1);
            }
            this.numberOfClusters = clusters.size;
            this.availableClusters = [...clusters.keys()].sort((a, b) => a - b).map(cluster => {
                return {
                    index: cluster,
                    size: clusters.get(cluster) ?? 0,
                    color: new THREE.Color().setHSL((360 / this.numberOfClusters * cluster) / 360, 0.5, 0.5).getStyle()
                };
            });
        } else {
            this.numberOfClusters = 0;
            this.availableClusters = [];
        }

        // Refreshes the plot that displays the eigenvalues
        this.refreshEigenvaluePlot();
    }

    /**
     * Gets or sets a list of all the clusters with their respective colors.
     */
    public accessor availableClusters: Cluster[] | null = null;

    /**
     * Contains the name of the selected clustering.
     */
    private _selectedClustering: string | null = null;

    /**
     * Gets the name of the selected clustering.
     *
     * @returns {string | null} Returns the name of the selected clustering.
     */
    public get selectedClustering(): string | null {
        return this._selectedClustering;
    }

    /**
     * Sets the name of the selected clustering.
     *
     * @param {string | null} selectedClustering The name of the selected clustering that is to be set.
     */
    public set selectedClustering(selectedClustering: string | null) {
        this._selectedClustering = selectedClustering;
        if (selectedClustering !== null) {
            void this.refreshAnalysisAsync();
        }
    }

    /**
     * Gets a list of all the dimensions that are available in the currently selected analysis. These are used to populate the selection boxes were
     * the user can choose the two dimensions that are to be displayed in the embedding visualizer.
     *
     * @returns {Array<number>} Returns an array that contains the indices of the dimensions that are available in the currently selected analysis.
     */
    public get embeddingDimensions(): number[] {
        if (!this.analysis || this.analysis.embedding.length === 0) {
            return [];
        }
        return new Array(this.analysis.embedding[0].value.length).fill(0).map((_, index) => index);
    }

    /**
     * Gets or sets the index of the dimension of the embedding that is to be displayed in the embedding visualizer.
     */
    public accessor firstEmbeddingDimensionIndex: number = 0;

    /**
     * Gets or sets the index of the dimension of the embedding that is to be displayed in the embedding visualizer.
     */
    public accessor secondEmbeddingDimensionIndex: number = 1;

    /**
     * Contains the name of the selected embedding.
     */
    private _selectedEmbedding: string | null = null;

    /**
     * Gets the name of the selected embedding.
     *
     * @returns {string | null} Returns the name of the selected embedding.
     */
    public get selectedEmbedding(): string | null {
        return this._selectedEmbedding;
    }

    /**
     * Sets the name of the selected embedding.
     *
     * @param {string | null} selectedEmbedding The name of the selected embedding that is to be set.
     */
    public set selectedEmbedding(selectedEmbedding: string | null) {

        // Sets the new value
        this._selectedEmbedding = selectedEmbedding;

        // Resets the dimensions that are to be displayed
        this.firstEmbeddingDimensionIndex = 0;
        this.secondEmbeddingDimensionIndex = 1;

        // Refreshes the analysis
        if (selectedEmbedding) {
            void this.refreshAnalysisAsync();
        }
    }

    /**
     * Contains the embedding vectors that were selected by the user in the embedding visualizer.
     */
    private _selectedEmbeddingVectors: EmbeddingVector[] = [];

    /**
     * Gets the embedding vectors that were selected by the user.
     *
     * @returns {EmbeddingVector[]} Returns an array that contains the embedding vectors that were selected by the user.
     */
    public get selectedEmbeddingVectors(): EmbeddingVector[] {
        return this._selectedEmbeddingVectors;
    }

    /**
     * Sets the embedding vectors that were selected by the user.
     *
     * @param {EmbeddingVector[]} selectedEmbeddingVectors The embedding vectors that were selected by the user.
     */
    public set selectedEmbeddingVectors(selectedEmbeddingVectors: EmbeddingVector[]) {
        this._selectedEmbeddingVectors = selectedEmbeddingVectors;
        void this.refreshAttributionsOfSelectedEmbeddingVectorsAsync();
    }

    /**
     * Gets or sets a value that determines whether the user is currently hovering the mouse over an embedding vector.
     */
    public accessor isHoveringOverEmbeddingVector: boolean = false;

    /**
     * Gets or sets the current state of the loading of the dataset sample preview for the embedding vector the user is currently hovering.
     */
    public accessor hoveredEmbeddingVectorDatasetSamplePreviewLoadingState: ResourceState = ResourceState.Pending;

    /**
     * Gets or sets the error message that is displayed when the dataset sample preview for the embedding vector the user is currently hovering could
     * not be loaded.
     */
    public accessor hoveredEmbeddingVectorDatasetSamplePreviewLoadingErrorMessage: string | null = null;

    /**
     * Gets or sets the corresponding dataset sample of the embedding vector that the user is currently hovering their mouse over.
     */
    public accessor hoveredEmbeddingVectorDatasetSamplePreview: Sample | null = null;

    /**
     * Gets or sets the data for the plot of the eigenvalues.
     */
    public accessor eigenvaluesGraphData: Plotly.Data[] | null = null;

    /**
     * Gets or sets the layout of the plot of the eigenvalues.
     */
    public accessor eigenvaluesGraphLayout: Partial<Plotly.Layout> = {
        width: 200,
        height: 200,
        margin: {
            l: 18,
            r: 0,
            t: 0,
            b: 22,
            pad: 0
        },
        xaxis: {
            autotick: false,
            ticks: 'outside',
            tick0: 0,
            dtick: 5,
            fixedrange: true,
            showgrid: false,
            linecolor: this.getThemeColor('--virelay-cluster-pane-eigenvalue-plot-axis-line-color'),
            tickcolor: this.getThemeColor('--virelay-cluster-pane-eigenvalue-plot-axis-tick-color'),
        },
        yaxis: {
            fixedrange: true,
            showline: false,
            showgrid: false
        },
        paper_bgcolor: '#00000000',
        plot_bgcolor: '#00000000',
        font: {
            color: this.getThemeColor('--virelay-cluster-pane-eigenvalue-plot-font-color')
        },
        hovermode: false
    };

    /**
     * Gets or sets the current state of the loading of the color maps.
     */
    public accessor colorMapsLoadingState: ResourceState = ResourceState.Pending;

    /**
     * Gets or sets the error message that is displayed when the color maps could not be loaded.
     */
    public accessor colorMapsLoadingErrorMessage: string | null = null;

    /**
     * Gets or sets the color maps from which the user can choose one for rendering the heatmaps.
     */
    public accessor colorMaps: ColorMap[] | null = null;

    /**
     * Gets or sets the color map that was selected by the user for rendering the heatmaps.
     */
    public accessor selectedColorMap: ColorMap | null = null;

    /**
     * Contains a value that determine how the selected attributions are displayed. The value "input" displays the input image of the corresponding
     * dataset sample, "overlay" overlays a gray-version of the input sample image with the heatmap of the attribution in the currently selected color
     * map, and "attribution" displays the heatmap of the attribution in the currently selected color map.
     */
    private _attributionImageMode: AttributionImageMode = AttributionImageMode.Input;

    /**
     * Gets a value that determine how the selected attributions are displayed. The value "input" displays the input image of the corresponding
     * dataset sample, "overlay" overlays a gray-version of the input sample image with the heatmap of the attribution in the currently selected color
     * map, and "attribution" displays the heatmap of the attribution in the currently selected color map.
     *
     * @returns {AttributionImageMode} Returns the value that determine how the selected attributions are displayed.
     */
    public get attributionImageMode(): AttributionImageMode {
        return this._attributionImageMode;
    }

    /**
     * Sets a value that determine how the selected attributions are displayed. The value "input" displays the input image of the corresponding
     * dataset sample, "overlay" overlays a gray-version of the input sample image with the heatmap of the attribution in the currently selected color
     * map, and "attribution" displays the heatmap of the attribution in the currently selected color map.
     *
     * @param {AttributionImageMode} attributionImageMode The value that determine how the selected attributions are displayed.
     */
    public set attributionImageMode(attributionImageMode: AttributionImageMode) {
        this._attributionImageMode = attributionImageMode;
        void this.refreshAttributionsOfSelectedEmbeddingVectorsAsync();
    }

    /**
     * Gets or sets the current state of the loading of the attributions.
     */
    public accessor selectedEmbeddingVectorAttributionsLoadingState: ResourceState = ResourceState.Pending;

    /**
     * Gets or sets the error message that is displayed when the attributions could not be loaded.
     */
    public accessor selectedEmbeddingVectorAttributionsLoadingErrorMessage: string | null = null;

    /**
     * Gets or sets the attributions for the embedding vectors selected by the user.
     */
    public accessor selectedEmbeddingVectorAttributions: EmbeddingVectorAttribution[] = [];

    /**
     * Gets or sets the current state of the exporting of the current application state.
     */
    public accessor exportSavingState: ResourceState = ResourceState.Pending;

    /**
     * Gets or sets the error message that is displayed when the exporting of the current application state failed.
     */
    public accessor exportSavingErrorMessage: string | null = null;

    /**
     * Gets or sets the current state of the importing of a saved application state.
     */
    public accessor importLoadingState: ResourceState = ResourceState.Pending;

    /**
     * Gets or sets the error message that is displayed when the importing of the saved application state failed.
     */
    public accessor importLoadingErrorMessage: string | null = null;

    /**
     * Gets or sets the generated shareable link, which can be used to reproduce the exact state of the ViRelAy in another browser.
     */
    public accessor shareableLinkUrl: string | null = null;

    /**
     * Gets or sets a value that determines whether the shareable link was created.
     */
    public accessor shareableLinkUrlCreationState: ResourceState = ResourceState.Pending;

    /**
     * Gets or sets the error message that is displayed when the shareable link could not be created
     */
    public accessor shareableLinkUrlCreationErrorMessage: string | null = null;

    /**
     * Gets or sets a value that determines whether the share dialog, where the user can copy the created shareable link URL, is open.
     */
    public accessor isShareDialogOpen: boolean = false;

    /**
     * Gets or sets a value that determines whether the shareable link was copied into the clipboard.
     */
    public accessor shareableLinkUrlCopyingState: ResourceState = ResourceState.Pending;

    /**
     * Gets or sets the error message that is displayed when the shareable link could not be copied into the clipboard.
     */
    public accessor shareableLinkUrlCopyingErrorMessage: string | null = null;

    // #endregion

    // #region Private Methods

    /**
     * Reloads the project and all its information.
     *
     * @returns {Promise<void>} Returns a promise that resolves when the project has been reloaded.
     */
    private async refreshProjectAsync(): Promise<void> {

        // If no project ID could be parsed from the URL, then the project cannot be loaded
        if (this.projectId === null) {
            return;
        }

        // Loads the project with the ID that was specified in the URL path
        this.projectLoadingState = ResourceState.Loading;
        try {
            this.project = await this.projectsService.getByIdAsync(this.projectId);
        } catch (exception: unknown) {
            if (exception instanceof Error) {
                this.projectLoadingErrorMessage = exception.message.endsWith('.') ? exception.message : `${exception.message}.`;
            } else {
                this.projectLoadingErrorMessage = 'An unknown error occurred while loading the projects.';
            }
            this.projectLoadingState = ResourceState.Failed;
            return;
        }

        // Resets the embedding vectors that are selected in the embedding visualization
        this.selectedEmbeddingVectors = [];

        // Parses the query parameters, which may contain state information that has to be restored
        const queryParameters = new URLSearchParams(window.location.search);

        // Resets/restores the selected analysis method
        let selectedAnalysisMethod: AnalysisMethod | undefined;
        if (this.project.analysisMethods.length > 0) {
            if (queryParameters.has('analysisMethod')) {
                selectedAnalysisMethod = this.project.analysisMethods
                    .find(analysisMethod => analysisMethod.name === queryParameters.get('analysisMethod'));
            } else {
                selectedAnalysisMethod = this.project.analysisMethods[0];
            }
        }
        if (!selectedAnalysisMethod) {
            this.projectLoadingErrorMessage =
                `The selected analysis method ${queryParameters.get('analysisMethod')} could not be found in the project.`;
            this.projectLoadingState = ResourceState.Failed;
            return;
        }
        this._selectedAnalysisMethod = selectedAnalysisMethod;

        // Resets/restores the selected category
        const selectedAnalysisCategory = this._selectedAnalysisMethod.categories
            .find(category => category.name === queryParameters.get('analysisCategory'));
        if (selectedAnalysisCategory) {
            this._selectedAnalysisCategory = selectedAnalysisCategory;
        } else {
            this._selectedAnalysisCategory = this._selectedAnalysisMethod.categories[0];
        }

        // Resets/restores the clustering
        if (queryParameters.has('clustering')) {
            this._selectedClustering = queryParameters.get('clustering');
        } else {
            const initialClustering = this._selectedAnalysisMethod.clusterings.filter(clustering => parseInt(clustering, 10) === 10);
            if (initialClustering.length > 0) {
                this._selectedClustering = initialClustering[0];
            } else {
                this._selectedClustering = this._selectedAnalysisMethod.clusterings[0];
            }
        }

        // Resets/restores the selected embedding (if no embedding is available in the query parameters, then t-SNE is selected by default if
        // available, otherwise the first one is selected)
        if (queryParameters.has('embedding')) {
            this._selectedEmbedding = queryParameters.get('embedding');
        } else if (this._selectedAnalysisMethod.embeddings.filter(embedding => embedding === 'tsne').length > 0) {
            this._selectedEmbedding = 'tsne';
        } else {
            this._selectedEmbedding = this._selectedAnalysisMethod.embeddings[0];
        }

        // Restores the image mode
        const attributionImageMode = queryParameters.get('imageMode');
        if (attributionImageMode) {
            this._attributionImageMode = AttributionImageMode[attributionImageMode as keyof typeof AttributionImageMode];
        }

        // Restores the dimensions that are displayed in the embedding visualization
        const firstEmbeddingDimensionIndex = queryParameters.get('firstEmbeddingDimension');
        if (firstEmbeddingDimensionIndex) {
            this.firstEmbeddingDimensionIndex = parseInt(firstEmbeddingDimensionIndex, 10);
        }
        const secondEmbeddingDimensionIndex = queryParameters.get('secondEmbeddingDimension');
        if (secondEmbeddingDimensionIndex) {
            this.secondEmbeddingDimensionIndex = parseInt(secondEmbeddingDimensionIndex, 10);
        }

        // Refreshes the analysis
        await this.refreshAnalysisAsync();

        // Restores the selected embedding vectors
        const selectedEmbeddingVectors = queryParameters.get('embeddingVectors');
        if (selectedEmbeddingVectors) {
            const embeddingVectorIndices = selectedEmbeddingVectors
                .split(',')
                .map(index => parseInt(index, 10));

            if (this.analysis) {
                this.selectedEmbeddingVectors = this.analysis.embedding
                    .filter(point => embeddingVectorIndices.includes(point.attributionIndex));
            }

            await this.refreshAttributionsOfSelectedEmbeddingVectorsAsync();
        }

        // Finally, the loading has finished
        this.projectLoadingState = ResourceState.Finished;
    }

    /**
     * Reloads the analysis and all its information.
     *
     * @returns {Promise<void>} Returns a promise that resolves when the analysis has been reloaded.
     */
    private async refreshAnalysisAsync(): Promise<void> {

        if (!this.selectedAnalysisMethod ||
            !this.selectedAnalysisCategory ||
            !this.selectedClustering ||
            !this.selectedEmbedding ||
            !this.project
        ) {
            return;
        }

        this.selectedEmbeddingVectors = [];

        try {
            this.analysisLoadingState = ResourceState.Loading;
            this.analysis = await this.analysesService.getAsync(
                this.project.id,
                this.selectedAnalysisMethod.name,
                this.selectedAnalysisCategory.name,
                this.selectedClustering,
                this.selectedEmbedding
            );
            this.analysisLoadingState = ResourceState.Finished;
        } catch (exception: unknown) {
            if (exception instanceof Error) {
                this.analysisLoadingErrorMessage = exception.message.endsWith('.') ? exception.message : `${exception.message}.`;
            } else {
                this.analysisLoadingErrorMessage = 'An unknown error occurred while loading the analysis.';
            }
            this.analysisLoadingState = ResourceState.Failed;
        }
    }

    /**
     * Refreshes the eigenvalue plot.
     */
    private refreshEigenvaluePlot(): void {

        if (!this.analysis?.eigenvalues) {
            this.eigenvaluesGraphData = null;
            return;
        }

        this.eigenvaluesGraphData = new Array<Plotly.Data>();
        this.eigenvaluesGraphData.push({
            name: 'Eigenvalues',
            x: this.analysis.eigenvalues.map((_, index) => index).reverse(),
            y: this.analysis.eigenvalues,
            type: 'bar',
            width: 0.25,
            hoverinfo: 'x'
        });
    }

    /**
     * Is invoked when the user selects embedding vectors in the embedding visualizer. Retrieves the corresponding attributions and displays them.
     *
     * @returns {Promise<void>} Returns a promise that resolves when the attributions of the selected embedding vectors have been retrieved and
     *  displayed.
     */
    private async refreshAttributionsOfSelectedEmbeddingVectorsAsync(): Promise<void> {

        // Checks if a project is loaded and any embedding vectors were selected, if not, then the attributions can be removed
        if (!this.project || this.selectedEmbeddingVectors.length === 0) {
            this.selectedEmbeddingVectorAttributions = [];
            return;
        }

        // Gets the indices of the attributions that are to be loaded
        const attributionIndices = this.selectedEmbeddingVectors
            .slice(0, 20)
            .map(embeddingVector => embeddingVector.attributionIndex);

        // Gets the attributions of the embedding vectors that were selected
        let attributions: Attribution[];
        try {
            this.selectedEmbeddingVectorAttributionsLoadingState = ResourceState.Loading;
            attributions = await this.attributionsService.getAsync(this.project.id, attributionIndices, this.attributionImageMode);
        } catch (exception: unknown) {
            if (exception instanceof Error) {
                this.selectedEmbeddingVectorAttributionsLoadingErrorMessage = exception.message.endsWith('.')
                    ? exception.message
                    : `${exception.message}.`;
            } else {
                this.selectedEmbeddingVectorAttributionsLoadingErrorMessage = 'An unknown error occurred while loading the attributions.';
            }
            this.selectedEmbeddingVectorAttributionsLoadingState = ResourceState.Failed;
            return;
        }

        // Since loading the attributions can take some time, it might be that the user has already changed the selection, which would cause an error;
        // therefore, we check if the selected embedding vectors have changed; if so, we return early, because the attributions cannot be matched to
        // their respective embedding vectors anymore, which means we cannot get the cluster and the color of the cluster for the attributions from
        // their corresponding embedding vectors
        const currentAttributionIndices = this.selectedEmbeddingVectors
            .slice(0, 20)
            .map(embeddingVector => embeddingVector.attributionIndex);
        if (currentAttributionIndices.length !== attributionIndices.length ||
            !currentAttributionIndices.every(index => attributionIndices.includes(index))
        ) {
            this.selectedEmbeddingVectorAttributionsLoadingState = ResourceState.Finished;
            return;
        }

        // Assigns the dataset sample to their respective attribution
        this.selectedEmbeddingVectorAttributions = [];
        for (let index = 0; index < attributions.length; index++) {
            const attributionEmbeddingVectorCluster = this.availableClusters
                ?.find(cluster => cluster.index === this.selectedEmbeddingVectors[index]?.cluster);
            if (!attributionEmbeddingVectorCluster?.color) {
                throw new Error('The color of the cluster could not be found.');
            }
            this.selectedEmbeddingVectorAttributions.push({
                attribution: attributions[index],
                color: attributionEmbeddingVectorCluster.color,
                clusterIndex: this.selectedEmbeddingVectors[index].cluster
            });
        }
        this.selectedEmbeddingVectorAttributionsLoadingState = ResourceState.Finished;
    }

    /**
     * Read the file content asynchronously.
     *
     * @param {File} file The file from which the content is to be read.
     *
     * @returns {Promise<string | null>} Returns a promise that resolves when the content of the file has been read. The result of the promise
     *  contains the content of the file as a <code>string</code>. If the file was empty, then <code>null</code> is returned.
     */
    private async readFileContentAsync(file: File): Promise<string | null> {

        return new Promise<string | null>((resolve, reject) => {
            const reader: FileReader = new FileReader();

            reader.onloadend = () => {
                if (!reader.result) {
                    resolve(null);
                } else if (reader.result instanceof ArrayBuffer) {
                    resolve(new TextDecoder().decode(reader.result));
                } else {
                    resolve(reader.result);
                }
            };

            reader.onerror = () => {
                reject(new Error('An error occurred while reading the file.'));
            };

            reader.readAsText(file);
        });
    }

    /**
     * Retrieves the computed value of a CSS custom property.
     * @param propertyName The name of the CSS custom property that contains the theme color.
     * @returns Returns the computed value of the CSS custom property.
     */
    private getCssCustomProperty(propertyName: string): string {
        return window
            .getComputedStyle(document.body)
            .getPropertyValue(propertyName);
    }

    /**
     * Converts an HSL color to an RGB color.
     *
     * @param {number} hue The hue of the HSL color, which is measure in degrees and must be in the range [0, 360).
     * @param {number} saturation The saturation of the HSL color, which is a percentage and must be in the range [0, 100].
     * @param {number} lightness The lightness of the HSL color, which is a percentage and must be in the range [0, 100].
     *
     * @returns {[red: number, green: number, blue: number]} Returns the RGB color that corresponds to the HSL color.
     **/
    private convertHslToRgb(hue: number, saturation: number, lightness: number): [red: number, green: number, blue: number] {

        // Saturation and lightness are in percent, but must be in the range [0, 1]
        saturation = saturation / 100.0;
        lightness = lightness / 100.0;

        // If the saturation is 0, then the color is a shade of gray
        if (saturation === 0) {
            const shadeOfGray = Math.round(lightness * 255);
            return [shadeOfGray, shadeOfGray, shadeOfGray];
        }

        // See: https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB_alternative
        const c = saturation * Math.min(lightness, 1 - lightness);
        const f = (n: number, k: number = (n + hue / 30) % 12) => Math.round((lightness - c * Math.max(Math.min(k - 3, 9 - k, 1), -1)) * 255);
        return [f(0), f(8), f(4)];
    }

    /**
     * Converts an RGB color to its hexadecimal representation.
     * @param {number} red The red component of the RGB color, which must be in the range [0, 255].
     * @param {number} green The green component of the RGB color, which must be in the range [0, 255].
     * @param {number} blue The blue component of the RGB color, which must be in the range [0, 255].
     *
     * @returns {string} Returns the hexadecimal representation of the RGB color.
     */
    private convertRgbToHex(red: number, green: number, blue: number): string {
        const redHex = red.toString(16).padStart(2, '0');
        const greenHex = green.toString(16).padStart(2, '0');
        const blueHex = blue.toString(16).padStart(2, '0');
        return `#${redHex}${greenHex}${blueHex}`;
    }

    /**
     * Parses the specified CSS color value in the format "rgb(<red>, <green>, <blue>)" and returns the RGB components.
     *
     * @param {string} color The CSS RGB color value that is to be parsed.
     *
     * @throws {Error} The specified color value is not a valid RGB color.
     *
     * @returns {[red: number, green: number, blue: number]} Returns the RGB components of the color.
     */
    private parseCssRgbColor(color: string): [red: number, green: number, blue: number] {

        const rgb = /^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/.exec(color);
        if (!rgb) {
            throw new Error(`The property value "${color}" is not a valid RGB color.`);
        }

        const red = parseInt(rgb[1], 10);
        const green = parseInt(rgb[2], 10);
        const blue = parseInt(rgb[3], 10);

        return [red, green, blue];
    }

    /**
     * Parses the specified CSS color value in the format "hsl(<hue>, <saturation>%, <lightness>%) and returns the HSL components.
     *
     * @param {string} color The CSS HSL color value that is to be parsed.
     *
     * @throws {Error} The specified color value is not a valid HSL color.
     *
     * @returns {[hue: number, saturation: number, lightness: number]} Returns the HSL components of the color.
     **/
    private parseCssHslColor(color: string): [hue: number, saturation: number, lightness: number] {

        const hsl = /^hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)$/.exec(color);
        if (!hsl) {
            throw new Error(`The property value "${color}" is not a valid HSL color.`);
        }

        const hue = parseInt(hsl[1], 10);
        const saturation = parseInt(hsl[2], 10);
        const lightness = parseInt(hsl[3], 10);

        return [hue, saturation, lightness];
    }

    /**
     * Parses the specified CSS color value and returns the RGB components. The color may be in HSL or RGB format.
     *
     * @param {string} color The CSS color value that is to be parsed.
     *
     * @throws {Error} The specified color value is neither a valid HSL nor a valid RGB color.
     *
     * @returns {[red: number, green: number, blue: number]} Returns the RGB components of the color.
     */
    private parseCssColor(color: string): [red: number, green: number, blue: number] {
        try {
            return this.parseCssRgbColor(color);
        } catch {
            const [hue, saturation, lightness] = this.parseCssHslColor(color);
            return this.convertHslToRgb(hue, saturation, lightness);
        }
    }

    /**
     * Retrieves the theme color from the specified CSS custom properties.
     * @param propertyName The name of the CSS custom property that contains the theme color.
     * @returns Returns the theme color in hexadecimal RGB format.
     */
    private getThemeColor(propertyName: string): string {

        const propertyValue = this.getCssCustomProperty(propertyName);
        const [red, green, blue] = this.parseCssColor(propertyValue);
        return this.convertRgbToHex(red, green, blue);
    }

    // #endregion

    // #region Public Methods

    /**
     * Is invoked when the user hovers the mouse over an embedding.
     *
     * @param {HoverEvent} event The event object that contains the information about the embedding that the user hovered over.
     *
     * @returns {Promise<void>} Returns a promise that resolves when the dataset sample preview has been loaded.
     */
    public async onHoverAsync(event: HoverEvent): Promise<void> {

        if (!this.project) {
            return;
        }

        this.isHoveringOverEmbeddingVector = true;
        const embedding = event.embeddingVector as EmbeddingVector;

        this.hoveredEmbeddingVectorDatasetSamplePreviewLoadingState = ResourceState.Loading;

        let attribution: Attribution;
        try {
            attribution = await this.attributionsService.getByIndexAsync(
                this.project.id,
                embedding.attributionIndex,
                AttributionImageMode.Attribution);
        } catch (exception: unknown) {
            if (exception instanceof Error) {
                this.hoveredEmbeddingVectorDatasetSamplePreviewLoadingErrorMessage = exception.message.endsWith('.')
                    ? exception.message
                    : `${exception.message}.`;
            } else {
                this.hoveredEmbeddingVectorDatasetSamplePreviewLoadingErrorMessage = 'An unknown error occurred while loading the attributions.';
            }
            this.hoveredEmbeddingVectorDatasetSamplePreviewLoadingState = ResourceState.Failed;
            return;
        }

        try {
            this.hoveredEmbeddingVectorDatasetSamplePreview = await this.datasetsService.getAsync(this.project.id, attribution.index);
        } catch (exception: unknown) {
            if (exception instanceof Error) {
                this.hoveredEmbeddingVectorDatasetSamplePreviewLoadingErrorMessage = exception.message.endsWith('.')
                ? exception.message
                : `${exception.message}.`;
            } else {
                this.hoveredEmbeddingVectorDatasetSamplePreviewLoadingErrorMessage = 'An unknown error occurred while loading the dataset sample.';
            }
            this.hoveredEmbeddingVectorDatasetSamplePreviewLoadingState = ResourceState.Failed;
        }

        this.hoveredEmbeddingVectorDatasetSamplePreviewLoadingState = ResourceState.Finished;
    }

    /**
     * Is invoked when the user moves the mouse away from a sample.
     */
    public onUnhover(): void {

        this.isHoveringOverEmbeddingVector = false;
        this.hoveredEmbeddingVectorDatasetSamplePreview = null;
    }

    /**
     * Is invoked when the user rotates the mouse wheel. Scrolls the element that the user was scrolling in horizontally.
     *
     * @param event The event arguments of the mouse wheel event.
     */
    public onMouseWheelRotation(event: WheelEvent): void {

        event.preventDefault();
        if (event.target instanceof HTMLElement) {
            let target: HTMLElement | null = event.target;
            while (target) {
                const style = window.getComputedStyle(target);
                const overflow = style.getPropertyValue('overflow');
                if (overflow.startsWith('scroll') || overflow.startsWith('auto')) {
                    target.scrollBy({ left: event.deltaY });
                    break;
                }
                target = target.parentElement;
            }
        }
    }

    /**
     * Selects the embedding vectors of the cluster with the specified index.
     *
     * @param {number} index The index of the cluster that is to be selected.
     */
    public selectCluster(index: number): void {

        if (!this.analysis) {
            return;
        }

        const embeddingVectorsInCluster = this.analysis.embedding.filter(embeddingVector => embeddingVector.cluster === index);
        this.selectedEmbeddingVectors = embeddingVectorsInCluster;
    }

    /**
     * Is invoked when user clicks the "Export" button. Exports the current state of the application as a JSON file and all information required to
     * restore it.
     */
    public export(): void {

        if (!this.project || !this.analysis) {
            this.exportSavingErrorMessage = 'The project or the analysis is not loaded.';
            this.exportSavingState = ResourceState.Failed;
            return;
        }

        this.exportSavingState = ResourceState.Saving;

        const selectedEmbeddingVectorsIndices = this.selectedEmbeddingVectors.map(embeddingVector => embeddingVector.attributionIndex);
        const selectedEmbeddingVectorsClusters = this.selectedEmbeddingVectors.map(embeddingVector => embeddingVector.cluster);

        const allEmbeddingVectorsIndices = this.analysis.embedding.map(embeddingVector => embeddingVector.attributionIndex);
        const allEmbeddingVectorsClusters = this.analysis.embedding.map(embeddingVector => embeddingVector.cluster);

        const data: ImportExportDataJson = {
            projectId: this.project.id,
            projectName: this.project.name,
            modelName: this.project.model,
            datasetName: this.project.dataset,
            selectedAnalysisMethod: this.selectedAnalysisMethod?.name,
            selectedAnalysisCategory: this.selectedAnalysisCategory?.name,
            selectedCategoryHumanReadableName: this.selectedAnalysisCategory?.humanReadableName,
            selectedEmbeddingName: this.selectedEmbedding,
            selectedClustering: this.selectedClustering,
            numberOfClusters: this.numberOfClusters,
            selectedColorMap: this.selectedColorMap?.name,
            selectedImageMode: this.attributionImageMode,
            selectedEmbeddingVectorsIndices: selectedEmbeddingVectorsIndices,
            selectedEmbeddingVectorsClusters: selectedEmbeddingVectorsClusters,
            allEmbeddingVectorsIndices: allEmbeddingVectorsIndices,
            allEmbeddingVectorsClusters: allEmbeddingVectorsClusters
        };

        const now = new Date();
        const year = now.getFullYear().toString();
        const month = now.getMonth().toString().padStart(2, '0');
        const day = now.getDay().toString().padStart(2, '0');
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const seconds = now.getSeconds().toString().padStart(2, '0');
        const fileName =
            `${year}-${month}-${day}-${hours}-${minutes}-${seconds} ` +
            `${this.project.name} - ` +
            `${this.selectedAnalysisCategory?.humanReadableName} (${this.selectedAnalysisCategory?.name}) - ` +
            `${this.selectedAnalysisMethod?.name} - ${this.selectedClustering}.json`;

        const jsonExport = new Blob(
            [JSON.stringify(data, undefined, 2)],
            {type: 'application/json'}
        );
        saveAs(jsonExport, fileName);

        this.exportSavingState = ResourceState.Finished;
    }

    /**
     * Is invoked when user hits the "Import" button and chooses a file. Imports the selected file and restores the state that is stored in it.
     *
     * @param {Event} event The event arguments for the change event of the file input. It contains the files that were selected by the user. Under
     *  normal circumstances, the user should only be able to select a single file, but if the event arguments contain multiple files, then only the
     *  first is loaded.
     *
     * @returns {Promise<void>} Returns a promise that resolves when the import has been completed.
     */
    public async importAsync(event: Event): Promise<void> {

        // Starts the loading process
        this.importLoadingState = ResourceState.Loading;

        // Retrieves the file that was selected by the user; although this should not be possible, if the user managed to select multiple files, the
        // first one is used
        const htmlInputEvent: HTMLInputEvent = event as HTMLInputEvent;
        if (!htmlInputEvent.target.files || htmlInputEvent.target.files.length === 0) {
            this.importLoadingErrorMessage = 'No file was selected.';
            this.importLoadingState = ResourceState.Failed;
            return;
        }
        const file = htmlInputEvent.target.files[0];

        // Loads the content of the file
        let dataJsonString: string | null;
        try {
            dataJsonString = await this.readFileContentAsync(file);
        } catch (exception: unknown) {
            if (exception instanceof Error) {
                this.importLoadingErrorMessage = `An error occurred while reading the file: ${exception.message}`;
            } else {
                this.importLoadingErrorMessage = 'An unknown error occurred while reading the file.';
            }
            this.importLoadingState = ResourceState.Failed;
            return;
        }

        // Checks if the file was empty
        if (!dataJsonString) {
            this.importLoadingErrorMessage = 'The file was empty.';
            this.importLoadingState = ResourceState.Failed;
            return;
        }

        // Parses the content of the file as JSON
        let data: ImportExportDataJson;
        try {
            data = JSON.parse(dataJsonString) as ImportExportDataJson;
        } catch (exception: unknown) {
            if (exception instanceof Error && exception.message) {
                this.importLoadingErrorMessage = `An error occurred while parsing the JSON: ${exception.message}`;
            } else {
                this.importLoadingErrorMessage = 'An unknown error occurred while parsing the JSON.';
            }
            this.importLoadingState = ResourceState.Failed;
            return;
        }

        // Loads the project (if the ID was specified, then the project is loaded by ID, otherwise by name)
        try {
            if (data.projectId) {
                this.projectId = data.projectId;
                this.project = await this.projectsService.getByIdAsync(this.projectId);
            } else if (data.projectName) {
                const projects = await this.projectsService.getAsync();
                const foundProject = projects.find(project => project.name == data.projectName);
                if (!foundProject) {
                    this.importLoadingErrorMessage = `The project with the name ${data.projectName} could not be found.`;
                    this.importLoadingState = ResourceState.Failed;
                    return;
                }
                this.projectId = foundProject.id;
                this.project = await this.projectsService.getByIdAsync(this.projectId);
            } else {
                this.importLoadingErrorMessage = 'Both the project ID and name are missing in the imported data.';
                this.importLoadingState = ResourceState.Failed;
                return;
            }
        } catch (exception: unknown) {
            if (exception instanceof Error) {
                this.importLoadingErrorMessage = exception.message.endsWith('.') ? exception.message : `${exception.message}.`;
            } else {
                this.importLoadingErrorMessage = 'An unknown error occurred while loading the project.';
            }
            this.importLoadingState = ResourceState.Failed;
            return;
        }

        // Gets the selected analysis method that was stored in the imported data from the project
        const selectedAnalysisMethod = this.project.analysisMethods.find(analysis => analysis.name === data.selectedAnalysisMethod);
        if (!selectedAnalysisMethod) {
            this.importLoadingErrorMessage = `The selected analysis method ${data.selectedAnalysisMethod} could not be found in the project.`;
            this.importLoadingState = ResourceState.Failed;
            return;
        }
        this._selectedAnalysisMethod = selectedAnalysisMethod;

        // Gets the selected category that was stored in the imported data from the project
        const selectedAnalysisCategory = this._selectedAnalysisMethod.categories.find(category => category.name === data.selectedAnalysisCategory);
        if (!selectedAnalysisCategory) {
            this.importLoadingErrorMessage = 'The selected analysis category could not be found in the project.';
            this.importLoadingState = ResourceState.Failed;
            return;
        }
        this._selectedAnalysisCategory = selectedAnalysisCategory;

        // Gets the selected clustering that was stored in the imported data from the project
        const selectedClustering = this._selectedAnalysisMethod.clusterings.find(clustering => clustering === data.selectedClustering)
        if (!selectedClustering) {
            this.importLoadingErrorMessage = 'The selected clustering could not be found in the project.';
            this.importLoadingState = ResourceState.Failed;
            return;
        }
        this._selectedClustering = selectedClustering;

        // Gets the selected embedding that was stored in the imported data from the project
        const selectedEmbedding = this._selectedAnalysisMethod.embeddings.find(embedding => embedding === data.selectedEmbeddingName);
        if (!selectedEmbedding) {
            this.importLoadingErrorMessage = 'The selected embedding could not be found in the project.';
            this.importLoadingState = ResourceState.Failed;
            return;
        }
        this._selectedEmbedding = selectedEmbedding;

        // Gets the selected color map that was stored in the imported data from the project
        const selectedColorMap = this.colorMaps?.find(colorMap => colorMap.name === data.selectedColorMap);
        if (!selectedColorMap) {
            this.importLoadingErrorMessage = 'The selected color map could not be found in the project.';
            this.importLoadingState = ResourceState.Failed;
            return;
        }
        this.selectedColorMap = selectedColorMap;

        // Gets the attribution image mode that was stored in the imported data from the project
        this.attributionImageMode = AttributionImageMode[data.selectedImageMode as keyof typeof AttributionImageMode];

        // Refreshes the analysis based on the selected analysis method, analysis category, clustering, and embedding
        await this.refreshAnalysisAsync();

        if (this.analysis) {
            this.selectedEmbeddingVectors = this.analysis.embedding
                .filter(point => data.selectedEmbeddingVectorsIndices?.includes(point.attributionIndex));
            await this.refreshAttributionsOfSelectedEmbeddingVectorsAsync();
        }

        // The loading has finished
        this.importLoadingState = ResourceState.Finished;
    }

    /**
     * Creates a link with all the necessary information to open ViRelAy to the exact state that it is currently in.
     */
    public createShareableLink(): void {

        if (!this.project || !this.analysis) {
            this.shareableLinkUrlCreationErrorMessage = 'The project or the analysis is not loaded.';
            this.shareableLinkUrlCreationState = ResourceState.Failed;
            return;
        }

        this.shareableLinkUrlCreationState = ResourceState.Creating;
        const shareableLinkUrl = new URL(window.location.origin);
        shareableLinkUrl.pathname = `projects/${this.project.id}`;

        shareableLinkUrl.searchParams.append('firstEmbeddingDimension', this.firstEmbeddingDimensionIndex.toString());
        shareableLinkUrl.searchParams.append('secondEmbeddingDimension', this.secondEmbeddingDimensionIndex.toString());
        if (this.selectedColorMap) {
            shareableLinkUrl.searchParams.append('colorMap', this.selectedColorMap.name);
        }
        if (this.selectedAnalysisMethod) {
            shareableLinkUrl.searchParams.append('analysisMethod', this.selectedAnalysisMethod.name);
        }
        if (this.selectedAnalysisCategory) {
            shareableLinkUrl.searchParams.append('analysisCategory', this.selectedAnalysisCategory.name);
        }
        if (this.selectedClustering) {
            shareableLinkUrl.searchParams.append('clustering', this.selectedClustering);
        }
        if (this.selectedEmbedding) {
            shareableLinkUrl.searchParams.append('embedding', this.selectedEmbedding);
        }
        shareableLinkUrl.searchParams.append('imageMode', this.attributionImageMode);
        if (this.selectedEmbeddingVectors.length > 0) {
            shareableLinkUrl.searchParams.append(
                'embeddingVectors',
                this.selectedEmbeddingVectors
                    .map(embeddingVector => embeddingVector.attributionIndex)
                    .join(','));
        }

        // Sets the shareable link, so that it can be copied by the user
        this.shareableLinkUrl = shareableLinkUrl.href;
        this.shareableLinkUrlCreationState = ResourceState.Finished;

        // Opens the dialog where the user can copy the shareable link
        this.isShareDialogOpen = true;
    }

    /**
     * Copies the generated shareable link into the clipboard of the user.
     */
    public async copyShareableLink(): Promise<void> {

        if (!this.shareableLinkUrl) {
            return;
        }

        try {
            await navigator.clipboard.writeText(this.shareableLinkUrl);
            this.shareableLinkUrlCopyingState = ResourceState.Finished;
        }
        catch {
            this.shareableLinkUrlCopyingErrorMessage = 'The shareable link could not be copied into the clipboard.';
            this.shareableLinkUrlCopyingState = ResourceState.Failed;
        }
    }

    /**
     * Closes the share dialog.
     */
    public closeShareDialog(): void {
        this.shareableLinkUrlCopyingState = ResourceState.Pending;
        this.shareableLinkUrl = null;
        this.isShareDialogOpen = false;
    }

    // #endregion

    // #region OnInit Implementation

    /**
     * Is invoked when the component is initialized. Retrieves the ID of the project from the current rout and loads it.
     */
    public ngOnInit(): void {

        // Subscribes to changes to the color preferences of the user and updates the colors used in the Eigenvalue plot accordingly (all other colors
        // are automatically updated because they are defined in CSS; even though, the CSS custom properties for the color values are also used for
        // the Eigenvalue plot, they do not automatically update, so the colors of the Eigenvalue plot are updated manually)
        this.colorSchemePreferenceChangeSubscription = fromEvent(window.matchMedia('(prefers-color-scheme: dark)'), 'change').subscribe(() => {

            if (this.eigenvaluesGraphLayout.xaxis) {
                this.eigenvaluesGraphLayout.xaxis.linecolor = this.getThemeColor('--virelay-cluster-pane-eigenvalue-plot-axis-line-color');
                this.eigenvaluesGraphLayout.xaxis.tickcolor = this.getThemeColor('--virelay-cluster-pane-eigenvalue-plot-axis-tick-color');
            }

            if (this.eigenvaluesGraphLayout.font) {
                this.eigenvaluesGraphLayout.font.color = this.getThemeColor('--virelay-cluster-pane-eigenvalue-plot-font-color');
            }

            this.refreshEigenvaluePlot();
        });

        // Subscribes to changes of the parameters of the currently activated route; when the parameters of the route change, then the project ID is
        // retrieved from the URL and the project is loaded; the subscribe method ensures that the callback is invoked once at the beginning when the
        // subscription is made, which means that, as soon as the subscription is made, the project with the ID of the current route is loaded; after
        // that, the project is only reloaded if the route changes; the subscription is stored, so that it can be unsubscribed from when the component
        // is destroyed (ViRelAy currently only has a single page, so there is no way for the user to navigate away from the project page, but in
        // order to be future proof for the event that we introduce another page, the subscription is still stored and unsubscribed from when the
        // component is destroyed, so that we will not have any surprises in the future)
        this.routeParametersChangeSubscription = this.route.paramMap.subscribe(paramMap => {
            if (!paramMap.has('id')) {
                return;
            }

            const idParameter = paramMap.get('id');
            if (!idParameter) {
                return;
            }

            this.projectId = parseInt(idParameter, 10);
            void this.refreshProjectAsync();
        });

        // Loads the color maps from the RESTful API
        this.colorMapsLoadingState = ResourceState.Loading;
        this.colorMapsService.getAsync()
            .then((colorMaps: ColorMap[]) => {

                // Stores the color maps in the component
                this.colorMaps = colorMaps;

                // Checks if the user has selected a color map in the URL parameters, if not, then the default color map is selected
                const queryParameters = new URLSearchParams(window.location.search);
                const colorMap = this.colorMaps.find(colorMap => colorMap.name === queryParameters.get('colorMap'));
                if (colorMap) {
                    this.selectedColorMap = colorMap;
                } else {
                    const defaultColorMaps = this.colorMaps.filter(colorMap => colorMap.name === 'black-fire-red');
                    if (defaultColorMaps.length > 0) {
                        this.selectedColorMap = defaultColorMaps[0];
                    } else {
                        this.selectedColorMap = this.colorMaps[0];
                    }
                }

                // The color maps have been loaded
                this.colorMapsLoadingState = ResourceState.Finished;
            })
            .catch((exception: unknown) => {
                if (exception instanceof Error) {
                    this.colorMapsLoadingErrorMessage = exception.message.endsWith('.') ? exception.message : `${exception.message}.`;
                } else {
                    this.colorMapsLoadingErrorMessage = 'An unknown error occurred while loading the color maps.';
                }
                this.colorMapsLoadingState = ResourceState.Failed;
            });
    }

    // #endregion

    // #region OnDestroy Implementation

    /**
     * Is invoked when the component is destroyed, i.e., the user navigates away from the project page. Unsubscribes from all subscriptions and event
     * handlers to prevent memory leaks.
     */
    public ngOnDestroy(): void {

        if (this.colorSchemePreferenceChangeSubscription) {
            this.colorSchemePreferenceChangeSubscription.unsubscribe();
        }

        if (this.routeParametersChangeSubscription) {
            this.routeParametersChangeSubscription.unsubscribe();
        }
    }

    // #endregion
}

/**
 * Represents the data that is being saved to a file when the user exports the current state of the ViRelAy.
 */
interface ImportExportDataJson {

    // #region Properties

    /**
     * The ID of the project that was loaded when the state was exported.
     */
    projectId?: number;

    /**
     * The name of the project that was loaded when the state was exported.
     */
    projectName?: string;

    /**
     * The name of the model of the project that was loaded when the state was exported.
     */
    modelName?: string;

    /**
     * The name of the dataset of the project that was loaded when the state was exported.
     */
    datasetName?: string;

    /**
     * The name of the analysis method of the project that was selected by the user when the state was exported.
     */
    selectedAnalysisMethod?: string;

    /**
     * The name of the category of the analysis that was selected by the user when the state was exported.
     */
    selectedAnalysisCategory?: string;

    /**
     * The human-readable name of the category of the analysis that was selected by the user when the state was exported.
     */
    selectedCategoryHumanReadableName?: string;

    /**
     * The name of the embedding that was selected by the user when the state was exported.
     */
    selectedEmbeddingName?: string | null;

    /**
     * The name of the clustering that was selected by the user when the state was exported.
     */
    selectedClustering?: string | null;

    /**
     * The number of clusters that were available when the state was exported.
     */
    numberOfClusters?: number;

    /**
     * The name of the color map that was selected by the user when the state was exported.
     */
    selectedColorMap?: string;

    /**
     * The name of the image mode that was selected by the user when the state was exported.
     */
    selectedImageMode?: string;

    /**
     * The indices of the embedding vectors that were selected by the user when the state was exported.
     */
    selectedEmbeddingVectorsIndices?: number[];

    /**
     * The clusters of the embedding vectors that were selected by the user when the state was exported.
     */
    selectedEmbeddingVectorsClusters?: number[];

    /**
     * The indices of all the embedding vectors that were available when the state was exported.
     */
    allEmbeddingVectorsIndices?: number[];

    /**
     * The clusters of all the embedding vectors that were available when the state was exported.
     */
    allEmbeddingVectorsClusters?: number[];

    // #endregion
}
