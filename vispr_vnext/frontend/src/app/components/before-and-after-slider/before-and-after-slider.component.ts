
import { Component, Input, ViewChild, ElementRef, AfterViewInit } from '@angular/core';

/**
 * Represents a slider, which shows a before and after image.
 */
@Component({
    selector: 'app-before-and-after-slider',
    styleUrls: ['before-and-after-slider.component.scss'],
    templateUrl: 'before-and-after-slider.component.html'
})
export class BeforeAndAfterSliderComponent implements AfterViewInit {

    /**
     * Contains a reference to the HTML element that represents the slider handle.
     */
    @ViewChild('sliderHandle', { static: false })
    public sliderHandle: ElementRef;

    /**
     * Contains a reference to the HTML element that represents the before image.
     */
    @ViewChild('beforeImage', { static: false })
    public beforeImage: ElementRef;

    /**
     * Contains a reference to the HTML element that represents the after image.
     */
    @ViewChild('afterImage', { static: false })
    public afterImage: ElementRef;

    /**
     * Contains the source of the before image.
     */
    @Input()
    public beforeImageSource: string;

    /**
     * Contains the source of the after image.
     */
    @Input()
    public afterImageSource: string;

    /**
     * Is invoked when the view of component was properly initialized.
     */
    public ngAfterViewInit(): void {
        const sliderHandle: HTMLDivElement = this.sliderHandle.nativeElement as HTMLDivElement;
        const beforeImage: HTMLImageElement = this.beforeImage.nativeElement as HTMLImageElement;

        const sliderHandleWidth = sliderHandle.getBoundingClientRect().width;
        const imageWidth = beforeImage.getBoundingClientRect().width;

        sliderHandle.style.left = `${imageWidth / 2 - sliderHandleWidth / 2}px`;
        beforeImage.style.clip = `rect(0px, ${imageWidth / 2}px, 999px, 0px)`;

        let isMouseDown = false;
        let sliderHandlePosition;
        sliderHandle.addEventListener('mousedown', event => {
            sliderHandlePosition = event.clientX;
            isMouseDown = true;
        });
        sliderHandle.addEventListener('mouseup', _ => isMouseDown = false);
        sliderHandle.addEventListener('mouseout', _ => isMouseDown = false);
        sliderHandle.addEventListener('mousemove', event => {
            if (isMouseDown) {
                sliderHandle.style.left = `${parseInt(sliderHandle.style.left, 10) + (event.clientX - sliderHandlePosition)}px`;
                sliderHandlePosition = event.clientX;
                beforeImage.style.clip = `rect(0px, ${sliderHandle.getBoundingClientRect().width / 2 + parseInt(sliderHandle.style.left, 10)}px, ${sliderHandle.getBoundingClientRect().height}px, 0px)`;
            }
        });
    }
}
