
import { Label, LabelJson } from '@services/datasets/label';
import { ServiceException } from '@services/service-exception';

/**
 * Represents a single sample from the dataset for which the analyses were performed.
 */
export class Sample {

    // #region Constructor

    /**
     * Initializes a new Sample instance.
     *
     * @param {SampleJson} sample The JSON object that was retrieved from the backend REST API.
     * @param {string}  baseUrl The base URL that is added to the image URL.
     *
     * @throws {ServiceException} The sample is <code>null</code> or <code>undefined</code>.
     */
    public constructor(sample?: SampleJson, baseUrl?: string) {

        if (!sample) {
            throw new ServiceException('Datasets', { message: 'The dataset sample could not be loaded from the received JSON.'});
        }

        this.index = sample.index;
        this.labels = sample.labels.map(label => new Label(label));
        this.width = sample.width;
        this.height = sample.height;
        this.url = sample.url;
        if (baseUrl) {
            this.url = baseUrl + this.url;
        }
    }

    // #endregion

    // #region Public Properties

    /**
     * Gets or sets the index of the dataset sample.
     */
    public accessor index: number;

    /**
     * Gets or sets the true labels of the dataset sample.
     */
    public accessor labels: Label[];

    /**
     * Gets a comma-separated list of all labels, which can be used for displaying the labels.
     */
    public get labelDisplay(): string {
        if (this.labels.length === 0) {
            return '';
        }

        if (this.labels.length === 1) {
            return this.labels[0].name;
        }

        if (this.labels.length === 2) {
            return `${this.labels[0].name} and ${this.labels[1].name}`;
        }

        return this.labels
            .slice(0, this.labels.length - 1)
            .map(label => label.name)
            .join(', ')
            .concat(' and ', this.labels[this.labels.length - 1].name);
    }

    /**
     * Gets or sets the width of the sample image.
     */
    public accessor width: number;

    /**
     * Gets or sets the height of the sample image.
     */
    public accessor height: number;

    /**
     * Gets the length of the shorter side of the sample image.
     */
    public get shorterSide(): number {
        return Math.min(this.width, this.height);
    }

    /**
     * Gets or sets the URL to the image of the dataset sample.
     */
    public accessor url: string;

    // #endregion
}

/**
 * Represents an interface for the JSON objects that contain the information about a dataset sample and are retrieved from the REST API.
 */
export interface SampleJson {

    // #region Fields

    /**
     * Contains the index of the dataset sample.
     */
    index: number;

    /**
     * Contains the true labels of the dataset sample.
     */
    labels: LabelJson[];

    /**
     * Contains the width of the sample image.
     */
    width: number;

    /**
     * Contains the height of the sample image.
     */
    height: number;

    /**
     * Contains the URL to the image of the dataset sample.
     */
    url: string;

    // #endregion
}
