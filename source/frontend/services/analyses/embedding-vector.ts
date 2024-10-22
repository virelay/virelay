
import { ServiceException } from '@services/service-exception';

/**
 * Represents a single vector from the embedding of the analysis.
 */
export class EmbeddingVector {

    // #region Constructor

    /**
     * Initializes a new EmbeddingVector instance.
     *
     * @param {EmbeddingVectorJson} embeddingVector The JSON object that was retrieved from the backend REST API.
     *
     * @throws {ServiceException} The embedding vector is <code>null</code> or <code>undefined</code>.
     */
    public constructor(embeddingVector?: EmbeddingVectorJson) {

        if (!embeddingVector) {
            throw new ServiceException('Analyses', { message: 'The embedding vector could not be loaded from the received JSON.'});
        }

        this.cluster = embeddingVector.cluster;
        this.attributionIndex = embeddingVector.attributionIndex;
        this.value = embeddingVector.value;
    }

    // #endregion

    // #region Public Properties

    /**
     * Gets or sets the index of the cluster to which the embedding vector belongs.
     */
    public accessor cluster: number;

    /**
     * Gets or sets the index of the attribution of the embedding vector.
     */
    public accessor attributionIndex: number;

    /**
     * Gets or sets the value of the embedding vector.
     */
    public accessor value: number[];

    // #endregion
}


/**
 * Represents an interface for the JSON objects that contain the information about an embedding vector and are retrieved from the REST API.
 */
export interface EmbeddingVectorJson {

    // #region Fields

    /**
     * Contains the index of the cluster to which the embedding vector belongs.
     */
    cluster: number;

    /**
     * Contains the index of the attribution of the embedding vector.
     */
    attributionIndex: number;

    /**
     * Contains the value of the embedding vector.
     */
    value: number[];

    // #endregion
}
