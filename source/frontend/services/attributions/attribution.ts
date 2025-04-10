
import { ServiceException } from '@services/service-exception';

/**
 * Represents a single attribution.
 */
export class Attribution {

    // #region Constructor

    /**
     * Initializes a new Attribution instance.
     *
     * @param {AttributionJson} attribution The JSON object that was retrieved from the backend REST API.
     * @param {string} baseUrl The base URL that is added to the heatmap URLs.
     *
     * @throws {ServiceException} The attribution is <code>null</code> or <code>undefined</code>.
     */
    public constructor(attribution?: AttributionJson, baseUrl?: string) {

        if (!attribution) {
            throw new ServiceException('Attributions', { message: 'The attribution could not be loaded from the received JSON.'});
        }

        this.index = attribution.index;
        this.labels = attribution.labels;
        this.prediction = attribution.prediction;
        this.width = attribution.width;
        this.height = attribution.height;
        this.urls = attribution.urls;
        if (baseUrl) {
            for (const colorMap in this.urls) {
                if (Object.prototype.hasOwnProperty.call(this.urls, colorMap)) {
                    this.urls[colorMap] = baseUrl + this.urls[colorMap];
                }
            }
        }
    }

    // #endregion

    // #region Public Properties

    /**
     * Gets or sets the index of the attribution, which is the index of the dataset sample for which the attribution was created.
     */
    public accessor index: number;

    /**
     * Gets or sets the true labels of the dataset sample for which the attribution was generated.
     */
    public accessor labels: string | string[];

    /**
     * Gets a comma-separated list of all labels, which can be used for displaying the labels.
     *
     * @returns {string} Returns a string containing a comma-separated list of all labels.
     */
    public get labelDisplay(): string {
        if (Array.isArray(this.labels)) {
            return this.labels.join(', ');
        }
        return this.labels;
    }

    /**
     * Gets or sets the output of the model for the dataset sample for which the attribution was generated.
     */
    public accessor prediction: number[];

    /**
     * Gets or sets the width of the attribution heatmap image.
     */
    public accessor width: number;

    /**
     * Gets or sets the height of the attribution heatmap image.
     */
    public accessor height: number;

    /**
     * Gets the length of the shorter side of the attribution heatmap image.
     */
    public get shorterSide(): number {
        return Math.min(this.width, this.height);
    }

    /**
     * Gets or sets the URLs to the heatmaps for the attribution for all supported color maps.
     */
    public accessor urls: Record<string, string>;

    // #endregion
}

/**
 * Represents an interface for the JSON objects that contain the information about an attribution and are retrieved from the REST API.
 */
export interface AttributionJson {

    // #region Fields

    /**
     * Contains the index of the dataset sample for which the attribution was generated.
     */
    index: number;

    /**
     * Contains the true labels of the dataset sample for which the attribution was generated.
     */
    labels: string | string[];

    /**
     * Contains the output of the model for the dataset sample for which the attribution was generated.
     */
    prediction: number[];

    /**
     * Contains the width of the attribution heatmap image.
     */
    width: number;

    /**
     * Contains the height of the attribution heatmap image.
     */
    height: number;

    /**
     * Contains the URLs to the heatmaps for the attribution for all supported color maps.
     */
    urls: Record<string, string>;

    // #endregion
}
