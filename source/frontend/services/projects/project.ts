
import { AnalysisMethod, AnalysisMethodJson } from '@services/projects/analysis-method';
import { ServiceException } from '@services/service-exception';

/**
 * Represents a single project from the workspace.
 */
export class Project {

    // #region Constructor

    /**
     * Initializes a new Project instance.
     *
     * @param {ProjectJson} project The JSON object that was retrieved from the backend REST API.
     *
     * @throws {ServiceException} The project is <code>null</code> or <code>undefined</code>.
     */
    public constructor(project?: ProjectJson) {

        if (!project) {
            throw new ServiceException('Projects', { message: 'The project could not be loaded from the received JSON.'});
        }

        this.id = project.id;
        this.name = project.name;
        this.model = project.model;
        this.dataset = project.dataset;
        this.analysisMethods = project.analysisMethods?.map((analysisMethod: AnalysisMethodJson) => new AnalysisMethod(analysisMethod)) ?? [];
    }

    // #endregion

    // #region Public Properties

    /**
     * Gets or sets the ID of the project.
     */
    public accessor id: number;

    /**
     * Gets or sets the name of the project.
     */
    public accessor name: string;

    /**
     * Gets or sets the name of the machine learning model on which the project is based.
     */
    public accessor model: string;

    /**
     * Gets or sets the name of the dataset on which the model was trained.
     */
    public accessor dataset: string;

    /**
     * Gets or sets the analysis methods supported by the project.
     */
    public accessor analysisMethods: AnalysisMethod[];

    // #endregion
}

/**
 * Represents an interface for the JSON objects that contain the information about a project and are retrieved from the REST API.
 */
export interface ProjectJson {

    // #region Fields

    /**
     * Contains the ID of the project.
     */
    id: number;

    /**
     * Contains the name of the project.
     */
    name: string;

    /**
     * Contains the name of the machine learning model on which the project is based.
     */
    model: string;

    /**
     * Contains the name of the dataset on which the model was trained.
     */
    dataset: string;

    /**
     * Contains the analysis methods supported by the project.
     */
    analysisMethods?: AnalysisMethod[];

    // #endregion
}
