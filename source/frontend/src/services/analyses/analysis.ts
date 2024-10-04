
import { Embedding } from './embedding';

/**
 * Represents a single analysis.
 */
export class Analysis {

    /**
     * Initializes a new Analysis instance.
     * @param analysis The JSON object that was retrieved from the RESTful API.
     */
    public constructor(analysis?: any) {
        if (analysis) {
            this.categoryName = analysis.categoryName;
            this.humanReadableCategoryName = analysis.humanReadableCategoryName;
            this.clusteringName = analysis.clusteringName;
            this.embeddingName = analysis.embeddingName;
            if (analysis.embedding) {
                this.embedding = analysis.embedding.map(embedding => new Embedding(embedding));
            }
            this.eigenvalues = analysis.eigenvalues;
        }
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
