import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import {
  ChartResponse,
  CsvImportResponse,
  DashboardSummary,
  ImportItem,
  MeasurementListResponse,
  MeasurementUnit,
  Polygon,
  SensorType,
} from './api.models';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly apiBase = 'http://localhost:8000/api';

  constructor(private readonly http: HttpClient) {}

  getPolygons(): Observable<Polygon[]> {
    return this.http.get<Polygon[]>(`${this.apiBase}/polygons`);
  }

  getSensorTypes(): Observable<SensorType[]> {
    return this.http.get<SensorType[]>(`${this.apiBase}/sensor-types`);
  }

  getMeasurementUnits(): Observable<MeasurementUnit[]> {
    return this.http.get<MeasurementUnit[]>(`${this.apiBase}/measurement-units`);
  }

  uploadCsv(formData: FormData): Observable<CsvImportResponse> {
    return this.http.post<CsvImportResponse>(`${this.apiBase}/imports/csv`, formData);
  }

  getImports(filters?: Record<string, string | number | undefined>): Observable<ImportItem[]> {
    let params = new HttpParams();
    if (filters) {
      for (const [key, value] of Object.entries(filters)) {
        if (value !== undefined && value !== null && value !== '') {
          params = params.set(key, String(value));
        }
      }
    }
    return this.http.get<ImportItem[]>(`${this.apiBase}/imports`, { params });
  }

  getMeasurements(filters: Record<string, string | number | undefined>): Observable<MeasurementListResponse> {
    let params = new HttpParams();
    for (const [key, value] of Object.entries(filters)) {
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, String(value));
      }
    }
    return this.http.get<MeasurementListResponse>(`${this.apiBase}/measurements`, { params });
  }

  getMultiSensorChart(filters: Record<string, string | number | undefined>): Observable<ChartResponse> {
    let params = new HttpParams();
    for (const [key, value] of Object.entries(filters)) {
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, String(value));
      }
    }
    return this.http.get<ChartResponse>(`${this.apiBase}/charts/multi-sensor`, { params });
  }

  getMultiPolygonChart(filters: Record<string, string | number | undefined>): Observable<ChartResponse> {
    let params = new HttpParams();
    for (const [key, value] of Object.entries(filters)) {
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, String(value));
      }
    }
    return this.http.get<ChartResponse>(`${this.apiBase}/charts/multi-polygon`, { params });
  }

  getDashboardSummary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(`${this.apiBase}/dashboard/summary`);
  }
}

