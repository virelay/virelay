
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
        RouterModule.forChild(projectRoutes)
    ],
    exports: [],
    providers: [
        ProjectsService,
        AnalysesService
    ]
})
export class ProjectsModule { }
