
/**
 * The dimensions of the selection box that is used in the embedding visualizer to select embedding vectors.
 */
export class SelectionBox {

    // #region Constructor

    /**
     * Initializes a new instance of the SelectionBox class.
     *
     * @param {number} startX Contains the initial x-coordinate of the mouse position when the user starts drawing the selection box.
     * @param {number} startY Contains the initial y-coordinate of the mouse position when the user starts drawing the selection box.
     */
    public constructor(startX: number, startY: number) {
        this.startX = startX;
        this.x = startX;
        this.startY = startY;
        this.y = startY;
    }

    // #endregion

    // #region Private Fields

    /**
     * Contains the x-coordinate of the first corner of the selection box. Usually, this is the smaller x-coordinate, i.e., the left edge of the
     * selection box. But, the user may draw the selection all the way to the left, so that the second x-coordinate crosses the first x-coordinate and
     * becomes the smaller one.
     */
    private startX: number;

    /**
     * Contains the x-coordinate of the second corner of the selection box. Usually, this is the larger x-coordinate, i.e., the right edge of the
     * selection box. But, the user may draw the selection all the way to the right, so that the first x-coordinate crosses the second x-coordinate
     * and becomes the larger one.
     */
    private x: number;

    /**
     * Contains the y-coordinate of the first corner of the selection box. Usually, this is the smaller y-coordinate, i.e., the top edge of the
     * selection box. But, the user may draw the selection all the way to the top, so that the second y-coordinate crosses the first y-coordinate and
     * becomes the smaller one.
     */
    private startY: number;

    /**
     * Contains the y-coordinate of the second corner of the selection box. Usually, this is the larger y-coordinate, i.e., the bottom edge of the
     * selection box. But, the user may draw the selection all the way to the bottom, so that the first y-coordinate crosses the second y-coordinate
     * and becomes the larger one.
     */
    private y: number;

    // #endregion

    // #region Public Properties

    /**
     * Gets the x-coordinate of the left edge of the selection box.
     *
     * @returns {number} Returns the x-coordinate of the left edge of the selection box.
     */
    public get left(): number {
        return Math.min(this.startX, this.x);
    }

    /**
     * Gets the x-coordinate of the right edge of the selection box.
     *
     * @returns {number} Returns the x-coordinate of the right edge of the selection box.
     */
    public get right(): number {
        return Math.max(this.startX, this.x);
    }

    /**
     * Gets the y-coordinate of the top edge of the selection box.
     *
     * @returns {number} Returns the y-coordinate of the top edge of the selection box.
     */
    public get top(): number {
        return Math.min(this.startY, this.y);
    }

    /**
     * Gets the y-coordinate of the bottom edge of the selection box.
     *
     * @returns {number} Returns the y-coordinate of the bottom edge of the selection box.
     */
    public get bottom(): number {
        return Math.max(this.startY, this.y);
    }

    /**
     * Gets the width of the selection box.
     *
     * @returns {number} Returns the width of the selection box.
     */
    public get width(): number {
        return this.right - this.left;
    }

    /**
     * Gets the height of the selection box.
     *
     * @returns {number} Returns the height of the selection box.
     */
    public get height(): number {
        return this.bottom - this.top;
    }

    // #endregion

    // #region Public Methods

    /**
     * Updates the second corner of the selection box to the current mouse position.
     *
     * @param {number} x Contains the x-coordinate of the second corner of the selection box.
     * @param {number} y Contains the y-coordinate of the second corner of the selection box.
     */
    public update(x: number, y: number): void {
        this.x = x;
        this.y = y;
    }

    // #endregion
}
