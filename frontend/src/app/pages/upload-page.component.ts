import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../data/api.service';
import { CsvImportResponse, Polygon } from '../data/api.models';

@Component({
  selector: 'app-upload-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './upload-page.component.html',
  styleUrl: './pages.shared.scss',
})
export class UploadPageComponent {
  polygons: Polygon[] = [];
  selectedFile: File | null = null;
  uploadResult: CsvImportResponse | null = null;
  errorMessage = '';
  isSubmitting = false;

  readonly form;

  constructor(
    private readonly fb: FormBuilder,
    private readonly api: ApiService,
    private readonly router: Router,
  ) {
    this.form = this.fb.group({
      polygon_id: [null as number | null, Validators.required],
      collector_last_name: ['', [Validators.required, Validators.maxLength(255)]],
      collector_first_name: [''],
      collector_middle_name: [''],
    });

    this.loadPolygons();
  }

  get selectedFileName(): string {
    return this.selectedFile?.name ?? 'Файл не выбран';
  }

  onFileSelected(event: Event): void {
    this.errorMessage = '';
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;

    if (!file) {
      this.selectedFile = null;
      return;
    }
    if (!file.name.toLowerCase().endsWith('.csv')) {
      this.selectedFile = null;
      this.errorMessage = 'Выберите файл с расширением .csv.';
      input.value = '';
      return;
    }
    this.selectedFile = file;
  }

  submit(): void {
    this.errorMessage = '';
    this.uploadResult = null;

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    if (!this.selectedFile) {
      this.errorMessage = 'Выберите CSV-файл для загрузки.';
      return;
    }

    const values = this.form.getRawValue();
    const lastName = values.collector_last_name?.trim() ?? '';
    if (!lastName) {
      this.errorMessage = 'Фамилия загрузившего обязательна.';
      return;
    }

    const formData = new FormData();
    formData.append('file', this.selectedFile);
    formData.append('polygon_id', String(values.polygon_id));
    formData.append('collector_last_name', lastName);
    if (values.collector_first_name?.trim()) {
      formData.append('collector_first_name', values.collector_first_name.trim());
    }
    if (values.collector_middle_name?.trim()) {
      formData.append('collector_middle_name', values.collector_middle_name.trim());
    }

    this.isSubmitting = true;
    this.api.uploadCsv(formData).subscribe({
      next: (response) => {
        this.uploadResult = response;
        this.isSubmitting = false;
      },
      error: (error) => {
        this.errorMessage = error?.error?.detail ?? 'Ошибка загрузки CSV.';
        this.isSubmitting = false;
      },
    });
  }

  goToMeasurements(): void {
    this.router.navigate(['/measurements']);
  }

  goToCharts(): void {
    this.router.navigate(['/charts']);
  }

  private loadPolygons(): void {
    this.api.getPolygons().subscribe({
      next: (data) => {
        this.polygons = data;
      },
      error: () => {
        this.errorMessage = 'Не удалось загрузить список полигонов.';
      },
    });
  }
}
