import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService } from '../data/api.service';
import { DashboardSummary } from '../data/api.models';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './pages.shared.scss',
})
export class DashboardPageComponent {
  summary: DashboardSummary | null = null;
  errorMessage = '';
  isLoading = true;

  constructor(private readonly api: ApiService) {
    this.loadSummary();
  }

  get cards(): { label: string; value: string }[] {
    if (!this.summary) {
      return [
        { label: 'Полигонов', value: '—' },
        { label: 'Типов датчиков', value: '—' },
        { label: 'Измерений', value: '—' },
        { label: 'CSV-загрузок', value: '—' },
      ];
    }

    return [
      { label: 'Полигонов', value: String(this.summary.polygons_count) },
      { label: 'Типов датчиков', value: String(this.summary.sensor_types_count) },
      { label: 'Измерений', value: String(this.summary.measurements_count) },
      { label: 'CSV-загрузок', value: String(this.summary.imports_count) },
    ];
  }

  private loadSummary(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.api.getDashboardSummary().subscribe({
      next: (data) => {
        this.summary = data;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Не удалось загрузить сводку Dashboard.';
        this.isLoading = false;
      },
    });
  }
}
