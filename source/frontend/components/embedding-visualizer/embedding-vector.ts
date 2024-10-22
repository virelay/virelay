
/**
 * An interface for vectors contained in the embedding that is being visualized by the embedding visualizer.
 */
export interface EmbeddingVector {

    // #region Properties

    /**
     * Contains the value of the data point.
     */
    value: number[];

    /**
     * Contains the index of the cluster to which the data point belongs.
     */
    cluster: number;

    // #endregion
}
