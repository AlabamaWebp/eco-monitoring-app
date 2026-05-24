import { CommonModule } from '@angular/common';
import { AfterViewInit, Component, ElementRef, OnDestroy, ViewChild } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ApiService } from '../data/api.service';
import { ChartResponse, Polygon, SensorType } from '../data/api.models';

type ChartMode = 'multiSensor' | 'multiPolygon';
type AggregationMode = 'raw' | 'hourly' | 'daily';
type PeriodMode = 'last_24h' | 'last_7d' | 'last_month' | 'custom';

@Component({
  selector: 'app-charts-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './charts-page.component.html',
  styleUrl: './pages.shared.scss',
})
export class ChartsPageComponent implements AfterViewInit, OnDestroy {
  @ViewChild('chartHost', { static: true }) chartHost!: ElementRef<HTMLDivElement>;

  polygons: Polygon[] = [];
  sensors: SensorType[] = [];
  mode: ChartMode = 'multiSensor';
  errorMessage = '';

  private echarts: any;
  private chartInstance: any;

  readonly multiSensorForm;
  readonly multiPolygonForm;

  constructor(
    private readonly fb: FormBuilder,
    private readonly api: ApiService,
  ) {
    this.multiSensorForm = this.fb.group({
      polygon_id: ['', Validators.required],
      sensor_type_ids: [<string[]>[], Validators.required],
      period: ['last_7d' as PeriodMode, Validators.required],
      date_from: [''],
      date_to: [''],
      aggregation: ['raw' as AggregationMode, Validators.required],
    });

    this.multiPolygonForm = this.fb.group({
      sensor_type_id: ['', Validators.required],
      polygon_ids: [<string[]>[], Validators.required],
      period: ['last_7d' as PeriodMode, Validators.required],
      date_from: [''],
      date_to: [''],
      aggregation: ['raw' as AggregationMode, Validators.required],
    });

    this.loadReferences();
  }

  async ngAfterViewInit(): Promise<void> {
    const module = await import('echarts');
    this.echarts = module;
    this.chartInstance = this.echarts.init(this.chartHost.nativeElement);
    this.renderEmptyState();
  }

  ngOnDestroy(): void {
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
  }

  setMode(mode: ChartMode): void {
    this.mode = mode;
    this.errorMessage = '';
    this.renderEmptyState();
  }

  buildMultiSensorChart(): void {
    const value = this.multiSensorForm.getRawValue();
    const sensorIds = value.sensor_type_ids ?? [];
    const period = value.period ?? undefined;
    if (!value.polygon_id || sensorIds.length === 0) {
      this.multiSensorForm.markAllAsTouched();
      return;
    }

    this.api
      .getMultiSensorChart({
        polygon_id: value.polygon_id,
        sensor_type_ids: sensorIds.join(','),
        period: period !== 'custom' ? period : undefined,
        date_from: period === 'custom' ? value.date_from || undefined : undefined,
        date_to: period === 'custom' ? value.date_to || undefined : undefined,
        aggregation: value.aggregation ?? 'raw',
      })
      .subscribe({
        next: (response) => this.renderChart(response),
        error: (error) => {
          this.errorMessage = error?.error?.detail ?? 'Не удалось построить график.';
        },
      });
  }

  buildMultiPolygonChart(): void {
    const value = this.multiPolygonForm.getRawValue();
    const polygonIds = value.polygon_ids ?? [];
    const period = value.period ?? undefined;
    if (!value.sensor_type_id || polygonIds.length === 0) {
      this.multiPolygonForm.markAllAsTouched();
      return;
    }

    this.api
      .getMultiPolygonChart({
        sensor_type_id: value.sensor_type_id,
        polygon_ids: polygonIds.join(','),
        period: period !== 'custom' ? period : undefined,
        date_from: period === 'custom' ? value.date_from || undefined : undefined,
        date_to: period === 'custom' ? value.date_to || undefined : undefined,
        aggregation: value.aggregation ?? 'raw',
      })
      .subscribe({
        next: (response) => this.renderChart(response),
        error: (error) => {
          this.errorMessage = error?.error?.detail ?? 'Не удалось построить график.';
        },
      });
  }

  private loadReferences(): void {
    this.api.getPolygons().subscribe((data) => (this.polygons = data));
    this.api.getSensorTypes().subscribe((data) => (this.sensors = data));
  }

  private renderChart(response: ChartResponse): void {
    if (!this.chartInstance) {
      return;
    }

    const option = {
      tooltip: {
        trigger: 'axis',
      },
      legend: {
        type: 'scroll',
      },
      grid: {
        left: 50,
        right: 20,
        top: 45,
        bottom: 70,
      },
      xAxis: {
        type: 'time',
        axisLabel: { color: '#475569' },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#475569' },
      },
      dataZoom: [
        { type: 'inside' },
        { type: 'slider', height: 24, bottom: 20 },
      ],
      series: response.series.map((series) => ({
        name: `${series.name} (${series.unit})`,
        type: 'line',
        showSymbol: false,
        smooth: false,
        data: series.data.map(([timestamp, value]) => [timestamp, value]),
      })),
    };
    this.chartInstance.setOption(option, true);
  }

  private renderEmptyState(): void {
    if (!this.chartInstance) {
      return;
    }
    this.chartInstance.setOption(
      {
        title: {
          text: 'Выберите параметры и нажмите "Построить график"',
          left: 'center',
          top: 'center',
          textStyle: { color: '#64748b', fontSize: 14, fontWeight: 'normal' },
        },
        xAxis: { show: false, type: 'time' },
        yAxis: { show: false, type: 'value' },
        series: [],
      },
      true,
    );
  }
}
