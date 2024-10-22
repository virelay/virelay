
import { ServiceException } from '@services/service-exception';

/**
 * Represents a color map that can be used to render heatmaps.
 */
export class ColorMap {

    /**
     * Initializes a new ColorMap instance.
     * @param {ColorMapJson} colorMap The JSON object that was retrieved from the backend REST API.
     * @param {string} baseUrl The base URL that is added to the heatmap URLs.
     * @throws {ServiceException} The analysis category is <code>null</code> or <code>undefined</code>.
     */
    public constructor(colorMap?: ColorMapJson, baseUrl?: string) {

        if (!colorMap) {
            throw new ServiceException('Color Maps', { message: 'The color map could not be loaded from the received JSON.'});
        }

        this.name = colorMap.name;
        this.humanReadableName = colorMap.humanReadableName;
        this.url = colorMap.url;

        if (baseUrl) {
            this.url = baseUrl + this.url;
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

/**
 * Represents an interface for the JSON objects that contain the information about a color map and are retrieved from the REST API.
 */
export interface ColorMapJson {

    /**
     * Represents the internal name of the color map.
     */
    name: string;

    /**
     * Contains a human-readable version of the name of the color map.
     */
    humanReadableName: string;

    /**
     * Contains the URL for a preview image of the color map.
     */
    url: string;
}
