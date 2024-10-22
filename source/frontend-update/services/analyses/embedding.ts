
import { ServiceException } from '@services/service-exception';

/**
 * Represents a single embedding.
 */
export class Embedding {

    /**
     * Initializes a new Embedding instance.
     *
     * @param {EmbeddingJson} embedding The JSON object that was retrieved from the backend REST API.
     *
     * @throws {ServiceException} The embedding is <code>null</code> or <code>undefined</code>.
     */
    public constructor(embedding?: EmbeddingJson) {

        if (!embedding) {
            throw new ServiceException('Analyses', { message: 'The embedding could not be loaded from the received JSON.'});
        }

        this.cluster = embedding.cluster;
        this.attributionIndex = embedding.attributionIndex;
        this.value = embedding.value;
    }

    /**
     * Contains the index of the cluster to which the embedding belongs.
     */
    public cluster: number;

    /**
     * Contains the index of the attribution of the embedding.
     */
    public attributionIndex: number;

    /**
     * Contains the value of the embedding.
     */
    public value: Array<number>;
}


/**
 * Represents an interface for the JSON objects that contain the information about an embedding and are retrieved from the REST API.
 */
export interface EmbeddingJson {

    /**
     * Contains the index of the cluster to which the embedding belongs.
     */
    cluster: number;

    /**
     * Contains the index of the attribution of the embedding.
     */
    attributionIndex: number;

    /**
     * Contains the value of the embedding.
     */
    value: Array<number>;
}
