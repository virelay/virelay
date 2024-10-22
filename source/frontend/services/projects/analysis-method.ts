
import { AnalysisCategory } from '@services/projects/analysis-category';
import { ServiceException } from '@services/service-exception';

/**
 * Represents an analysis method.
 */
export class AnalysisMethod {

    // #region Constructor

    /**
     * Initializes a new AnalysisMethod instance.
     *
     * @param {AnalysisMethodJson} analysisMethod The JSON object that was retrieved from the backend REST API.
     *
     * @throws {ServiceException} The analysis category is <code>null</code> or <code>undefined</code>.
     */
    public constructor(analysisMethod?: AnalysisMethodJson) {

        if (!analysisMethod) {
            throw new ServiceException('Projects', { message: 'The analysis method could not be loaded from the received JSON.'});
        }

        this.name = analysisMethod.name;
        this.categories = analysisMethod.categories.map(category => new AnalysisCategory(category));
        this.clusterings = analysisMethod.clusterings;
        this.embeddings = analysisMethod.embeddings;
    }

    // #endregion

    // #region Public Properties

    /**
     * Gets or sets the name of the analysis method.
     */
    public accessor name: string;

    /**
     * Gets or sets the names of the categories that are in the analysis.
     */
    public accessor categories: AnalysisCategory[];

    /**
     * Gets or sets the names of the clusterings that are in the analysis.
     */
    public accessor clusterings: string[];

    /**
     * Gets or sets the names of the embeddings that are in the analysis.
     */
    public accessor embeddings: string[];

    // #endregion
}

/**
 * Represents an interface for the JSON objects that contain the information about an analysis method and are retrieved from the REST API.
 */
export interface AnalysisMethodJson {

    // #region Fields

    /**
     * Contains the name of the analysis method.
     */
    name: string;

    /**
     * Contains the names of the categories that are in the analysis.
     */
    categories: AnalysisCategory[];

    /**
     * Contains the names of the clusterings that are in the analysis.
     */
    clusterings: string[];

    /**
     * Contains the names of the embeddings that are in the analysis.
     */
    embeddings: string[];

    // #endregion
}
