import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.scss',
})
export class MainLayoutComponent {
  navItems = [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Загрузка CSV', path: '/upload' },
    { label: 'Измерения', path: '/measurements' },
    { label: 'Графики', path: '/charts' },
  ];
}

