import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../data/api.service';
import { ImportItem, MeasurementItem, MeasurementListResponse, Polygon, SensorType } from '../data/api.models';

@Component({
  selector: 'app-measurements-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './measurements-page.component.html',
  styleUrl: './pages.shared.scss',
})
export class MeasurementsPageComponent {
  polygons: Polygon[] = [];
  sensorTypes: SensorType[] = [];
  imports: ImportItem[] = [];
  items: MeasurementItem[] = [];

  total = 0;
  limit = 50;
  offset = 0;
  isLoading = false;
  errorMessage = '';

  readonly form;

  constructor(
    private readonly fb: FormBuilder,
    private readonly api: ApiService,
  ) {
    this.form = this.fb.group({
      polygon_id: [''],
      sensor_type_id: [''],
      import_file_id: [''],
      date_from: [''],
      date_to: [''],
      sort_order: ['desc'],
    });
    this.bootstrap();
  }

  get pageNumber(): number {
    return Math.floor(this.offset / this.limit) + 1;
  }

  get totalPages(): number {
    return this.total > 0 ? Math.ceil(this.total / this.limit) : 1;
  }

  loadMeasurements(): void {
    this.isLoading = true;
    this.errorMessage = '';
    const values = this.form.getRawValue();
    this.api
      .getMeasurements({
        polygon_id: values.polygon_id || undefined,
        sensor_type_id: values.sensor_type_id || undefined,
        import_file_id: values.import_file_id || undefined,
        date_from: values.date_from || undefined,
        date_to: values.date_to || undefined,
        sort_order: values.sort_order || 'desc',
        limit: this.limit,
        offset: this.offset,
      })
      .subscribe({
        next: (response: MeasurementListResponse) => {
          this.items = response.items;
          this.total = response.total;
          this.isLoading = false;
        },
        error: (error) => {
          this.errorMessage = error?.error?.detail ?? 'Ошибка загрузки измерений.';
          this.isLoading = false;
        },
      });
  }

  applyFilters(): void {
    this.offset = 0;
    this.loadMeasurements();
  }

  resetFilters(): void {
    this.form.reset({
      polygon_id: '',
      sensor_type_id: '',
      import_file_id: '',
      date_from: '',
      date_to: '',
      sort_order: 'desc',
    });
    this.offset = 0;
    this.loadMeasurements();
  }

  prevPage(): void {
    if (this.offset === 0) {
      return;
    }
    this.offset = Math.max(0, this.offset - this.limit);
    this.loadMeasurements();
  }

  nextPage(): void {
    if (this.offset + this.limit >= this.total) {
      return;
    }
    this.offset += this.limit;
    this.loadMeasurements();
  }

  trackByMeasurement(_: number, item: MeasurementItem): number {
    return item.measurement_id;
  }

  private bootstrap(): void {
    this.api.getPolygons().subscribe((data) => (this.polygons = data));
    this.api.getSensorTypes().subscribe((data) => (this.sensorTypes = data));
    this.api.getImports().subscribe((data) => (this.imports = data));
    this.loadMeasurements();
  }
}
