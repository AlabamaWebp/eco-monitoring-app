import { Routes } from '@angular/router';
import { MainLayoutComponent } from './layout/main-layout.component';
import { ChartsPageComponent } from './pages/charts-page.component';
import { DashboardPageComponent } from './pages/dashboard-page.component';
import { MeasurementsPageComponent } from './pages/measurements-page.component';
import { UploadPageComponent } from './pages/upload-page.component';

export const routes: Routes = [
  {
    path: '',
    component: MainLayoutComponent,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', component: DashboardPageComponent },
      { path: 'upload', component: UploadPageComponent },
      { path: 'measurements', component: MeasurementsPageComponent },
      { path: 'charts', component: ChartsPageComponent },
    ],
  },
];
