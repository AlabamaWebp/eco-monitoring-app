import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-measurements-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './measurements-page.component.html',
  styleUrl: './pages.shared.scss',
})
export class MeasurementsPageComponent {}

