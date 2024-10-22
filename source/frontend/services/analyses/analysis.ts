
import { EmbeddingVector, EmbeddingVectorJson } from '@services/analyses/embedding-vector';
import { ServiceException } from '@services/service-exception';

/**
 * Represents a single analysis.
 */
export class Analysis {

    // #region Constructor

    /**
     * Initializes a new Analysis instance.
     *
     * @param {AnalysisJson} analysis The JSON object that was retrieved from the backend REST API.
     *
     * @throws {ServiceException} The analysis is <code>null</code> or <code>undefined</code>.
     */
    public constructor(analysis?: AnalysisJson) {

        if (!analysis) {
            throw new ServiceException('Analyses', { message: 'The analysis could not be loaded from the received JSON.'});
        }

        this.categoryName = analysis.categoryName;
        this.humanReadableCategoryName = analysis.humanReadableCategoryName;
        this.clusteringName = analysis.clusteringName;
        this.embeddingName = analysis.embeddingName;
        this.embedding = analysis.embedding.map((embedding: EmbeddingVectorJson) => new EmbeddingVector(embedding));
        this.eigenvalues = analysis.eigenvalues ?? null;
    }

    // #endregion

    // #region Public Properties

    /**
     * Gets or sets the name of the category to which the analysis belongs.
     */
    public accessor categoryName: string;

    /**
     * Gets or sets the human readable name of the category to which the analysis belongs.
     */
    public accessor humanReadableCategoryName: string;

    /**
     * Gets or sets the name of the clustering that was applied to the embedding.
     */
    public accessor clusteringName: string;

    /**
     * Gets or sets the name of the embedding method.
     */
    public accessor embeddingName: string;

    /**
     * Gets or sets the embedding.
     */
    public accessor embedding: EmbeddingVector[];

    /**
     * Gets or sets the eigen values of the analysis.
     */
    public accessor eigenvalues: number[] | null;

    // #endregion
}


/**
 * Represents an interface for the JSON objects that contain the information about an analysis and are retrieved from the REST API.
 */
export interface AnalysisJson {

    // #region Fields

    /**
     * Contains the name of the category to which the analysis belongs.
     */
    categoryName: string;

    /**
     * Contains the human readable name of the category to which the analysis belongs.
     */
    humanReadableCategoryName: string;

    /**
     * Contains the name of the clustering that was applied to the embedding.
     */
    clusteringName: string;

    /**
     * Contains the name of the embedding method.
     */
    embeddingName: string;

    /**
     * Contains the embedding.
     */
    embedding: EmbeddingVector[];

    /**
     * Contains the eigen values of the analysis.
     */
    eigenvalues: number[] | null;

    // #endregion
}
