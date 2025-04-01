
import { Component, Input } from "@angular/core";
import { ClarityModule } from "@clr/angular";

/**
 * A component that renders an error message. The error message is displayed in an alert box with red color.
 */
@Component({
    selector: 'virelay-error-message',
    templateUrl: 'error-message.component.html',
    styleUrl: 'error-message.component.scss',
    imports: [ClarityModule]
})
export class ErrorMessageComponent {

    // #region Public Properties

    /**
     * Gets or sets the heading of the error message.
     */
    @Input()
    public accessor heading: string | null = null;

    /**
     * Gets or sets the content of the message to display.
     */
    @Input()
    public accessor content: string | null = null;

    /**
     * Gets or sets a value that determines whether the error message is displayed inline, i.e., as a small box, or on the app-level, i.e., as a
     * full-width box at the top of the container. By default, the error message is displayed inline.
     */
    @Input()
    public accessor isInline: boolean = true;

    // #endregion
}
