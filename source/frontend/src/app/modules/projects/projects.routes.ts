
import { Routes } from '@angular/router';

import { IndexPage } from './pages/index/index.page';

/**
 * Defines the routes of the projects module.
 */
export const projectRoutes: Routes = [
    { path: 'projects/:id', component: IndexPage }
];
