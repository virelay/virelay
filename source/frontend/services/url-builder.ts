
/**
 * A utility for building URLs.
 */
export class UrlBuilder {

    // #region Private Fields

    /**
     * Contains the base URL from which the URL is built.
     */
    private baseUrl: string | null = null;

    /**
     * Contains the path segments that are added to the URL.
     */
    private readonly pathSegments: string[] = [];

    /**
     * Contains the query parameters that are added to the URL.
     */
    private readonly queryParameters: QueryParameter[] = [];

    // #endregion

    // #region Public Static Methods

    /**
     * Creates a new instance of the UrlBuilder class.
     *
     * @param {string} baseUrl The base URL from which the URL is built.
     *
     * @returns {UrlBuilder} Returns a new instance of the UrlBuilder class.
     */
    public static for(baseUrl: string): UrlBuilder {
        const urlBuilder = new UrlBuilder();
        urlBuilder.baseUrl = baseUrl;
        return urlBuilder;
    }

    // #endregion

    // #region Public Methods

    /**
     * Adds the specified path segments to the URL.
     *
     * @param {Array<string>} pathSegments The path segments that are added to the URL.
     *
     * @returns {UrlBuilder} Returns the current instance of the UrlBuilder class so that additional method calls can be chained.
     */
    public withPath(... pathSegments: (string | number)[]): this {
        this.pathSegments.push(...pathSegments.map(pathSegment => pathSegment.toString()));
        return this;
    }

    /**
     * Adds the specified query parameter to the URL.
     *
     * @param {string} key The key of the query parameter.
     * @param {string | number | boolean} value The value of the query parameter.
     *
     * @returns {UrlBuilder} Returns the current instance of the UrlBuilder class so that additional method calls can be chained.
     */
    public withQueryParameter(key: string, value: string | number | boolean): this {
        this.queryParameters.push({ key, value });
        return this;
    }

    /**
     * Builds the URL from the specified base URL, path segments, and query parameters.
     *
     * @returns {string} Returns the URL that was built from the specified base URL, path segments, and query parameters.
     */
    public build(): string {

        let url = this.baseUrl ?? '';

        if (url.endsWith('/')) {
            url = url.substring(0, url.length - 1);
        }

        for (let pathSegment of this.pathSegments) {
            if (pathSegment.startsWith('/')) {
                pathSegment = pathSegment.substring(1);
            }
            if (pathSegment.endsWith('/')) {
                pathSegment = pathSegment.substring(0, pathSegment.length - 1);
            }
            url += '/' + pathSegment;
        }

        if (this.queryParameters.length > 0) {
            url += '?';
        }

        for (let index = 0; index < this.queryParameters.length; index++) {
            const queryParameter = this.queryParameters[index];
            url += `${queryParameter.key}=${encodeURIComponent(queryParameter.value)}`;
            if (index < this.queryParameters.length - 1) {
                url += '&';
            }
        }

        return url;
    }

    // #endregion
}

/**
 * Represents a query parameter.
 */
interface QueryParameter {

    // #region Fields

    /**
     * The key of the query parameter.
     */
    key: string;

    /**
     * The value of the query parameter.
     */
    value: string | number | boolean;

    // #endregion
}
