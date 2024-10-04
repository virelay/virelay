
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { ClarityModule } from '@clr/angular';
import { RouterModule } from '@angular/router';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { ProjectsService } from 'src/services/projects/projects.service';
import { ProjectsModule } from './modules/projects/projects.module';
import { AnalysesService } from 'src/services/analyses/analyses.service';
import { AttributionsService } from 'src/services/attributions/attributions.service';
import { DatasetService } from 'src/services/dataset/dataset.service';
import { ColorMapsService } from 'src/services/colorMaps/color-maps.service';
import { FormsModule } from '@angular/forms';

/**
 * Represents the app module, which is the main module of the application.
 */
@NgModule({
    declarations: [
        AppComponent
    ],
    imports: [
        BrowserModule,
        FormsModule,
        HttpClientModule,
        ClarityModule,
        BrowserAnimationsModule,
        ProjectsModule,
        RouterModule.forRoot([], { relativeLinkResolution: 'legacy' })
    ],
    providers: [
        ProjectsService,
        AnalysesService,
        AttributionsService,
        DatasetService,
        ColorMapsService
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }
