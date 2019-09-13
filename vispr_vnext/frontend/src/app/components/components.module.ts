
import { NgModule } from '@angular/core';

import { BeforeAndAfterSliderComponent } from './before-and-after-slider/before-and-after-slider.component';

/**
 * Represents the module for application-wide components.
 */
@NgModule({
    declarations: [
        BeforeAndAfterSliderComponent
    ],
    exports: [
        BeforeAndAfterSliderComponent
    ]
})
export class ComponentsModule { }
