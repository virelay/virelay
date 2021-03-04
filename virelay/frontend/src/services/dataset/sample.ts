
/**
 * Represents a single sample from the dataset for which the analyses were performed.
 */
export class Sample {

    /**
     * Initializes a new Sample instance.
     * @param sample The JSON object that was retrieved from the RESTful API.
     * @param baseUrl The base URL that is added to the image URL.
     */
    public constructor(sample?: any, baseUrl?: string) {
        if (sample) {
            this.index = sample.index;
            this.labels = sample.labels;
            this.width = sample.width;
            this.height = sample.height;
            this.url = sample.url;
            if (baseUrl) {
                this.url = baseUrl + this.url;
            }
        }
    }

    /**
     * Contains the index of the dataset sample.
     */
    public index: number;

    /**
     * Contains the true labels of the dataset sample.
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
     * The width of the sample image.
     */
    public width: number;

    /**
     * The height of the sample image.
     */
    public height: number;

    /**
     * Contains the URL to the image of the dataset sample.
     */
    public url: string;
}
