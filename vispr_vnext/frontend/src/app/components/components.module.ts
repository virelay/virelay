
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { BeforeAndAfterSliderComponent } from './before-and-after-slider/before-and-after-slider.component';
import { EmbeddingVisualizerComponent } from './embedding-visualizer/embedding-visualizer.component';

/**
 * Represents the module for application-wide components.
 */
@NgModule({
    declarations: [
        BeforeAndAfterSliderComponent,
        EmbeddingVisualizerComponent
    ],
    imports: [
        FormsModule
    ],
    exports: [
        BeforeAndAfterSliderComponent,
        EmbeddingVisualizerComponent
    ]
})
export class ComponentsModule { }
