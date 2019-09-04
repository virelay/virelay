
/**
 * Represents an analysis method.
 */
export class AnalysisMethod {

    /**
     * Initializes a new AnalysisMethod instance.
     * @param analysisMethod The JSON object that was retrieved from the RESTful API.
     */
    constructor(analysisMethod?: any) {
        if (analysisMethod) {
            this.name = analysisMethod.name;
            this.categories = analysisMethod.categories;
            this.clusterings = analysisMethod.clusterings;
            this.embeddings = analysisMethod.embeddings;
        }
    }

    /**
     * Contains the name of the analysis method.
     */
    public name: string;

    /**
     * Contains the names of the categories that are in the analysis.
     */
    public categories: Array<string>;

    /**
     * Contains the names of the clusterings that are in the analysis.
     */
    public clusterings: Array<string>;

    /**
     * Contains the names of the embeddings that are in the analysis.
     */
    public embeddings: Array<string>;
}
