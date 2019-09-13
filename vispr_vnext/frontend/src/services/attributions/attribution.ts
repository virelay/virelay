import { Sample } from '../dataset/sample';

/**
 * Represents a single attribution.
 */
export class Attribution {

    /**
     * Initializes a new Attribution instance.
     * @param attribution The JSON object that was retrieved from the RESTful API.
     * @param baseUrl The base URL that is added to the heatmap URLs.
     */
    public constructor(attribution?: any, baseUrl?: string) {
        if (attribution) {
            this.index = attribution.index;
            this.labels = attribution.labels;
            this.prediction = attribution.prediction;
            this.width = attribution.width;
            this.height = attribution.height;
            this.url = attribution.url;
            this.urls = attribution.urls;
            if (baseUrl) {
                this.url = baseUrl + this.url;
                for (const colorMap in this.urls) {
                    if (this.urls.hasOwnProperty(colorMap)) {
                        this.urls[colorMap] = baseUrl + this.urls[colorMap];
                    }
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
     * Contains the URL to the heatmap for the attribution with a default color map.
     */
    public url: string;

    /**
     * Contains the URLs to the heatmaps for the attribution for all supported color maps.
     */
    public urls: { [colorMap: string]: string; };
}
