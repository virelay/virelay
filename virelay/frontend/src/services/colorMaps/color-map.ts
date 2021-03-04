
/**
 * Represents a color map that can be used to render heatmaps.
 */
export class ColorMap {

    /**
     * Initializes a new ColorMap instance.
     * @param colorMap The JSON object that was retrieved from the RESTful API.
     * @param baseUrl The base URL that is added to the heatmap URLs.
     */
    public constructor(colorMap?: any, baseUrl?: string) {
        if (colorMap) {
            this.name = colorMap.name;
            this.humanReadableName = colorMap.humanReadableName;
            this.url = colorMap.url;

            if (baseUrl) {
                this.url = baseUrl + this.url;
            }
        }
    }

    /**
     * Represents the internal name of the color map.
     */
    public name: string;

    /**
     * Contains a human-readable version of the name of the color map.
     */
    public humanReadableName: string;

    /**
     * Contains the URL for a preview image of the color map.
     */
    public url: string;
}
