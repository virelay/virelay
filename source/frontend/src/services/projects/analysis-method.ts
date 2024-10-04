
import { AnalysisCategory } from './analysis-category';

/**
 * Represents an analysis method.
 */
export class AnalysisMethod {

    /**
     * Initializes a new AnalysisMethod instance.
     * @param analysisMethod The JSON object that was retrieved from the RESTful API.
     */
    public constructor(analysisMethod?: any) {
        if (analysisMethod) {
            this.name = analysisMethod.name;
            if (analysisMethod.categories) {
                this.categories = analysisMethod.categories.map(category => new AnalysisCategory(category));
            }
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
    public categories: Array<AnalysisCategory>;

    /**
     * Contains the names of the clusterings that are in the analysis.
     */
    public clusterings: Array<string>;

    /**
     * Contains the names of the embeddings that are in the analysis.
     */
    public embeddings: Array<string>;
}
