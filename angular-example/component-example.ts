import { Component, OnInit } from '@angular/core';
import { IncidentService, IncidentData } from './data.service';

@Component({
  selector: 'app-incident-manager',
  template: `
    <div class="container">
      <h2>Registrar Siniestro</h2>
      
      <div class="form-section">
        <h3>Información del Siniestro</h3>
        <div class="form-group">
          <label for="description">Descripción:</label>
          <textarea id="description" [(ngModel)]="incidentData.incident_info.description" class="form-control"></textarea>
        </div>
        
        <div class="form-group">
          <label for="damage_type">Tipo de Daño:</label>
          <select id="damage_type" [(ngModel)]="incidentData.incident_info.damage_type" class="form-control">
            <option value="Frontal">Frontal</option>
            <option value="Lateral">Lateral</option>
            <option value="Trasero">Trasero</option>
            <option value="Múltiple">Múltiple</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="severity">Severidad:</label>
          <select id="severity" [(ngModel)]="incidentData.incident_info.severity" class="form-control">
            <option value="Leve">Leve</option>
            <option value="Moderado">Moderado</option>
            <option value="Grave">Grave</option>
          </select>
        </div>
      </div>
      
      <div class="form-section">
        <h3>Información del Vehículo</h3>
        <div class="form-group">
          <label for="make">Marca:</label>
          <input type="text" id="make" [(ngModel)]="incidentData.vehicle_info.make" class="form-control">
        </div>
        
        <div class="form-group">
          <label for="model">Modelo:</label>
          <input type="text" id="model" [(ngModel)]="incidentData.vehicle_info.model" class="form-control">
        </div>
        
        <div class="form-group">
          <label for="year">Año:</label>
          <input type="text" id="year" [(ngModel)]="incidentData.vehicle_info.year" class="form-control">
        </div>
        
        <div class="form-group">
          <label for="plate">Matrícula:</label>
          <input type="text" id="plate" [(ngModel)]="incidentData.vehicle_info.plate" class="form-control">
        </div>
        
        <div class="form-group">
          <label for="color">Color:</label>
          <input type="text" id="color" [(ngModel)]="incidentData.vehicle_info.color" class="form-control">
        </div>
      </div>
      
      <div class="form-section">
        <h3>Información del Seguro</h3>
        <div class="form-group">
          <label for="policy_number">Número de Póliza:</label>
          <input type="text" id="policy_number" [(ngModel)]="incidentData.insurance_info.policy_number" class="form-control">
        </div>
        
        <div class="form-group">
          <label for="card_number">Número de Tarjeta:</label>
          <input type="text" id="card_number" [(ngModel)]="incidentData.insurance_info.card_number" class="form-control">
        </div>
        
        <div class="form-group">
          <label for="expiration_date">Fecha de Expiración:</label>
          <input type="text" id="expiration_date" [(ngModel)]="incidentData.insurance_info.expiration_date" class="form-control">
        </div>
        
        <div class="form-group">
          <label for="holder_name">Nombre del Titular:</label>
          <input type="text" id="holder_name" [(ngModel)]="incidentData.insurance_info.holder_name" class="form-control">
        </div>
      </div>
      
      <div class="form-section">
        <h3>Ubicación</h3>
        <div class="form-group">
          <label for="latitude">Latitud:</label>
          <input type="number" id="latitude" [(ngModel)]="incidentData.location.latitude" class="form-control">
        </div>
        
        <div class="form-group">
          <label for="longitude">Longitud:</label>
          <input type="number" id="longitude" [(ngModel)]="incidentData.location.longitude" class="form-control">
        </div>
        
        <div class="form-group">
          <label for="address">Dirección:</label>
          <input type="text" id="address" [(ngModel)]="incidentData.location.address" class="form-control">
        </div>
        
        <div class="form-group">
          <label for="reference">Punto de Referencia:</label>
          <input type="text" id="reference" [(ngModel)]="incidentData.location.reference" class="form-control">
        </div>
      </div>
      
      <button (click)="sendIncident()" class="btn btn-primary">Enviar Siniestro</button>
      
      <hr>
      
      <h2>Siniestros Registrados</h2>
      <button (click)="loadIncidents()" class="btn btn-info">Cargar Siniestros</button>
      
      <div *ngIf="incidents.length > 0" class="incidents-list">
        <div *ngFor="let incident of incidents" class="incident-item">
          <h3>Siniestro ID: {{ incident.incident_id }}</h3>
          <p><strong>Estado:</strong> {{ incident.status }}</p>
          <p><strong>Fecha:</strong> {{ incident.timestamp | date:'medium' }}</p>
          <p><strong>Vehículo:</strong> {{ incident.vehicle_info.make }} {{ incident.vehicle_info.model }} ({{ incident.vehicle_info.year }})</p>
          <p><strong>Descripción:</strong> {{ incident.incident_info.description }}</p>
          
          <div class="incident-actions">
            <button (click)="viewIncidentDetails(incident.incident_id)" class="btn btn-sm btn-info">Ver Detalles</button>
            <button (click)="updateStatus(incident.incident_id, 'processing')" class="btn btn-sm btn-warning">Procesar</button>
            <button (click)="updateStatus(incident.incident_id, 'completed')" class="btn btn-sm btn-success">Completar</button>
          </div>
        </div>
      </div>
      
      <div *ngIf="incidents.length === 0" class="no-incidents">
        No hay siniestros registrados
      </div>
      
      <hr>
      
      <h2>Notificaciones</h2>
      <button (click)="loadNotifications()" class="btn btn-info">Cargar Notificaciones</button>
      
      <div *ngIf="notifications.length > 0" class="notifications-list">
        <div *ngFor="let notification of notifications" class="notification-item">
          <p><strong>{{ notification.timestamp | date:'medium' }}:</strong> {{ notification.message }}</p>
        </div>
      </div>
      
      <div *ngIf="notifications.length === 0" class="no-notifications">
        No hay notificaciones recientes
      </div>
    </div>
  `,
  styles: [`
    .container { max-width: 800px; margin: 0 auto; padding: 20px; }
    .form-section { margin-bottom: 20px; border: 1px solid #eee; padding: 15px; border-radius: 5px; }
    .form-group { margin-bottom: 15px; }
    .form-control { width: 100%; padding: 8px; }
    .btn { padding: 8px 16px; margin-right: 10px; cursor: pointer; }
    .incidents-list, .notifications-list { margin-top: 20px; }
    .incident-item { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
    .notification-item { padding: 10px; border-bottom: 1px solid #eee; }
    .no-incidents, .no-notifications { margin-top: 20px; color: #888; }
    .incident-actions { margin-top: 10px; }
    .btn-sm { padding: 5px 10px; font-size: 12px; }
  `]
})
export class IncidentManagerComponent implements OnInit {
  incidentData: IncidentData = {
    incident_info: {
      description: '',
      date: new Date().toISOString(),
      damage_type: 'Frontal',
      severity: 'Leve'
    },
    vehicle_info: {
      make: '',
      model: '',
      year: '',
      plate: '',
      color: ''
    },
    insurance_info: {
      policy_number: '',
      card_number: '',
      expiration_date: '',
      holder_name: ''
    },
    location: {
      latitude: 0,
      longitude: 0,
      address: '',
      reference: ''
    },
    images: []
  };
  
  incidents: any[] = [];
  notifications: any[] = [];
  selectedIncidentId: string | null = null;
  
  constructor(private incidentService: IncidentService) { }
  
  ngOnInit(): void {
    this.loadIncidents();
    this.loadNotifications();
    
    // En una aplicación real, podrías configurar un intervalo para verificar notificaciones
    setInterval(() => this.loadNotifications(), 30000);
  }
  
  sendIncident(): void {
    // Actualizar la fecha
    this.incidentData.incident_info.date = new Date().toISOString();
    
    this.incidentService.sendIncidentData(this.incidentData).subscribe(
      response => {
        console.log('Siniestro enviado correctamente', response);
        // Recargar la lista de siniestros
        this.loadIncidents();
        // Limpiar el formulario
        this.resetForm();
      },
      error => {
        console.error('Error al enviar siniestro', error);
      }
    );
  }
  
  loadIncidents(): void {
    this.incidentService.getAllIncidents().subscribe(
      response => {
        if (response.success) {
          this.incidents = response.incidents;
        }
      },
      error => {
        console.error('Error al cargar siniestros', error);
      }
    );
  }
  
  viewIncidentDetails(incidentId: string): void {
    this.selectedIncidentId = incidentId;
    this.incidentService.getIncidentById(incidentId).subscribe(
      response => {
        if (response.success) {
          console.log('Detalles del siniestro:', response.incident);
          // Aquí podrías mostrar los detalles en un modal o en otra vista
        }
      },
      error => {
        console.error('Error al obtener detalles del siniestro', error);
      }
    );
  }
  
  updateStatus(incidentId: string, status: string): void {
    this.incidentService.updateIncidentStatus(incidentId, status).subscribe(
      response => {
        console.log('Estado del siniestro actualizado', response);
        // Recargar la lista de siniestros
        this.loadIncidents();
        // Recargar notificaciones
        this.loadNotifications();
      },
      error => {
        console.error('Error al actualizar estado del siniestro', error);
      }
    );
  }
  
  loadNotifications(): void {
    this.incidentService.getNotifications().subscribe(
      response => {
        if (response.success) {
          this.notifications = response.notifications;
        }
      },
      error => {
        console.error('Error al cargar notificaciones', error);
      }
    );
  }
  
  resetForm(): void {
    this.incidentData = {
      incident_info: {
        description: '',
        date: new Date().toISOString(),
        damage_type: 'Frontal',
        severity: 'Leve'
      },
      vehicle_info: {
        make: '',
        model: '',
        year: '',
        plate: '',
        color: ''
      },
      insurance_info: {
        policy_number: '',
        card_number: '',
        expiration_date: '',
        holder_name: ''
      },
      location: {
        latitude: 0,
        longitude: 0,
        address: '',
        reference: ''
      },
      images: []
    };
  }
} 