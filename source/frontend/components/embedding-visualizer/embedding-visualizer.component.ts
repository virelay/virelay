
import { delay, of, ReplaySubject, Subscription, switchMap } from 'rxjs';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { AfterViewInit, Component, ElementRef, EventEmitter, forwardRef, inject, Input, NgZone, OnDestroy, Output, ViewChild } from '@angular/core';

import { SelectionBox } from '@components/embedding-visualizer/selection-box';
import { EmbeddingVector } from '@services/analyses/embedding-vector';
import { HoverEvent } from '@components/embedding-visualizer/hover-event';
import { NG_VALUE_ACCESSOR } from '@angular/forms';

/**
 * A component that renders a point cloud that visualizes two of potentially many dimensions of the vectors of an embedding.
 */
@Component({
    selector: 'virelay-embedding-visualizer',
    templateUrl: 'embedding-visualizer.component.html',
    styleUrl: 'embedding-visualizer.component.scss',
    providers: [{
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => EmbeddingVisualizerComponent),
            multi: true
        }]
})
export class EmbeddingVisualizerComponent implements AfterViewInit, OnDestroy {

    // #region Private Fields

    /**
     * Contains the Angular zone, which is needed to execute code outside of Angular's change detection.
     */
    private readonly ngZone: NgZone = inject(NgZone);

    /**
     * Contains a value that determines whether the component has been initialized.
     */
    private isInitialized: boolean = false;

    /**
     * Contains the renderer, which is used to render the embedding vectors of the embedding.
     */
    private renderer: THREE.WebGLRenderer | null = null;

    /**
     * Contains the camera that is used to render the embedding.
     */
    private camera: THREE.OrthographicCamera | null = null;

    /**
     * Contains the controller for the camera, which allows the user to zoom and pan.
     */
    private cameraController: OrbitControls | null = null;

    /**
     * Contains the scene, which contains the embedding vectors of the embedding.
     */
    private scene: THREE.Scene | null = null;

    /**
     * Contains a handle to the current animation frame request. This is needed to cancel the animation frame, when the component is being destroyed.
     */
    private animationFrameRequestHandle: number | null = null;

    /**
     * Contains the object that contains the visualization of the embedding.
     */
    private embeddingVectorPoints: THREE.Points | null = null;

    /**
     * Contains the texture for the embedding vectors.
     */
    private embeddingVectorTexture: THREE.Texture | null = null;

    /**
     * Contains a subject that emits the index of the embedding vector that is currently being hovered by the user.
     */
    private readonly embeddingVectorHoverObservable = new ReplaySubject<number | null>();

    /**
     * Contains the subscription to the embedding vector hover observable. The subscription is stored, so that it can be unsubscribed from when the
     * component is destroyed.
     */
    private embeddingVectorHoverSubscription: Subscription | null = null;

    /**
     * Contains a value that determine whether the hover event was emitted. The unhover event will only be emitted if the hover event was emitted
     * before.
     */
    private wasHoverEventEmitted: boolean = false;

    /**
     * Contains a value that determines whether the user is currently making a selection.
     */
    private isSelecting: boolean = false;

    /**
     * Contains the rectangle of the selection box.
     */
    private selectionBoxRectangle: SelectionBox | null = null;

    /**
     * Contains the indices of the embedding vectors that have been selected by the user.
     */
    private selectedEmbeddingVectorIndices: number[] = [];

    /**
     * Contains the embedding vectors that have been selected by the user.
     */
    private selectedEmbeddingVectors: EmbeddingVector[] = [];

    /**
     * Contains the number of clusters that are present in the embedding.
     */
    private numberOfClusters: number = 0;

    /**
     * Contains the callback that is invoked when the selected embedding vectors change.
     */
    private onSelectedEmbeddingVectorsChange: ((selection: EmbeddingVector[]) => void) | null = null;

    /**
     * Contains the callback that is invoked when the selected embedding vectors were "touched" (which in this case is nothing more then changed).
     */
    private onSelectedEmbeddingVectorsTouched: (() => void) | null = null;

    // #endregion

    // #region Public Properties

    /**
     * Gets or sets a reference to the HTML element that represents the render target.
     */
    @ViewChild('renderTarget')
    public accessor renderTarget: ElementRef | null = null;

    /**
     * Gets or sets a reference to the HTML element that represents the selection box.
     */
    @ViewChild('selectionBox')
    public accessor selectionBox: ElementRef | null = null;

    /**
     * Gets or sets the number of milliseconds to throttle the hover event.
     */
    @Input()
    public accessor hoverDebounceTime: number = 500;

    /**
     * Gets or sets a value that determines whether the visualizer is disabled.
     */
    @Input()
    public accessor disabled: boolean = false;

    /**
     * Gets or sets a value that determines whether the user can select embedding vectors. This can be used to temporarily disable the selection
     * mechanism when the attributions for the selected embeddings are being loaded.
     */
    @Input()
    public accessor canSelect: boolean = true;

    /**
     * Contains the embedding that is displayed in the visualizer.
     */
    private _embedding: EmbeddingVector[] = [];

    /**
     * Gets the embedding that is displayed in the visualizer.
     *
     * @returns {EmbeddingVector[]} The embedding that is displayed in the visualizer.
     */
    public get embedding(): EmbeddingVector[] {
        return this._embedding;
    }

    /**
     * Sets the embedding that is displayed in the visualizer.
     *
     * @param {EmbeddingVector[]} value The embedding that is displayed in the visualizer.^
     */
    @Input()
    public set embedding(value: EmbeddingVector[]) {

        // Stores the new value
        this._embedding = value;

        // Determines the total number of clusters, which is needed to determine the number of colors that are needed for the visualization
        const clusters = new Array<number>();
        for (const cluster of this.embedding.map(embeddingVector => embeddingVector.cluster)) {
            if (!clusters.includes(cluster)) {
                clusters.push(cluster);
            }
        }
        this.numberOfClusters = clusters.length;

        // Updates the visualizer with the new embedding vectors
        this.updateVisualizer();
    }

    /**
     * Contains the first dimension of the embedding that is being visualized. Only two dimensions can be displayed at a time, if the embedding is
     * multi-dimensional, then this is the dimension that is displayed on the x-axis.
     */
    private _firstEmbeddingDimensionIndex = 0;

    /**
     * Gets the first dimension of the embedding that is being visualized.
     *
     * @returns {number} Returns the first dimension of the embedding that is being visualized.
     */
    public get firstEmbeddingDimensionIndex(): number {
        return this._firstEmbeddingDimensionIndex;
    }

    /**
     * Sets the first dimension of the embedding that is being visualized.
     *
     * @param {number} value The first dimension of the embedding that is being visualized.
     */
    @Input()
    public set firstEmbeddingDimensionIndex(value: number) {
        this._firstEmbeddingDimensionIndex = value;
        this.updateVisualizer();
    }

    /**
     * Contains the second dimension of the embedding that is being visualized. Only two dimensions can be displayed at a time, if the embedding is
     * multi-dimensional, then this is the dimension that is displayed on the y-axis.
     */
    private _secondEmbeddingDimensionIndex = 1;

    /**
     * Gets the second dimension of the embedding that is being visualized.
     *
     * @returns {number} Returns the second dimension of the embedding that is being visualized.
     */
    public get secondEmbeddingDimensionIndex(): number {
        return this._secondEmbeddingDimensionIndex;
    }

    /**
     * Sets the second dimension of the embedding that is being visualized.
     *
     * @param {number} value The second dimension of the embedding that is being visualized.
     */
    @Input()
    public set secondEmbeddingDimensionIndex(value: number) {
        this._secondEmbeddingDimensionIndex = value;
        this.updateVisualizer();
    }

    /**
     * Gets or sets the event that is invoked when the user hovers a embedding vector.
     */
    @Output()
    public hover: EventEmitter<HoverEvent> = new EventEmitter<HoverEvent>();

    /**
     * Gets or sets the event that is invoked, when the user moves the mouse away from a embedding vector.
     */
    @Output()
    public unhover: EventEmitter<void> = new EventEmitter<void>();

    // #endregion

    // #region Private Methods

    /**
     * A callback that is invoked when the window is resized. Updates the camera and the renderer to the new canvas size.
     */
    private onWindowResize(): void {

        // If the HTML element that represents the render target, the camera, or the renderer is not available, then nothing can be done
        if (!this.renderTarget || !this.camera || !this.renderer) {
            return;
        }

        // Gets a reference to the canvas that has probably also been resized due to the window resize
        const renderTargetNativeElement = this.renderTarget.nativeElement as HTMLCanvasElement;

        // If the parent element of the render target is not available, then nothing can be done
        if (!renderTargetNativeElement.parentElement) {
            return;
        }

        // Determines the size of the render target (in this case the parent element is used, because the canvas itself gets a fixed size from the
        // renderer and therefore never resizes unless the renderer is updated)
        const width = renderTargetNativeElement.parentElement.clientWidth;
        const height = renderTargetNativeElement.parentElement.clientHeight;

        // Updates the camera and the renderer to the size
        this.camera.left = width / -2;
        this.camera.right = width / 2;
        this.camera.top = height / 2;
        this.camera.bottom = height / -2;
        this.camera.updateProjectionMatrix();

        // Updates the renderer
        this.renderer.setSize(width, height);
    }

    /**
     * Updates the position of the selection box.
     */
    private updateSelectionBox(): void {

        // If HTML element that visualizes the selection box is not available, then nothing can be done
        if (!this.selectionBox) {
            return;
        }

        // If nothing is currently selected, then the selection box is hidden, otherwise it is shown
        const selectionBoxNativeElement = this.selectionBox.nativeElement as HTMLDivElement;
        if (!this.isSelecting) {
            selectionBoxNativeElement.style.display = 'none';
            return;
        }
        selectionBoxNativeElement.style.display = 'block';

        // If the selection box is not available, then nothing further can be done
        if (!this.selectionBoxRectangle) {
            return;
        }

        // Updates the selection box
        selectionBoxNativeElement.style.left = `${this.selectionBoxRectangle.left}px`;
        selectionBoxNativeElement.style.top = `${this.selectionBoxRectangle.top}px`;
        selectionBoxNativeElement.style.width = `${this.selectionBoxRectangle.width}px`;
        selectionBoxNativeElement.style.height = `${this.selectionBoxRectangle.height}px`;

        // If the render target, the camera is not available, or the 3D object that renders the embedding vectors is not available, then nothing more
        // than updating the selection box can be done
        if (!this.renderTarget || !this.camera || !this.embeddingVectorPoints) {
            return;
        }

        // Determines the size of the render target
        const renderTargetNativeElement = this.renderTarget.nativeElement as HTMLCanvasElement;
        const renderTargetWidth = renderTargetNativeElement.clientWidth;
        const renderTargetHeight = renderTargetNativeElement.clientHeight;

        // Determines the positions of the corners of the selection box in camera space
        const left = (this.selectionBoxRectangle.left / renderTargetWidth) * 2 - 1;
        const right = (this.selectionBoxRectangle.right / renderTargetWidth) * 2 - 1;
        const top = -(this.selectionBoxRectangle.top / renderTargetHeight) * 2 + 1;
        const bottom = -(this.selectionBoxRectangle.bottom / renderTargetHeight) * 2 + 1;
        const topLeftVector = new THREE.Vector3(left, top, 0);
        const bottomRightVector = new THREE.Vector3(right, bottom, 0);

        // Brings the vertices of the corners of the selection box into the world space
        topLeftVector.unproject(this.camera);
        bottomRightVector.unproject(this.camera);

        // Determines which embedding objects are inside the selection box
        this.selectedEmbeddingVectorIndices = new Array<number>();
        const vertices = this.embeddingVectorPoints.geometry.attributes['position'].array;
        for (let index = 0; index < this.embedding.length; index++) {
            const vectorX = vertices[index * 3];
            const vectorY = vertices[index * 3 + 1];
            if (vectorX > topLeftVector.x && vectorX < bottomRightVector.x && vectorY < topLeftVector.y && vectorY > bottomRightVector.y) {
                this.selectedEmbeddingVectorIndices.push(index);
            }
        }

        // Increases the saturation of the embedding vectors that are selected and decreases the saturation of the rest
        const colorsAttribute = this.embeddingVectorPoints.geometry.attributes['color'];
        const colors = (colorsAttribute.array as Float32Array);
        for (let index = 0; index < this.embedding.length; index++) {
            const embeddingVector = this.embedding[index];
            if (!this.selectedEmbeddingVectorIndices.includes(index)) {
                const color = new THREE.Color().setHSL((360 / this.numberOfClusters * embeddingVector.cluster) / 360, 0.5, 0.5);
                colors[index * 3] = color.r;
                colors[index * 3 + 1] = color.g;
                colors[index * 3 + 2] = color.b;
            } else {
                const color = new THREE.Color().setHSL((360 / this.numberOfClusters * embeddingVector.cluster) / 360, 1, 0.5);
                colors[index * 3] = color.r;
                colors[index * 3 + 1] = color.g;
                colors[index * 3 + 2] = color.b;
            }
        }
        colorsAttribute.needsUpdate = true;
    }

    /**
     * Is invoked, when the user clicks a mouse button. When the left mouse button is clicked, then selection process is
     * started.
     *
     * @param {MouseEvent} event The event arguments that contain information about the event such as the button that was clicked.
     */
    private onMouseDown = (event: MouseEvent) => {

        // If the component has not been initialized, is disabled, or the selection mechanism is disabled, then nothing can be done
        if (!this.isInitialized || this.disabled || !this.canSelect) {
            return;
        }

        // If the render target is not available, then the position of the mouse relative to the render target cannot be determined, so the selection
        // process cannot be started
        if (!this.renderTarget) {
            return;
        }

        // Only when the left mouse button was clicked, the selection is started, otherwise nothing needs to be done
        if (event.buttons !== 1) {
            return;
        }

        // Starts the selection
        this.isSelecting = true;

        // Since the selection box is positioned absolutely, the left and top of the render target need to be subtracted from the mouse position
        const renderTargetNativeElement = this.renderTarget.nativeElement as HTMLCanvasElement;
        const boundingRectangle = (renderTargetNativeElement as HTMLElement).getBoundingClientRect();

        // Shows the selection box
        this.selectionBoxRectangle = new SelectionBox(
            event.clientX - boundingRectangle.left,
            event.clientY - boundingRectangle.top);
        this.updateSelectionBox();
    }

    /**
     * Is invoked, when the user moves the mouse over the window. This is used for making selections.
     *
     * @param {MouseEvent} event The event arguments that contain information about the event such as mouse position.
     */
    private onMouseMoveWindow = (event: MouseEvent) => {

        // If the user is not selecting, then nothing needs to be done
        if (!this.isSelecting) {
            return;
        }

        // If the render target is not available, then the position of the mouse relative to the render target cannot be determined, so the selection
        // process cannot be started
        if (!this.renderTarget) {
            return;
        }

        // Since the selection box is positioned absolutely, the left and top of the render target need to be subtracted from the mouse position
        const renderTargetNativeElement = this.renderTarget.nativeElement as HTMLCanvasElement;
        const boundingRectangle = (renderTargetNativeElement as HTMLElement).getBoundingClientRect();

        // Updates the selection box
        this.selectionBoxRectangle?.update(
            event.clientX - boundingRectangle.left,
            event.clientY - boundingRectangle.top);
        this.updateSelectionBox();
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

        // Gets the embedding vectors that have been selected and writes them
        const selectedEmbeddingVectors = this.embedding.filter((_, index) => this.selectedEmbeddingVectorIndices.includes(index));
        this.writeValue(selectedEmbeddingVectors);
    }

    /**
     * Is invoked, when the user moves the mouse over the render target. This is used to detect the embedding vector the user is hovering over.
     *
     * @param {MouseEvent} event The event arguments that contain information about the event such as mouse position.
     */
    private onMouseMoveRenderTarget = (event: MouseEvent) => {

        // If the component has not been initialized, or no embedding has been specified, then there is nothing that the user can hover over; if there
        // is no render target, camera, or 3D object that renders the embedding vectors, then there is nothing that can be done, as there is no
        // embedding visualizer to hover over
        if (!this.isInitialized || this.embedding.length === 0 || !this.renderTarget || !this.camera || !this.embeddingVectorPoints) {
            return;
        }

        // When the user is simultaneously using any mouse buttons, then the hover events are not emitted
        if (event.buttons !== 0) {
            this.embeddingVectorHoverObservable.next(null);
            return;
        }

        // Gets a reference to the render target
        const renderTargetNativeElement = this.renderTarget.nativeElement as HTMLCanvasElement;

        // Determines the size of the render target
        const width = renderTargetNativeElement.clientWidth;
        const height = renderTargetNativeElement.clientHeight;

        // Determines the position of the mouse in camera space
        const boundingRectangle = (event.target as HTMLElement).getBoundingClientRect();
        const mouseX = ((event.clientX - boundingRectangle.left) / width) * 2 - 1;
        const mouseY = -((event.clientY - boundingRectangle.top) / height) * 2 + 1;
        const mouseVector = new THREE.Vector2(mouseX, mouseY);

        // Casts a ray from the camera through the mouse and checks if any of the embedding vectors intersect with the ray
        const rayCaster = new THREE.Raycaster();
        rayCaster.params.Points.threshold = 5 / this.camera.zoom;
        rayCaster.setFromCamera(mouseVector, this.camera);
        const intersections = rayCaster.intersectObject(this.embeddingVectorPoints);
        if (intersections.length > 0 && intersections[0].index) {
            this.embeddingVectorHoverObservable.next(intersections[0].index);
        } else {
            this.embeddingVectorHoverObservable.next(null);
        }
    }

    /**
     * Renders the scene.
     */
    private render = () => {

        // If not renderer, scene, or camera is available, then nothing can be rendered
        if (!this.renderer || !this.scene || !this.camera) {
            return;
        }

        // Renders the scene
        this.renderer.render(this.scene, this.camera);

        // Requests an animation frame, which enables us to synchronize the rendering with the browser; once the browser repaints the screen the next
        // time, it will call our render method, which will render the scene and then request another animation frame (it would not make sense to
        // render the scene unless the browser is also repainting the screen; also the animation frames are paused when the browser tab is hidden)
        this.animationFrameRequestHandle = requestAnimationFrame(this.render);
    }

    /**
     * Updates the visualization of the embedding.
     */
    private updateVisualizer(): void {

        // If the component has not been initialized, no embedding has been specified, the render target is not available, or there is no scene to
        // render, then the embedding visualizer cannot be updated
        if (!this.isInitialized || this.embedding.length === 0 || !this.renderTarget || !this.scene) {
            return;
        }

        // If there is an embedding that is currently being visualized, then the object is remove from the scene
        if (this.embeddingVectorPoints) {
            this.scene.remove(this.embeddingVectorPoints);
        }

        // Gets a reference to the render target
        const renderTargetNativeElement = this.renderTarget.nativeElement as HTMLCanvasElement;

        // Determines the size of the render target
        const width = renderTargetNativeElement.clientWidth * 0.95 / 2;
        const height = renderTargetNativeElement.clientHeight * 0.95 / 2;

        // Creates the scene object for the embedding vectors
        let maximumX = 0;
        let maximumY = 0;
        const vertices = new Array<number>();
        const colors = new Array<number>();
        for (const embeddingVector of this.embedding) {

            // Determines X and Y positions of the points that are the farthest away from the origin, this information
            // is used to scale the embedding vectors so that they fill out the whole viewport
            if (Math.abs(embeddingVector.value[this.firstEmbeddingDimensionIndex]) > maximumX) {
                maximumX = Math.abs(embeddingVector.value[this.firstEmbeddingDimensionIndex]);
            }
            if (Math.abs(embeddingVector.value[this.secondEmbeddingDimensionIndex]) > maximumY) {
                maximumY = Math.abs(embeddingVector.value[this.secondEmbeddingDimensionIndex]);
            }

            // Creates a new vertex for the embedding vector
            vertices.push(embeddingVector.value[this.firstEmbeddingDimensionIndex], embeddingVector.value[this.secondEmbeddingDimensionIndex], -1);

            // Generates a color for the embedding vector based on its cluster
            const color = new THREE.Color().setHSL((360 / this.numberOfClusters * embeddingVector.cluster) / 360, 0.75, 0.5);
            colors.push(color.r, color.g, color.b);
        }
        const pointsGeometry = new THREE.BufferGeometry();
        pointsGeometry.setAttribute('position', new THREE.BufferAttribute(Float32Array.from(vertices), 3, true));
        pointsGeometry.setAttribute('color', new THREE.BufferAttribute(Float32Array.from(colors), 3, true));

        // Scales all embedding vectors so that they fill out the whole viewport
        const scaleFactor = Math.min(width / maximumX, height / maximumY);
        pointsGeometry.scale(scaleFactor, scaleFactor, 1);

        // Creates the material for the points (setting the size attenuation to false means that the points always have
        // the same size no matter the zoom level)
        const pointsMaterial = new THREE.PointsMaterial({
            size: 8,
            sizeAttenuation: false,
            vertexColors: true,
            map: this.embeddingVectorTexture,
            transparent: true,
            depthTest: false
        });

        // Generates the scene object that contains all the embedding vectors and adds it to the scene
        this.embeddingVectorPoints = new THREE.Points(pointsGeometry, pointsMaterial);
        this.scene.add(this.embeddingVectorPoints);

        // Resets the camera
        this.cameraController?.reset();
    }

    // #endregion

    // #region Public Methods

    /**
     * Changes the selected embedding vectors.
     *
     * @param {EmbeddingVector[]} value The new selected embedding vectors.
     */
    public writeValue(value?: EmbeddingVector[]): void {

        // Stores the selected embedding vectors
        this.selectedEmbeddingVectors = value ?? [];

        // Checks if the user selected embedding vectors or deselected everything, if the user selected embedding vectors, then the
        // saturation of the selected embedding vectors is increased and the saturation of the embedding vectors that are not
        // selected is decreased, if the user deselected everything, then the saturation of the embedding vectors is reset
        if (this.embeddingVectorPoints) {
            const colorsAttribute = this.embeddingVectorPoints.geometry.attributes['color'];
            const colors = (colorsAttribute.array as Float32Array);
            for (let index = 0; index < this.embedding.length; index++) {
                const embeddingVector = this.embedding[index];
                if (!this.selectedEmbeddingVectors.includes(embeddingVector)) {
                    const color = new THREE.Color().setHSL((360 / this.numberOfClusters * embeddingVector.cluster) / 360, 0.5, 0.5);
                    colors[index * 3] = color.r;
                    colors[index * 3 + 1] = color.g;
                    colors[index * 3 + 2] = color.b;
                } else {
                    const color = new THREE.Color().setHSL((360 / this.numberOfClusters * embeddingVector.cluster) / 360, 1, 0.5);
                    colors[index * 3] = color.r;
                    colors[index * 3 + 1] = color.g;
                    colors[index * 3 + 2] = color.b;
                }
            }
            colorsAttribute.needsUpdate = true;
        }

        // Propagates the change
        if (this.onSelectedEmbeddingVectorsChange) {
            this.onSelectedEmbeddingVectorsChange(this.selectedEmbeddingVectors);
        }
        if (this.onSelectedEmbeddingVectorsTouched) {
            this.onSelectedEmbeddingVectorsTouched();
        }
    }

    /**
     * Registers a callback, which is invoked, when the selected embedding vectors change.
     *
     * @param {(selection: EmbeddingVector[]) => void} callback The callback that is invoked, when the selected embedding vectors change.
     */
    public registerOnChange(callback: (selection: EmbeddingVector[]) => void): void {
        this.onSelectedEmbeddingVectorsChange = callback;
    }

    /**
     * Registers a callback, which is invoked, when the selected embedding vectors were touched.
     *
     * @param {() => void} callback The callback that is invoked, when the selected embedding vectors were touched.
     */
    public registerOnTouched(callback: () => void): void {
        this.onSelectedEmbeddingVectorsTouched = callback;
    }

    /**
     * Sets whether the visualizer is enabled or disabled.
     *
     * @param {boolean} isDisabled Determines whether the visualizer is disabled.
     */
    public setDisabledState?(isDisabled: boolean): void {
        this.disabled = isDisabled;
    }

    // #endregion

    // #region AfterViewInit Implementation

    /**
     * Is invoked after the view was initialized (and the view children are available). Initializes the renderer.
     */
    public ngAfterViewInit(): void {

        // If no render target is available, then the embedding visualizer cannot be initialized, because the embedding visualizer is rendered onto
        // the render target
        if (!this.renderTarget) {
            return;
        }

        // Gets a reference to the canvas onto which the embedding will be rendered
        const renderTargetNativeElement = this.renderTarget.nativeElement as HTMLCanvasElement;

        // Determines the size of the render target
        const width = renderTargetNativeElement.clientWidth;
        const height = renderTargetNativeElement.clientHeight;

        // Creates the renderer (alpha is set to true, so that the renderer supports transparency; the clear color is set to transparent, which means
        // that the actual background color of the elements behind it will be the background color of the embedding visualizer)
        this.renderer = new THREE.WebGLRenderer({
            canvas: renderTargetNativeElement,
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(width, height);
        this.renderer.setClearColor(0xffffff, 0);

        // Creates the scene
        this.scene = new THREE.Scene();

        // Creates the camera
        this.camera = new THREE.OrthographicCamera(width / -2, width / 2, height / 2, height / -2, -10, 1000);
        this.camera.position.set(0, 0, 1);
        this.scene.add(this.camera);

        // Adds a camera controller for zooming and panning
        this.cameraController = new OrbitControls(this.camera, renderTargetNativeElement);
        this.cameraController.minZoom = 0.1;
        this.cameraController.maxZoom = 10.0;
        this.cameraController.screenSpacePanning = true;
        this.cameraController.enableRotate = false;

        // Loads the texture that is used to display the embedding vectors
        this.embeddingVectorTexture = new THREE.TextureLoader().load('assets/images/circle-sprite.png');

        // This should be run outside angular zones, because it could trigger heavy change detection cycles
        this.ngZone.runOutsideAngular(() => {

            // Subscribes to the window resize event, in which case the camera and the renderer have to be updated
            window.addEventListener('resize', () => { this.onWindowResize(); });

            // Starts the rendering
            this.render();
        });

        // Subscribes to the mouse move event of the canvas, which is used to raise the hover events
        renderTargetNativeElement.addEventListener('mousemove', this.onMouseMoveRenderTarget);

        // Subscribes to the mouse events, which are used for making a selection
        renderTargetNativeElement.addEventListener('mousedown', this.onMouseDown);
        window.addEventListener('mousemove', this.onMouseMoveWindow);
        window.addEventListener('mouseup', this.onMouseUp);

        // Subscribes to the hover observable, which emits the index of the embedding vector that is currently being hovered by the user; when the
        // user un-hovers the embedding vector it emits null; the hovering is throttled, which is useful to prevent loading the attribution of the
        // embedding vector, even if the user is just moving the mouse over the embedding vectors without the intent of hovering over one; the
        // subscription emits the hover event, which can be listened to by the user of the component; the subscription is stored, so that it can be
        // unsubscribed from when the component is destroyed
        this.embeddingVectorHoverSubscription = this.embeddingVectorHoverObservable
            .pipe(switchMap(hoveredEmbeddingVectorIndex => hoveredEmbeddingVectorIndex === null
                ? of(hoveredEmbeddingVectorIndex)
                : of(hoveredEmbeddingVectorIndex).pipe(delay(this.hoverDebounceTime))))
            .subscribe(hoveredEmbeddingVectorIndex => {

                if (!this.embeddingVectorPoints) {
                    return;
                }

                if (hoveredEmbeddingVectorIndex !== null) {
                    const embeddingVector = this.embedding[hoveredEmbeddingVectorIndex];
                    const colors = this.embeddingVectorPoints.geometry.attributes['color'].array;
                    const red = colors[hoveredEmbeddingVectorIndex * 3];
                    const green = colors[hoveredEmbeddingVectorIndex * 3 + 1];
                    const blue = colors[hoveredEmbeddingVectorIndex * 3 + 2];
                    this.hover.emit(new HoverEvent(embeddingVector, new THREE.Color(red, green, blue)));
                    this.wasHoverEventEmitted = true;
                } else if (this.wasHoverEventEmitted) {
                    this.unhover.emit();
                    this.wasHoverEventEmitted = false;
                }
            });

        // The initialization has finished
        this.isInitialized = true;
        this.updateVisualizer();
    }

    // #endregion

    // #region OnDestroy Implementation

    /**
     * Is invoked when the component is being destroyed. Aborts the animation.
     */
    public ngOnDestroy(): void {

        // Cancels the current animation frame request, so that the browser stops calling our render method
        if (this.animationFrameRequestHandle) {
            cancelAnimationFrame(this.animationFrameRequestHandle);
        }

        // Unsubscribed from the hover event
        if (this.embeddingVectorHoverSubscription) {
            this.embeddingVectorHoverSubscription.unsubscribe();
        }
    }

    // #endregion
}
