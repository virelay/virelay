
import { AnalysisMethod } from './analysis-method';

/**
 * Represents a single project from the workspace.
 */
export class Project {

    /**
     * Initializes a new Project instance.
     * @param project The JSON object that was retrieved from the RESTful API.
     */
    public constructor(project?: any) {
        if (project) {
            this.id = project.id;
            this.name = project.name;
            this.model = project.model;
            this.dataset = project.dataset;
            if (project.analysisMethods) {
                this.analysisMethods = project.analysisMethods.map(analysisMethod => new AnalysisMethod(analysisMethod));
            }
        }
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
