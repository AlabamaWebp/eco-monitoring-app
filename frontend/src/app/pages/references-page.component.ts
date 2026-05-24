import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { ApiService } from '../data/api.service';
import { MeasurementUnit, Polygon, SensorType } from '../data/api.models';

@Component({
  selector: 'app-references-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './references-page.component.html',
  styleUrl: './pages.shared.scss',
})
export class ReferencesPageComponent {
  polygons: Polygon[] = [];
  sensorTypes: SensorType[] = [];
  units: MeasurementUnit[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(private readonly api: ApiService) {
    this.loadReferences();
  }

  private loadReferences(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.api.getPolygons().subscribe({
      next: (data) => {
        this.polygons = data;
      },
      error: () => {
        this.errorMessage = 'Не удалось загрузить справочник полигонов.';
      },
    });

    this.api.getSensorTypes().subscribe({
      next: (data) => {
        this.sensorTypes = data;
      },
      error: () => {
        this.errorMessage = 'Не удалось загрузить справочник датчиков.';
      },
    });

    this.api.getMeasurementUnits().subscribe({
      next: (data) => {
        this.units = data;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Не удалось загрузить справочник единиц измерения.';
        this.isLoading = false;
      },
    });
  }
}
