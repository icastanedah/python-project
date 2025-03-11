import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface IncidentData {
  incident_info: {
    description: string;
    date: string;
    damage_type: string;
    severity: string;
  };
  vehicle_info: {
    make: string;
    model: string;
    year: string;
    plate: string;
    color: string;
  };
  insurance_info?: {
    policy_number: string;
    card_number: string;
    expiration_date: string;
    holder_name: string;
  };
  location: {
    latitude: number;
    longitude: number;
    address: string;
    reference?: string;
  };
  images?: Array<{
    url: string;
    type: string;
    analysis_results?: any;
  }>;
}

@Injectable({
  providedIn: 'root'
})
export class IncidentService {
  private apiUrl = 'http://localhost:8081/api/angular';

  constructor(private http: HttpClient) { }

  /**
   * Envía datos de un siniestro a la API de Flask
   */
  sendIncidentData(incidentData: IncidentData): Observable<any> {
    return this.http.post(`${this.apiUrl}/receive`, incidentData);
  }

  /**
   * Obtiene todos los siniestros almacenados
   */
  getAllIncidents(): Observable<any> {
    return this.http.get(`${this.apiUrl}/incidents`);
  }

  /**
   * Obtiene un siniestro específico por su ID
   */
  getIncidentById(incidentId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/incidents/${incidentId}`);
  }

  /**
   * Actualiza el estado de un siniestro
   */
  updateIncidentStatus(incidentId: string, status: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/incidents/${incidentId}/status`, { status });
  }

  /**
   * Obtiene notificaciones de siniestros recientes
   */
  getNotifications(): Observable<any> {
    return this.http.get(`${this.apiUrl}/notifications`);
  }
} 