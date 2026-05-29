export interface Polygon {
  polygon_id: number;
  name: string;
  location?: string | null;
  description?: string | null;
}

export interface SensorType {
  sensor_type_id: number;
  unit_id: number;
  name: string;
  code: string;
  description?: string | null;
  unit_symbol: string;
}

export interface MeasurementUnit {
  unit_id: number;
  name: string;
  symbol: string;
  description?: string | null;
}

export interface PolygonWritePayload {
  name: string;
  location?: string | null;
  description?: string | null;
}

export interface SensorTypeWritePayload {
  unit_id: number;
  name: string;
  code: string;
  description?: string | null;
}

export interface MeasurementUnitWritePayload {
  name: string;
  symbol: string;
  description?: string | null;
}

export interface CsvImportResponse {
  import_file_id: number;
  file_name: string;
  status: string;
  rows_count: number;
  measurements_count: number;
  skipped_values: number;
}

export interface ImportItem {
  import_file_id: number;
  file_name: string;
  polygon_name: string;
  collector_last_name: string;
  uploaded_at: string;
  rows_count: number;
  measurements_count: number;
  status: string;
  error_message?: string | null;
}

export interface MeasurementItem {
  measurement_id: number;
  measured_at: string;
  polygon_id: number;
  polygon_name: string;
  sensor_type_id: number;
  sensor_name: string;
  sensor_code: string;
  value: number | string;
  unit_symbol: string;
  import_file_id?: number | null;
  file_name?: string | null;
  collector_last_name?: string | null;
}

export interface MeasurementListResponse {
  items: MeasurementItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface MeasurementWritePayload {
  polygon_id: number;
  sensor_type_id: number;
  measured_at: string;
  value: number;
}

export interface MeasurementWriteResponse {
  measurement_id: number;
}

export interface ChartSeries {
  name: string;
  unit: string;
  data: [string, number][];
}

export interface ChartResponse {
  series: ChartSeries[];
}

export interface DashboardImportItem {
  import_file_id: number;
  file_name: string;
  polygon_name: string;
  collector_last_name: string;
  uploaded_at: string;
  status: string;
  rows_count: number;
  measurements_count: number;
}

export interface DashboardSummary {
  polygons_count: number;
  sensor_types_count: number;
  measurements_count: number;
  imports_count: number;
  latest_imports: DashboardImportItem[];
}
