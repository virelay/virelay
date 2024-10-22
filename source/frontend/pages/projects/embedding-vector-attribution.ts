
import {Attribution} from '@services/attributions/attribution';

/**
 * Represents the attribution of an embedding vector.
 */
export interface EmbeddingVectorAttribution {

    // #region Properties

    /**
     * Contains the attribution of the embedding vector.
     */
    attribution: Attribution;

    /**
     * Contains the color of the embedding vector in the embedding visualizer.
     */
    color: string;

    /**
     * Contains the index of the cluster to which the embedding vector belongs.
     */
    clusterIndex: number
}
