
/**
 * Represents a single embedding.
 */
export class Embedding {

    /**
     * Initializes a new Embedding instance.
     * @param embedding The JSON object that was retrieved from the RESTful service.
     */
    public constructor(embedding?: any) {
        if (embedding) {
            this.cluster = embedding.cluster;
            this.attributionIndex = embedding.attributionIndex;
            this.value = embedding.value;
        }
    }

    /**
     * Contains the index of the cluster to which the embedding belongs.
     */
    public cluster: number;

    /**
     * Contains the index of the attribution of the embedding.
     */
    public attributionIndex: number;

    /**
     * Contains the value of the embedding.
     */
    public value: Array<number>;
}
