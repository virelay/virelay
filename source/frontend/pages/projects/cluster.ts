
/**
 * Represents a single cluster of embedding vectors.
 */
export interface Cluster {

    // #region Properties

    /**
     * Contains the index of the cluster.
     */
    index: number;

    /**
     * Contains the hex color of the cluster in the embedding visualizer and the clustering selection pane.
     */
    color: string;

    /**
     * Contains the number of embedding vectors in the cluster.
     */
    size: number;

    // #endregion
}
