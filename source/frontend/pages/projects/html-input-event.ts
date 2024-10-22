
/**
 * Represents the interface for the event that is triggered when the value of an input element changes.
 */
export interface HTMLInputEvent extends Event {

    // #region Fields

    /**
     * Contains the target of the event, which is the input element that triggered the event.
     */
    target: HTMLInputElement & EventTarget;

    // #endregion
}
