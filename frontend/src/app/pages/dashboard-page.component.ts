import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './pages.shared.scss',
})
export class DashboardPageComponent {
  cards = [
    { label: 'Полигонов', value: '3' },
    { label: 'Типов датчиков', value: '6' },
    { label: 'Записей измерений', value: '0' },
    { label: 'Последних импортов', value: '0' },
  ];
}

