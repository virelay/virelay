
import * as THREE from 'three';

import { EmbeddingVector } from '@components/embedding-visualizer/embedding-vector';

/**
 * An event that is triggered when the user hovers an embedding vector in the embedding visualizer.
 */
export class HoverEvent {

    // #region Constructor

    /**
     * Initializes a new HoverEvent instance.
     * @param {EmbeddingVector} embeddingVector The embedding vector that the user is hovering.
     * @param {THREE.Color} clusterColor The color that was assigned to the cluster of the embedding vector.
     */
    public constructor(embeddingVector: EmbeddingVector, clusterColor: THREE.Color) {

        this.embeddingVector = embeddingVector;
        this.clusterColor = clusterColor.getStyle();
    }

    // #endregion

    // #region Properties

    /**
     * Contains the embedding vector that the user hovered.
     */
    public embeddingVector: EmbeddingVector;

    /**
     * Contains the color that was assigned to the cluster.
     */
    public clusterColor: string;

    // #endregion
}
