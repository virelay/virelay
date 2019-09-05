
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

@NgModule({
    declarations: [
        AppComponent
    ],
    imports: [
        BrowserModule,
        HttpClientModule,
        ClarityModule,
        BrowserAnimationsModule,
        ProjectsModule,
        RouterModule.forRoot([])
    ],
    providers: [
        ProjectsService,
        AnalysesService,
        AttributionsService,
        DatasetService
    ],
  bootstrap: [AppComponent]
})
export class AppModule { }
