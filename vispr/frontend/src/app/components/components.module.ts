
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { EmbeddingVisualizerComponent } from './embedding-visualizer/embedding-visualizer.component';

/**
 * Represents the module for application-wide components.
 */
@NgModule({
    declarations: [
        EmbeddingVisualizerComponent
    ],
    imports: [
        FormsModule
    ],
    exports: [
        EmbeddingVisualizerComponent
    ]
})
export class ComponentsModule { }
