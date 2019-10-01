
import { ElementRef, ViewChild, Component, AfterViewInit, NgZone, OnDestroy, Input, EventEmitter, Output, forwardRef } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import * as THREE from 'three';
import * as OrbitControls from 'three-orbitcontrols';

/**
 * Represents a data point of the embedding.
 */
export interface DataPoint {

    /**
     * Contains the value of the data point.
     */
    value: Array<number>;

    /**
     * Contains the index of the cluster to which the data point belongs.
     */
    cluster: number;
}

/**
 * Represents a hover event.
 */
export class HoverEvent {

    /**
     * Initializes a new HoverEvent instance.
     * @param dataPoint The data point that the user is hovering.
     * @param clusterColor The color that was assigned to the cluster of the data point.
     */
    public constructor(dataPoint: DataPoint, clusterColor: THREE.Color) {
        this.dataPoint = dataPoint;
        this.clusterColor = clusterColor.getStyle();
    }

    /**
     * Contains the data point that the user hovered.
     */
    public dataPoint: DataPoint;

    /**
     * Contains the color that was assigned to the cluster.
     */
    public clusterColor: string;
}

/**
 * Represents a visualizer, which can render an embedding.
 */
@Component({
    selector: 'app-embedding-visualizer',
    styleUrls: ['embedding-visualizer.component.scss'],
    templateUrl: 'embedding-visualizer.component.html',
    providers: [{
        provide: NG_VALUE_ACCESSOR,
        useExisting: forwardRef(() => EmbeddingVisualizerComponent),
        multi: true
    }]
})
export class EmbeddingVisualizerComponent implements ControlValueAccessor, AfterViewInit, OnDestroy {

    /**
     * Initializes a new EmbeddingVisualizerComponent instance.
     * @param ngZone The Angular zone, which is needed to execute some code outside of Angular.
     */
    public constructor(private ngZone: NgZone) { }

    /**
     * Contains a value that determines whether the component has been initialized.
     */
    private isInitialized: boolean;

    /**
     * Contains the renderer, which is used to render the data points of the embedding.
     */
    private renderer: THREE.WebGLRenderer;

    /**
     * Contains the camera that is used to render the embedding.
     */
    private camera: THREE.OrthographicCamera;

    /**
     * Contains the controller for the camera, which allows the user to zoom and pan.
     */
    private cameraController: OrbitControls;

    /**
     * Contains the scene, which contains the data points of the embedding.
     */
    private scene: THREE.Scene;

    /**
     * Contains the ID of the current animation frame. This is needed to cancel the animation frame, when the component
     * is being destroyed.
     */
    private animationFrameId: number;

    /**
     * Contains the object that contains the visualization of the embedding.
     */
    private embeddingObject: THREE.Points;

    /**
     * Contains the texture for the data points.
     */
    private dataPointTexture: THREE.Texture;

    /**
     * Contains the index of the data point that is currently being hovered by the user.
     */
    private indexOfDataPointCurrentBeingHovered: number = null;

    /**
     * Contains a value that determines whether the user is currently making a selection.
     */
    private isSelecting: boolean;

    /**
     * Contains the rectangle of the selection box.
     */
    private selectionBoxRectangle: { x: number; y: number; startX: number; startY: number; };

    /**
     * Contains the indices of the data points that have been selected by the user.
     */
    private selectedDataPointIndices: Array<number>;

    /**
     * Contains the data points that have been selected by the user.
     */
    private selectedDataPoints: Array<DataPoint>;

    /**
     * Contains a reference to the HTML element that represents the render target.
     */
    @ViewChild('renderTarget', { static: false })
    public renderTarget: ElementRef;

    /**
     * Contains a reference to the HTML element that represents the selection box.
     */
    @ViewChild('selectionBox', { static: false })
    public selectionBox: ElementRef;

    /**
     * Contains a value that determines whether the visualizer is disabled.
     */
    @Input()
    public disabled: boolean;

    /**
     * Contains the number of clusters that are present in the embedding.
     */
    private numberOfClusters: number;

    /**
     * Contains the embedding that is displayed in the visualizer.
     */
    private _embedding: Array<DataPoint>;

    /**
     * Gets the embedding that is displayed in the visualizer.
     */
    public get embedding(): Array<DataPoint> {
        return this._embedding;
    }

    /**
     * Sets the embedding that is displayed in the visualizer.
     */
    @Input()
    public set embedding(value: Array<DataPoint>) {

        // Stores the new value
        this._embedding = value;

        // Determines the total number of clusters, which is needed to determine the number of colors that are needed
        // for the visualization
        if (this.embedding) {
            const clusters = new Array<number>();
            for (const cluster of this.embedding.map(dataPoint => dataPoint.cluster)) {
                if (clusters.indexOf(cluster) === -1) {
                    clusters.push(cluster);
                }
            }
            this.numberOfClusters = clusters.length;
        }

        // Updates the visualizer with the new data points
        this.updateVisualizer();
    }

    /**
     * Contains the first dimension of the embedding that is being visualized. Only two dimensions can be displayed at a
     * time, if the embedding is multi-dimensional, then this is the dimension that is displayed on the x-axis.
     */
    private _firstDimension = 0;

    /**
     * Gets the first dimension of the embedding that is being visualized.
     */
    public get firstDimension(): number {
        return this._firstDimension;
    }

    /**
     * Sets the first dimension of the embedding that is being visualized.
     */
    @Input()
    public set firstDimension(value: number) {
        this._firstDimension = value;
        this.updateVisualizer();
    }

    /**
     * Contains the second dimension of the embedding that is being visualized. Only two dimensions can be displayed at
     * a time, if the embedding is multi-dimensional, then this is the dimension that is displayed on the y-axis.
     */
    private _secondDimension = 1;

    /**
     * Gets the second dimension of the embedding that is being visualized.
     */
    public get secondDimension(): number {
        return this._secondDimension;
    }

    /**
     * Sets the second dimension of the embedding that is being visualized.
     */
    @Input()
    public set secondDimension(value: number) {
        this._secondDimension = value;
        this.updateVisualizer();
    }

    /**
     * Contains the background color of the embedding visualizer.
     */
    @Input()
    public backgroundColor: string;

    /**
     * The event that is invoked when the user hovers a data point.
     */
    @Output()
    public onHover: EventEmitter<HoverEvent> = new EventEmitter<HoverEvent>();

    /**
     * The event that is invoked, when the user moves the mouse away from a data point.
     */
    @Output()
    public onUnhover: EventEmitter<any> = new EventEmitter();

    /**
     * Is invoked when the selected data points change.
     */
    private onSelectedDataPointsChange = (_: Array<DataPoint>) => {};

    /**
     * Is invoked when the selected data points were "touched" (which in this case is nothing more then changed).
     */
    private onSelectedDataPointsTouched = () => {};

    /**
     * Is invoked when the window was resized. Updates the camera and the renderer to the new canvas size.
     */
    private onWindowResize() {

        // Gets a reference to the canvas that has probably also been resized due to the window resize
        const renderTargetNativeElement: HTMLCanvasElement = this.renderTarget.nativeElement;

        // Determines the size of the render target (in this case the parent element is used, because the canvas itself
        // gets a fixed size from the renderer and therefore never resizes unless the renderer is updated)
        const width = renderTargetNativeElement.parentElement.clientWidth;
        const height = renderTargetNativeElement.parentElement.clientHeight;

        // Updates the camera and the renderer to the size
        (this.camera as any).aspect = width / height;
        this.camera.updateProjectionMatrix();

        // Updates the renderer
        this.renderer.setSize(width, height);
    }

    /**
     * Updates the position of the selection box.
     */
    private updateSelectionBox() {

        // If nothing is currently selected, then the selection box is hidden, otherwise it is shown
        const selectionBoxNativeElement: HTMLDivElement = this.selectionBox.nativeElement;
        if (!this.isSelecting) {
            selectionBoxNativeElement.style.display = 'none';
            return;
        }
        selectionBoxNativeElement.style.display = 'block';

        // Updates the selection box
        const left = Math.min(this.selectionBoxRectangle.x, this.selectionBoxRectangle.startX);
        const top = Math.min(this.selectionBoxRectangle.y, this.selectionBoxRectangle.startY);
        const width = Math.abs(this.selectionBoxRectangle.x - this.selectionBoxRectangle.startX);
        const height = Math.abs(this.selectionBoxRectangle.y - this.selectionBoxRectangle.startY);
        selectionBoxNativeElement.style.left = `${left}px`;
        selectionBoxNativeElement.style.top = `${top}px`;
        selectionBoxNativeElement.style.width = `${width}px`;
        selectionBoxNativeElement.style.height = `${height}px`;

        // Determines the size of the render target
        const renderTargetNativeElement: HTMLCanvasElement = this.renderTarget.nativeElement;
        const renderTargetWidth = renderTargetNativeElement.clientWidth;
        const renderTargetHeight = renderTargetNativeElement.clientHeight;

        // Determines the positions of the corners of the selection box in camera space
        const right = (Math.max(this.selectionBoxRectangle.x, this.selectionBoxRectangle.startX) / renderTargetWidth) * 2 - 1;
        const bottom = -(Math.max(this.selectionBoxRectangle.y, this.selectionBoxRectangle.startY) / renderTargetHeight) * 2 + 1;
        const topLeftVector = new THREE.Vector3((left / renderTargetWidth) * 2 - 1, -(top / renderTargetHeight) * 2 + 1, 0);
        const bottomRightVector = new THREE.Vector3(right, bottom, 0);

        // Brings the vertices of the corners of the selection box into the world space
        topLeftVector.unproject(this.camera);
        bottomRightVector.unproject(this.camera);

        // Determines which embedding objects are inside the selection box
        this.selectedDataPointIndices = new Array<number>();
        for (let index = 0; index < this.embedding.length; index++) {
            const vector = (this.embeddingObject.geometry as THREE.Geometry).vertices[index];
            if (vector.x > topLeftVector.x && vector.x < bottomRightVector.x && vector.y < topLeftVector.y && vector.y > bottomRightVector.y) {
                this.selectedDataPointIndices.push(index);
            }
        }

        // Increases the saturation of the data points that are selected and decreases the saturation of the rest
        for (let index = 0; index < this.embedding.length; index++) {
            const dataPoint = this.embedding[index];
            if (this.selectedDataPointIndices.indexOf(index) === -1) {
                (this.embeddingObject.geometry as THREE.Geometry).colors[index] = new THREE.Color().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 0.25, 0.5);
            } else {
                (this.embeddingObject.geometry as THREE.Geometry).colors[index] = new THREE.Color().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 1, 0.5);
            }
        }
        (this.embeddingObject.geometry as THREE.Geometry).colorsNeedUpdate = true;
    }

    /**
     * Is invoked, when the user clicks a mouse button. When the left mouse button is clicked, then selection process is
     * started.
     * @param event The event arguments that contain information about the event such as the button that was clicked.
     */
    private onMouseDown = (event: MouseEvent) => {

        // Only when the left mouse button was clicked, the selection is started, otherwise nothing needs to be done
        if (event.buttons !== 1) {
            return;
        }

        // Starts the selection
        this.isSelecting = true;

        // Since the selection box is positioned absolutely, the left and top of the render target need to be subtracted
        // from the mouse position
        const renderTargetNativeElement: HTMLCanvasElement = this.renderTarget.nativeElement;
        const boundingRectangle = (renderTargetNativeElement as HTMLElement).getBoundingClientRect();

        // Shows the selection box
        this.selectionBoxRectangle = {
            x: event.clientX - boundingRectangle.left,
            y: event.clientY - boundingRectangle.top,
            startX: event.clientX - boundingRectangle.left,
            startY: event.clientY - boundingRectangle.top
        };
        this.updateSelectionBox();
    }

    /**
     * Is invoked, when the user moves the mouse over the window. This is used for making selections.
     */
    private onMouseMoveWindow = (event: MouseEvent) => {

        // When the user is performing a selection, then the selection box must be updated
        if (this.isSelecting) {

            // Since the selection box is positioned absolutely, the left and top of the render target need to be subtracted
            // from the mouse position
            const renderTargetNativeElement: HTMLCanvasElement = this.renderTarget.nativeElement;
            const boundingRectangle = (renderTargetNativeElement as HTMLElement).getBoundingClientRect();

            // Updates the selection box
            this.selectionBoxRectangle.x = event.clientX - boundingRectangle.left;
            this.selectionBoxRectangle.y = event.clientY - boundingRectangle.top;
            this.updateSelectionBox();
        }
    }

    /**
     * Is invoked, when the user releases a mouse button. Stops the selection process.
     */
    private onMouseUp = () => {

        // If the user wasn't selecting, then nothing needs to be done
        if (!this.isSelecting) {
            return;
        }

        // Stops the selection
        this.isSelecting = false;
        this.selectionBoxRectangle = null;
        this.updateSelectionBox();

        // Gets the data points that have been selected and writes them
        const selectedDataPoints = this.embedding.filter((_, index) => this.selectedDataPointIndices.indexOf(index) !== -1);
        this.writeValue(selectedDataPoints);
    }

    /**
     * Is invoked, when the user moves the mouse over the render target. This is used to detect the data point the user
     * is hovering over.
     * @param event The event arguments that contain information about the event such as mouse position.
     */
    private onMouseMoveRenderTarget = (event: MouseEvent) => {

        // If the component has not been initialized or no embedding has been specified, there is nothing that the user
        // can hover over
        if (!this.isInitialized || !this.embedding) {
            return;
        }

        // When the user is simultaneously using any mouse buttons, then the hover events are not emitted
        if (event.buttons !== 0) {
            if (this.indexOfDataPointCurrentBeingHovered != null) {
                this.onUnhover.emit();
            }
            this.indexOfDataPointCurrentBeingHovered = null;
            return;
        }

        // Gets a reference to the render target
        const renderTargetNativeElement: HTMLCanvasElement = this.renderTarget.nativeElement;

        // Determines the size of the render target
        const width = renderTargetNativeElement.clientWidth;
        const height = renderTargetNativeElement.clientHeight;

        // Determines the position of the mouse in camera space
        const boundingRectangle = (event.target as HTMLElement).getBoundingClientRect();
        const mouseX = ((event.clientX - boundingRectangle.left) / width) * 2 - 1;
        const mouseY = -((event.clientY - boundingRectangle.top) / height) * 2 + 1;
        const mouseVector = new THREE.Vector3(mouseX, mouseY, 0);

        // Casts a ray from the camera through the mouse and checks if any of the data points intersect with the ray
        const rayCaster = new THREE.Raycaster();
        rayCaster.params.Points.threshold = 5 / this.camera.zoom;
        rayCaster.setFromCamera(mouseVector, this.camera);
        const intersections = rayCaster.intersectObject(this.embeddingObject);
        if (intersections.length > 0) {
            if (this.indexOfDataPointCurrentBeingHovered !== intersections[0].index) {
                const dataPoint = this.embedding[intersections[0].index];
                const clusterColor = (this.embeddingObject.geometry as THREE.Geometry).colors[intersections[0].index];
                this.indexOfDataPointCurrentBeingHovered = intersections[0].index;
                this.onHover.emit(new HoverEvent(dataPoint, clusterColor));
            }
        } else {
            if (this.indexOfDataPointCurrentBeingHovered != null) {
                this.onUnhover.emit();
            }
            this.indexOfDataPointCurrentBeingHovered = null;
        }
    }

    /**
     * Renders the scene.
     */
    private render = () => {
        requestAnimationFrame(this.render);
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Updates the visualization of the embedding.
     */
    private updateVisualizer() {

        // If the component has not been initialized or no embedding has been specified, then the visualizer cannot be
        // updated
        if (!this.isInitialized || !this.embedding) {
            return;
        }

        // If there is an embedding that is currently being visualized, then the object is remove from the scene
        if (this.embeddingObject) {
            this.scene.remove(this.embeddingObject);
        }

        // Gets a reference to the render target
        const renderTargetNativeElement: HTMLCanvasElement = this.renderTarget.nativeElement;

        // Determines the size of the render target
        const width = renderTargetNativeElement.clientWidth * 0.95 / 2;
        const height = renderTargetNativeElement.clientHeight * 0.95 / 2;

        // Creates the scene object for the data points
        let maximumX = 0;
        let maximumY = 0;
        const pointsGeometry = new THREE.Geometry();
        for (const dataPoint of this.embedding) {

            // Determines X and Y positions of the points that are the farthest away from the origin, this information
            // is used to scale the data points so that they fill out the whole viewport
            if (Math.abs(dataPoint.value[this.firstDimension]) > maximumX) {
                maximumX = Math.abs(dataPoint.value[this.firstDimension]);
            }
            if (Math.abs(dataPoint.value[this.secondDimension]) > maximumY) {
                maximumY = Math.abs(dataPoint.value[this.secondDimension]);
            }

            // Creates a new vertex for the data point
            const vertex = new THREE.Vector3(
                dataPoint.value[this.firstDimension],
                dataPoint.value[this.secondDimension],
                -1
            );
            pointsGeometry.vertices.push(vertex);

            // Generates a color for the data point based on its cluster
            const color = new THREE.Color().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 0.75, 0.5);
            pointsGeometry.colors.push(color);
        }

        // Scales all data points so that they fill out the whole viewport
        pointsGeometry.scale(width / maximumX, height / maximumY, 1);

        // Creates the material for the points (setting the size attenuation to false means that the points always have
        // the same size no matter the zoom level)
        const pointsMaterial = new THREE.PointsMaterial({
            size: 8,
            sizeAttenuation: false,
            vertexColors: THREE.VertexColors,
            map: this.dataPointTexture,
            transparent: true,
            depthTest: false
        });

        // Generates the scene object that contains all the data points and adds it to the scene
        this.embeddingObject = new THREE.Points(pointsGeometry, pointsMaterial);
        this.scene.add(this.embeddingObject);

        // Resets the camera
        this.cameraController.reset();
    }

    /**
     * Is invoked after the view was initialized (and the view children are available). Initializes the renderer.
     */
    public ngAfterViewInit(): void {

        // Gets a reference to the canvas onto which the embedding will be rendered
        const renderTargetNativeElement: HTMLCanvasElement = this.renderTarget.nativeElement;

        // Determines the size of the render target
        const width = renderTargetNativeElement.clientWidth;
        const height = renderTargetNativeElement.clientHeight;

        // Creates the renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: renderTargetNativeElement,
            antialias: true
        });
        this.renderer.setSize(width, height);
        const backgroundColor = new THREE.Color().setStyle(this.backgroundColor || '#FFFFFF');
        this.renderer.setClearColor(backgroundColor);

        // Creates the scene
        this.scene = new THREE.Scene();

        // Creates the camera
        this.camera = new THREE.OrthographicCamera(width / -2, width / 2, height / 2, height / -2, -10, 1000);
        this.camera.position.set(0, 0, 1);
        this.scene.add(this.camera);

        // Adds a camera controller for zooming and panning
        this.cameraController = new OrbitControls(this.camera, renderTargetNativeElement);
        this.cameraController.minZoom = 0.5;
        this.cameraController.maxZoom = 5.0;
        this.cameraController.screenSpacePanning = true;
        this.cameraController.enableRotate = false;

        // Loads the texture that is used to display the data points
        this.dataPointTexture = new THREE.TextureLoader().load('assets/images/circle-sprite.png');

        // This should be run outside angular zones, because it could trigger heavy change detection cycles
        this.ngZone.runOutsideAngular(() => {

            // Subscribes to the window resize event, in which case the camera and the renderer have to be updated
            window.addEventListener('resize', () => this.onWindowResize());

            // Starts the rendering
            this.render();
        });

        // Subscribes to the mouse move event of the canvas, which is used to raise the hover events
        renderTargetNativeElement.addEventListener('mousemove', this.onMouseMoveRenderTarget);

        // Subscribes to the mouse events, which are used for making a selection
        renderTargetNativeElement.addEventListener('mousedown', this.onMouseDown);
        window.addEventListener('mousemove', this.onMouseMoveWindow);
        window.addEventListener('mouseup', this.onMouseUp);

        // The initialization has finished
        this.isInitialized = true;
        this.updateVisualizer();
    }

    /**
     * Is invoked when the component is being destroyed. Aborts the animation.
     */
    public ngOnDestroy(): void {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
    }

    /**
     * Changes the selected data points.
     * @param value The new selected data points.
     */
    public writeValue(value: Array<DataPoint>): void {

        // Stores the selected data points
        this.selectedDataPoints = value ? value : new Array<DataPoint>();

        // Checks if the user selected data points or deselected everything, if the user selected data points, then the
        // saturation of the selected data points is increased and the saturation of the data points that are not
        // selected is decreased, if the user deselected everything, then the saturation of the data points is reset
        if (this.embeddingObject) {
            if (this.selectedDataPoints.length !== 0) {
                for (let index = 0; index < this.embedding.length; index++) {
                    const dataPoint = this.embedding[index];
                    if (this.selectedDataPoints.indexOf(dataPoint) === -1) {
                        (this.embeddingObject.geometry as THREE.Geometry).colors[index] = new THREE.Color().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 0.25, 0.5);
                    } else {
                        (this.embeddingObject.geometry as THREE.Geometry).colors[index] = new THREE.Color().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 1, 0.5);
                    }
                }
            } else {
                for (let index = 0; index < this.embedding.length; index++) {
                    const dataPoint = this.embedding[index];
                    (this.embeddingObject.geometry as THREE.Geometry).colors[index] = new THREE.Color().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 0.5, 0.5);
                }
            }
            (this.embeddingObject.geometry as THREE.Geometry).colorsNeedUpdate = true;
        }

        // Propagates the change
        this.onSelectedDataPointsChange(this.selectedDataPoints);
        this.onSelectedDataPointsTouched();
    }

    /**
     * Registers a callback, which is invoked, when the selected data points change.
     * @param callback The callback that is invoked, when the selected data points change.
     */
    public registerOnChange(callback: (value: Array<DataPoint>) => void): void {
        this.onSelectedDataPointsChange = callback;
    }

    /**
     * Registers a callback, which is invoked, when the selected data points were touched.
     * @param callback The callback that is invoked, when the selected data points were touched.
     */
    public registerOnTouched(callback: () => void): void {
        this.onSelectedDataPointsTouched = callback;
    }

    /**
     * Sets whether the visualizer is enabled or disabled.
     * @param isDisabled Determines whether the visualizer is disabled.
     */
    public setDisabledState?(isDisabled: boolean): void {
        this.disabled = isDisabled;
    }
}
