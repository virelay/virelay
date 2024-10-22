
import { Routes } from '@angular/router';

import { ProjectPageComponent } from '@pages/projects/project-page.component';

/**
 * Contains the routes for the components of the AppModule.
 */
export const routes: Routes = [
    { path: 'projects/:id', component: ProjectPageComponent }
];
