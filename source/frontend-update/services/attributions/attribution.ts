
import { ServiceException } from '@services/service-exception';

/**
 * Represents a single attribution.
 */
export class Attribution {

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
                if (this.urls.hasOwnProperty(colorMap)) {
                    this.urls[colorMap] = baseUrl + this.urls[colorMap];
                }
            }
        }
    }

    /**
     * Contains the index of the dataset sample for which the attribution was generated.
     */
    public index: number;

    /**
     * Contains the true labels of the dataset sample for which the attribution was generated.
     */
    public labels: string | Array<string>;

    /**
     * Gets a comma-separated list of all labels, which can be used for displaying the labels.
     *
     * @returns Returns a string containing a comma-separated list of all labels.
     */
    public get labelDisplay(): string {
        if (Array.isArray(this.labels)) {
            return this.labels.join(', ');
        }
        return this.labels;
    }

    /**
     * Contains the output of the model for the dataset sample for which the attribution was generated.
     */
    public prediction: Array<number>;

    /**
     * The width of the attribution heatmap image.
     */
    public width: number;

    /**
     * The height of the attribution heatmap image.
     */
    public height: number;

    /**
     * Contains the URLs to the heatmaps for the attribution for all supported color maps.
     */
    public urls: { [colorMap: string]: string; };
}

/**
 * Represents an interface for the JSON objects that contain the information about an attribution and are retrieved from the REST API.
 */
export interface AttributionJson {

    /**
     * Contains the index of the dataset sample for which the attribution was generated.
     */
    index: number;

    /**
     * Contains the true labels of the dataset sample for which the attribution was generated.
     */
    labels: string | Array<string>;

    /**
     * Contains the output of the model for the dataset sample for which the attribution was generated.
     */
    prediction: Array<number>;

    /**
     * The width of the attribution heatmap image.
     */
    width: number;

    /**
     * The height of the attribution heatmap image.
     */
    height: number;

    /**
     * Contains the URLs to the heatmaps for the attribution for all supported color maps.
     */
    urls: { [colorMap: string]: string; };
}
