import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { ApiService } from '../data/api.service';
import { MeasurementUnit, Polygon, SensorType } from '../data/api.models';

type ReferenceTab = 'polygons' | 'sensorTypes' | 'units';

@Component({
  selector: 'app-references-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './references-page.component.html',
  styleUrl: './pages.shared.scss',
})
export class ReferencesPageComponent {
  polygons: Polygon[] = [];
  sensorTypes: SensorType[] = [];
  units: MeasurementUnit[] = [];

  activeTab: ReferenceTab = 'polygons';
  isLoading = false;
  isSubmitting = false;
  errorMessage = '';
  successMessage = '';

  editingPolygonId: number | null = null;
  editingSensorTypeId: number | null = null;
  editingUnitId: number | null = null;

  readonly polygonForm;
  readonly sensorTypeForm;
  readonly unitForm;

  constructor(
    private readonly fb: FormBuilder,
    private readonly api: ApiService,
  ) {
    this.polygonForm = this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(255)]],
      location: ['', [Validators.maxLength(255)]],
      description: [''],
    });

    this.sensorTypeForm = this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(255)]],
      code: ['', [Validators.required, Validators.maxLength(100)]],
      unit_id: [null as number | null, [Validators.required]],
      description: [''],
    });

    this.unitForm = this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(255)]],
      symbol: ['', [Validators.required, Validators.maxLength(50)]],
      description: [''],
    });

    this.loadReferences();
  }

  setTab(tab: ReferenceTab): void {
    this.activeTab = tab;
    this.clearMessages();
  }

  startCreatePolygon(): void {
    this.clearMessages();
    this.editingPolygonId = null;
    this.polygonForm.reset({ name: '', location: '', description: '' });
  }

  startEditPolygon(item: Polygon): void {
    this.clearMessages();
    this.editingPolygonId = item.polygon_id;
    this.polygonForm.setValue({
      name: item.name,
      location: item.location ?? '',
      description: item.description ?? '',
    });
  }

  savePolygon(): void {
    if (this.polygonForm.invalid) {
      this.polygonForm.markAllAsTouched();
      return;
    }
    this.isSubmitting = true;
    this.clearMessages();
    const raw = this.polygonForm.getRawValue();
    const payload = {
      name: (raw.name ?? '').trim(),
      location: this.normalizeOptional(raw.location),
      description: this.normalizeOptional(raw.description),
    };

    const request = this.editingPolygonId
      ? this.api.updatePolygon(this.editingPolygonId, payload)
      : this.api.createPolygon(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.editingPolygonId ? 'Полигон обновлен.' : 'Полигон создан.';
        this.editingPolygonId = null;
        this.polygonForm.reset({ name: '', location: '', description: '' });
        this.loadReferences();
        this.isSubmitting = false;
      },
      error: (error) => {
        this.errorMessage = error?.error?.detail ?? 'Не удалось сохранить полигон.';
        this.isSubmitting = false;
      },
    });
  }

  deletePolygon(item: Polygon): void {
    if (!window.confirm('Вы действительно хотите удалить эту запись?')) {
      return;
    }
    this.clearMessages();
    this.api.deletePolygon(item.polygon_id).subscribe({
      next: () => {
        this.successMessage = 'Полигон удален.';
        this.loadReferences();
      },
      error: (error) => {
        this.errorMessage =
          error?.error?.detail ?? 'Невозможно удалить полигон, так как с ним связаны измерения или загруженные файлы.';
      },
    });
  }

  startCreateSensorType(): void {
    this.clearMessages();
    this.editingSensorTypeId = null;
    this.sensorTypeForm.reset({ name: '', code: '', unit_id: null, description: '' });
  }

  startEditSensorType(item: SensorType): void {
    this.clearMessages();
    this.editingSensorTypeId = item.sensor_type_id;
    this.sensorTypeForm.setValue({
      name: item.name,
      code: item.code,
      unit_id: item.unit_id,
      description: item.description ?? '',
    });
  }

  saveSensorType(): void {
    if (this.sensorTypeForm.invalid) {
      this.sensorTypeForm.markAllAsTouched();
      return;
    }
    this.isSubmitting = true;
    this.clearMessages();
    const raw = this.sensorTypeForm.getRawValue();
    const payload = {
      name: (raw.name ?? '').trim(),
      code: (raw.code ?? '').trim(),
      unit_id: Number(raw.unit_id),
      description: this.normalizeOptional(raw.description),
    };

    const request = this.editingSensorTypeId
      ? this.api.updateSensorType(this.editingSensorTypeId, payload)
      : this.api.createSensorType(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.editingSensorTypeId ? 'Тип датчика обновлен.' : 'Тип датчика создан.';
        this.editingSensorTypeId = null;
        this.sensorTypeForm.reset({ name: '', code: '', unit_id: null, description: '' });
        this.loadReferences();
        this.isSubmitting = false;
      },
      error: (error) => {
        this.errorMessage = error?.error?.detail ?? 'Не удалось сохранить тип датчика.';
        this.isSubmitting = false;
      },
    });
  }

  deleteSensorType(item: SensorType): void {
    if (!window.confirm('Вы действительно хотите удалить эту запись?')) {
      return;
    }
    this.clearMessages();
    this.api.deleteSensorType(item.sensor_type_id).subscribe({
      next: () => {
        this.successMessage = 'Тип датчика удален.';
        this.loadReferences();
      },
      error: (error) => {
        this.errorMessage =
          error?.error?.detail ?? 'Невозможно удалить тип датчика, так как для него существуют измерения.';
      },
    });
  }

  startCreateUnit(): void {
    this.clearMessages();
    this.editingUnitId = null;
    this.unitForm.reset({ name: '', symbol: '', description: '' });
  }

  startEditUnit(item: MeasurementUnit): void {
    this.clearMessages();
    this.editingUnitId = item.unit_id;
    this.unitForm.setValue({
      name: item.name,
      symbol: item.symbol,
      description: item.description ?? '',
    });
  }

  saveUnit(): void {
    if (this.unitForm.invalid) {
      this.unitForm.markAllAsTouched();
      return;
    }
    this.isSubmitting = true;
    this.clearMessages();
    const raw = this.unitForm.getRawValue();
    const payload = {
      name: (raw.name ?? '').trim(),
      symbol: (raw.symbol ?? '').trim(),
      description: this.normalizeOptional(raw.description),
    };

    const request = this.editingUnitId ? this.api.updateMeasurementUnit(this.editingUnitId, payload) : this.api.createMeasurementUnit(payload);

    request.subscribe({
      next: () => {
        this.successMessage = this.editingUnitId ? 'Единица измерения обновлена.' : 'Единица измерения создана.';
        this.editingUnitId = null;
        this.unitForm.reset({ name: '', symbol: '', description: '' });
        this.loadReferences();
        this.isSubmitting = false;
      },
      error: (error) => {
        this.errorMessage = error?.error?.detail ?? 'Не удалось сохранить единицу измерения.';
        this.isSubmitting = false;
      },
    });
  }

  deleteUnit(item: MeasurementUnit): void {
    if (!window.confirm('Вы действительно хотите удалить эту запись?')) {
      return;
    }
    this.clearMessages();
    this.api.deleteMeasurementUnit(item.unit_id).subscribe({
      next: () => {
        this.successMessage = 'Единица измерения удалена.';
        this.loadReferences();
      },
      error: (error) => {
        this.errorMessage =
          error?.error?.detail ??
          'Невозможно удалить единицу измерения, так как она используется в типах датчиков или измерениях.';
      },
    });
  }

  private loadReferences(): void {
    this.isLoading = true;
    forkJoin({
      polygons: this.api.getPolygons(),
      sensorTypes: this.api.getSensorTypes(),
      units: this.api.getMeasurementUnits(),
    }).subscribe({
      next: (result) => {
        this.polygons = result.polygons;
        this.sensorTypes = result.sensorTypes;
        this.units = result.units;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Не удалось загрузить справочники.';
        this.isLoading = false;
      },
    });
  }

  private normalizeOptional(value: string | null): string | null {
    const normalized = (value ?? '').trim();
    return normalized || null;
  }

  private clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }
}
