
import { AnalysisMethod } from '@services/projects/analysis-method';
import { ServiceException } from '@services/service-exception';

/**
 * Represents a single project from the workspace.
 */
export class Project {

    /**
     * Initializes a new Project instance.
     * @param {ProjectJson} project The JSON object that was retrieved from the backend REST API.
     */
    public constructor(project?: ProjectJson) {

        if (!project) {
            throw new ServiceException('Projects', { message: 'The project could not be loaded from the received JSON.'});
        }

        this.id = project.id;
        this.name = project.name;
        this.model = project.model;
        this.dataset = project.dataset;
        this.analysisMethods = project.analysisMethods?.map((analysisMethod: any) => new AnalysisMethod(analysisMethod)) ?? [];
    }

    /**
     * Contains the ID of the project.
     */
    public id: number;

    /**
     * Contains the name of the project.
     */
    public name: string;

    /**
     * Contains the name of the machine learning model on which the project is based.
     */
    public model: string;

    /**
     * Contains the name of the dataset on which the model was trained.
     */
    public dataset: string;

    /**
     * Contains the analysis methods supported by the project.
     */
    public analysisMethods: Array<AnalysisMethod>;
}

/**
 * Represents an interface for the JSON objects that contain the information about a project and are retrieved from the REST API.
 */
export interface ProjectJson {

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
    analysisMethods: Array<AnalysisMethod>;
}
