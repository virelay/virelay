
/**
 * Represents a single category in an analysis. One category can contain many analyses for different attributions. The
 * category name is usually an umbrella term for all the attributions contained in the analysis. This is most-likely
 * a class name.
 */
export class AnalysisCategory {

    /**
     * Initializes a new AnalysisCategory instance.
     * @param analysisCategory The JSON object that was retrieved from the RESTful API.
     */
    public constructor(analysisCategory?: any) {
        if (analysisCategory) {
            this.name = analysisCategory.name;
            this.humanReadableName = analysisCategory.humanReadableName;
        }
    }

    /**
     * Contains the name of the category, which is usually a label index or a WordNet ID.
     */
    public name: string;

    /**
     * Contains a human-readable version of the category name, which is usually a label name.
     */
    public humanReadableName: string;
}
