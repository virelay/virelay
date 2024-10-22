
export enum AttributionImageMode {

    /**
     * The image of the dataset sample corresponding to the attribution is retrieved.
     */
    Input = 'input',

    /**
     * The image of the dataset sample corresponding to the attribution is retrieved as black and white image with the heatmap of the attribution
     * superimposed onto it.
     */
    Overlay = 'overlay',

    /**
     * The heatmap of the attribution is retrieved.
     */
    Attribution = 'attribution'
}
