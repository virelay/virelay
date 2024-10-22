
import { Embedding } from '@services/analyses/embedding';
import { ServiceException } from '@services/service-exception';

/**
 * Represents a single analysis.
 */
export class Analysis {

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
        this.embedding = analysis.embedding?.map((embedding: any) => new Embedding(embedding)) ?? [];
        this.eigenvalues = analysis.eigenvalues;
    }

    /**
     * Contains the name of the category to which the analysis belongs.
     */
    public categoryName: string;

    /**
     * Contains the human readable name of the category to which the analysis belongs.
     */
    public humanReadableCategoryName: string;

    /**
     * Contains the name of the clustering that was applied to the embedding.
     */
    public clusteringName: string;

    /**
     * Contains the name of the embedding method.
     */
    public embeddingName: string;

    /**
     * Contains the embedding.
     */
    public embedding: Array<Embedding>;

    /**
     * Contains the eigen values of the analysis.
     */
    public eigenvalues?: Array<number>;
}


/**
 * Represents an interface for the JSON objects that contain the information about an analysis and are retrieved from the REST API.
 */
export interface AnalysisJson {

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
    embedding: Array<Embedding>;

    /**
     * Contains the eigen values of the analysis.
     */
    eigenvalues?: Array<number>;
}
