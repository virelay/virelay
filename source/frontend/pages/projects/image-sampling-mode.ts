
export enum ImageSamplingMode {

    /**
     * The sampling mode for the dataset samples and the attributions is automatically determined based on the image size and the size of the image
     * element displaying the image.
     */
    Automatic = 'automatic',

    /**
     * The sampling mode for the dataset samples and the attributions is smooth, which means that an image sampling method such as bicubic or bilinear
     * interpolation is used.
     */
    Smooth = 'smooth',

    /**
     * The sampling mode for the dataset samples and the attributions is pixelated, which means that a nearest neighbor sampling method is used.
     */
    Pixelated = 'pixelated'
}
