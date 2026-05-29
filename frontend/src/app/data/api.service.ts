import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import {
  ChartResponse,
  CsvImportResponse,
  DashboardSummary,
  ImportItem,
  MeasurementListResponse,
  MeasurementUnitWritePayload,
  MeasurementWritePayload,
  MeasurementWriteResponse,
  MeasurementUnit,
  PolygonWritePayload,
  Polygon,
  SensorTypeWritePayload,
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

  createPolygon(payload: PolygonWritePayload): Observable<Polygon> {
    return this.http.post<Polygon>(`${this.apiBase}/polygons`, payload);
  }

  updatePolygon(polygonId: number, payload: PolygonWritePayload): Observable<Polygon> {
    return this.http.put<Polygon>(`${this.apiBase}/polygons/${polygonId}`, payload);
  }

  deletePolygon(polygonId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiBase}/polygons/${polygonId}`);
  }

  getSensorTypes(): Observable<SensorType[]> {
    return this.http.get<SensorType[]>(`${this.apiBase}/sensor-types`);
  }

  createSensorType(payload: SensorTypeWritePayload): Observable<SensorType> {
    return this.http.post<SensorType>(`${this.apiBase}/sensor-types`, payload);
  }

  updateSensorType(sensorTypeId: number, payload: SensorTypeWritePayload): Observable<SensorType> {
    return this.http.put<SensorType>(`${this.apiBase}/sensor-types/${sensorTypeId}`, payload);
  }

  deleteSensorType(sensorTypeId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiBase}/sensor-types/${sensorTypeId}`);
  }

  getMeasurementUnits(): Observable<MeasurementUnit[]> {
    return this.http.get<MeasurementUnit[]>(`${this.apiBase}/measurement-units`);
  }

  createMeasurementUnit(payload: MeasurementUnitWritePayload): Observable<MeasurementUnit> {
    return this.http.post<MeasurementUnit>(`${this.apiBase}/measurement-units`, payload);
  }

  updateMeasurementUnit(unitId: number, payload: MeasurementUnitWritePayload): Observable<MeasurementUnit> {
    return this.http.put<MeasurementUnit>(`${this.apiBase}/measurement-units/${unitId}`, payload);
  }

  deleteMeasurementUnit(unitId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiBase}/measurement-units/${unitId}`);
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

  createMeasurement(payload: MeasurementWritePayload): Observable<MeasurementWriteResponse> {
    return this.http.post<MeasurementWriteResponse>(`${this.apiBase}/measurements`, payload);
  }

  updateMeasurement(measurementId: number, payload: MeasurementWritePayload): Observable<MeasurementWriteResponse> {
    return this.http.put<MeasurementWriteResponse>(`${this.apiBase}/measurements/${measurementId}`, payload);
  }

  deleteMeasurement(measurementId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiBase}/measurements/${measurementId}`);
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
