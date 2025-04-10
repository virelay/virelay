
import { ServiceException } from '@services/service-exception';

/**
 * Represents a label of a dataset sample.
 */
export class Label {

    // #region Constructor

    /**
     * Initializes a new Label instance.
     *
     * @param {LabelJson} label The JSON object that was retrieved from the backend REST API.
     *
     * @throws {ServiceException} The label is <code>null</code> or <code>undefined</code>.
     */
    public constructor(label?: LabelJson) {

        if (!label) {
            throw new ServiceException('Datasets', { message: 'The dataset sample label could not be loaded from the received JSON.'});
        }

        this.index = label.index;
        this.wordNetId = label.wordNetId;
        this.name = label.name;
    }

    // #endregion

    // #region Public Properties

    /**
     * Gets or sets the index of the output neuron that corresponds to the label.
     */
    public accessor index: number;

    /**
     * Gets or sets the WordNet ID of the synset that describes the label (this is only necessary for some datasets like ImageNet).
     */
    public accessor wordNetId: string;

    /**
     * Gets or sets the human-readable name of the label.
     */
    public accessor name: string;

    // #endregion
}

/**
 * Represents an interface for the JSON objects that contain the information about a dataset sample label and are retrieved from the REST API.
 */
export interface LabelJson {

    // #region Fields

    /**
     * Contains the index of the output neuron that corresponds to the label.
     */
    index: number;

    /**
     * Contains the WordNet ID of the synset that describes the label (this is only necessary for some datasets like ImageNet).
     */
    wordNetId: string;

    /**
     * Contains the human-readable name of the label.
     */
    name: string;

    // #endregion
}
