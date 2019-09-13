
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';
import { ClarityModule } from '@clr/angular';
import * as PlotlyJS from 'plotly.js/dist/plotly.js';
import { PlotlyModule } from 'angular-plotly.js';
import { FormsModule } from '@angular/forms';

import { ProjectsService } from 'src/services/projects/projects.service';
import { projectRoutes } from './projects.routes';
import { IndexPage } from './pages/index/index.page';
import { AnalysesService } from 'src/services/analyses/analyses.service';
import { AttributionsService } from 'src/services/attributions/attributions.service';
import { DatasetService } from 'src/services/dataset/dataset.service';
import { ComponentsModule } from 'src/app/components/components.module';
import { ColorMapsService } from 'src/services/colorMaps/color-maps.service';

PlotlyModule.plotlyjs = PlotlyJS;

/**
 * Represents the module that contains the project pages.
 */
@NgModule({
    declarations: [
        IndexPage
    ],
    imports: [
        BrowserModule,
        ClarityModule,
        PlotlyModule,
        FormsModule,
        ComponentsModule,
        RouterModule.forChild(projectRoutes)
    ],
    exports: [],
    providers: [
        ProjectsService,
        AnalysesService,
        AttributionsService,
        DatasetService,
        ColorMapsService
    ]
})
export class ProjectsModule { }
