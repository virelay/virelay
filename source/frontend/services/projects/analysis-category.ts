
import { ServiceException } from '@services/service-exception';

/**
 * Represents a single category in an analysis. One category can contain many analyses for different attributions. The category name is usually an
 * umbrella term for all the attributions contained in the analysis. This is most-likely a class name.
 */
export class AnalysisCategory {

    // #region Constructor

    /**
     * Initializes a new AnalysisCategory instance.
     *
     * @param {AnalysisCategory} analysisCategory The JSON object that was retrieved from the backend REST API.
     *
     * @throws {ServiceException} The analysis category is <code>null</code> or <code>undefined</code>.
     */
    public constructor(analysisCategory?: AnalysisCategoryJson) {

        if (!analysisCategory) {
            throw new ServiceException('Projects', { message: 'The analysis category could not be loaded from the received JSON.'});
        }

        this.name = analysisCategory.name;
        this.humanReadableName = analysisCategory.humanReadableName;
    }

    // #endregion

    // #region Public Properties

    /**
     * Gets or sets the name of the category, which is usually a label index or a WordNet ID.
     */
    public accessor name: string;

    /**
     * Gets or sets a human-readable version of the category name, which is usually a label name.
     */
    public accessor humanReadableName: string;

    // #endregion
}

/**
 * Represents an interface for the JSON objects that contain the information about an analysis category and are retrieved from the REST API.
 */
export interface AnalysisCategoryJson {

    // #region Fields

    /**
     * Contains the name of the category, which is usually a label index or a WordNet ID.
     */
    name: string;

    /**
     * Contains a human-readable version of the category name, which is usually a label name.
     */
    humanReadableName: string;

    // #endregion
}
