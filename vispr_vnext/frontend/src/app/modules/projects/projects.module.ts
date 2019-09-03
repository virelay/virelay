
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';
import { ClarityModule } from '@clr/angular';

import { ProjectsService } from 'src/services/projects/projects.service';
import { projectRoutes } from './projects.routes';
import { IndexPage } from './pages/index/index.page';

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
        RouterModule.forChild(projectRoutes)
    ],
    exports: [],
    providers: [
        ProjectsService
    ]
})
export class ProjectsModule { }
