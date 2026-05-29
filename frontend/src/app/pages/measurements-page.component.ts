import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
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
  isSubmitting = false;
  errorMessage = '';
  successMessage = '';

  editingMeasurementId: number | null = null;
  editingImportFileId: number | null = null;

  readonly filterForm;
  readonly measurementForm;

  constructor(
    private readonly fb: FormBuilder,
    private readonly api: ApiService,
  ) {
    this.filterForm = this.fb.group({
      polygon_id: [''],
      sensor_type_id: [''],
      import_file_id: [''],
      date_from: [''],
      date_to: [''],
      sort_order: ['desc'],
    });

    this.measurementForm = this.fb.group({
      polygon_id: [null as number | null, [Validators.required]],
      sensor_type_id: [null as number | null, [Validators.required]],
      measured_at: ['', [Validators.required]],
      value: [null as number | null, [Validators.required]],
      collector_last_name: [''],
    });

    this.bootstrap();
  }

  get pageNumber(): number {
    return Math.floor(this.offset / this.limit) + 1;
  }

  get totalPages(): number {
    return this.total > 0 ? Math.ceil(this.total / this.limit) : 1;
  }

  get isEditMode(): boolean {
    return this.editingMeasurementId !== null;
  }

  get canEditCollectorLastName(): boolean {
    return this.isEditMode && this.editingImportFileId !== null;
  }

  loadMeasurements(): void {
    this.isLoading = true;
    this.errorMessage = '';
    const values = this.filterForm.getRawValue();

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
    this.filterForm.reset({
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

  startCreateMeasurement(): void {
    this.clearMessages();
    this.editingMeasurementId = null;
    this.editingImportFileId = null;
    this.measurementForm.reset({
      polygon_id: null,
      sensor_type_id: null,
      measured_at: '',
      value: null,
      collector_last_name: '',
    });
  }

  startEditMeasurement(item: MeasurementItem): void {
    this.clearMessages();
    this.editingMeasurementId = item.measurement_id;
    this.editingImportFileId = item.import_file_id ?? null;
    this.measurementForm.setValue({
      polygon_id: item.polygon_id,
      sensor_type_id: item.sensor_type_id,
      measured_at: this.toDateTimeLocal(item.measured_at),
      value: Number(item.value),
      collector_last_name: item.collector_last_name ?? '',
    });
  }

  cancelMeasurementEdit(): void {
    this.startCreateMeasurement();
  }

  saveMeasurement(): void {
    if (this.measurementForm.invalid) {
      this.measurementForm.markAllAsTouched();
      return;
    }

    this.clearMessages();
    this.isSubmitting = true;
    const raw = this.measurementForm.getRawValue();
    const payload = {
      polygon_id: Number(raw.polygon_id),
      sensor_type_id: Number(raw.sensor_type_id),
      measured_at: raw.measured_at ?? '',
      value: Number(raw.value),
      collector_last_name: undefined as string | undefined,
    };

    if (this.canEditCollectorLastName) {
      const normalizedLastName = (raw.collector_last_name ?? '').trim();
      if (!normalizedLastName) {
        this.errorMessage = 'Фамилия загрузившего обязательна для импортированного измерения.';
        this.isSubmitting = false;
        return;
      }
      payload.collector_last_name = normalizedLastName;
    }

    const request = this.editingMeasurementId
      ? this.api.updateMeasurement(this.editingMeasurementId, payload)
      : this.api.createMeasurement(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.editingMeasurementId ? 'Измерение обновлено.' : 'Измерение добавлено.';
        this.editingMeasurementId = null;
        this.editingImportFileId = null;
        this.measurementForm.reset({
          polygon_id: null,
          sensor_type_id: null,
          measured_at: '',
          value: null,
          collector_last_name: '',
        });
        this.isSubmitting = false;
        this.loadMeasurements();
      },
      error: (error) => {
        this.errorMessage = error?.error?.detail ?? 'Не удалось сохранить измерение.';
        this.isSubmitting = false;
      },
    });
  }

  deleteMeasurement(item: MeasurementItem): void {
    if (!window.confirm('Вы действительно хотите удалить это измерение?')) {
      return;
    }

    this.clearMessages();
    this.api.deleteMeasurement(item.measurement_id).subscribe({
      next: () => {
        this.successMessage = 'Измерение удалено.';
        this.reloadAfterDelete();
      },
      error: (error) => {
        this.errorMessage = error?.error?.detail ?? 'Не удалось удалить измерение.';
      },
    });
  }

  trackByMeasurement(_: number, item: MeasurementItem): number {
    return item.measurement_id;
  }

  private bootstrap(): void {
    this.api.getPolygons().subscribe((data) => (this.polygons = data));
    this.api.getSensorTypes().subscribe((data) => (this.sensorTypes = data));
    this.api.getImports().subscribe((data) => (this.imports = data));
    this.startCreateMeasurement();
    this.loadMeasurements();
  }

  private reloadAfterDelete(): void {
    this.isLoading = true;
    const values = this.filterForm.getRawValue();
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
        next: (response) => {
          if (this.offset > 0 && response.items.length === 0) {
            this.offset = Math.max(0, this.offset - this.limit);
            this.loadMeasurements();
            return;
          }
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

  private toDateTimeLocal(value: string): string {
    if (!value) {
      return '';
    }
    const normalized = value.includes('T') ? value : value.replace(' ', 'T');
    return normalized.slice(0, 16);
  }

  private clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }
}
