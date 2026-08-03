import patientClient from "./patientClient";

export interface PRemedy { name: string; potency?: string; dosage?: string; frequency?: string; duration?: string; }
export interface PPrescription {
  id: string; remedies: PRemedy[]; dietary_advice?: string; lifestyle_advice?: string;
  precautions?: string; created_at?: string;
}
export interface PNotification { type: string; message: string; at?: string | null; }
export interface PDashboard {
  patient_name: string; recovery_status: string; last_visit_at?: string | null;
  next_followup_at?: string | null; current_prescription?: PPrescription | null; notifications: PNotification[];
}
export interface PFollowUp {
  id: string; followup_type: string; scheduled_at: string; responded: boolean;
  outcome?: string | null; wellness?: number | null;
}
export interface PTimelineEvent { type: string; label: string; at: string | null; meta?: any; }

export const portalAuth = {
  login: (phone: string, access_code: string) =>
    patientClient.post<{ access_token: string }>("/auth/login", { phone, access_code }),
  me: () => patientClient.get<{ id: string; full_name: string; phone: string; gender: string; language_pref?: string }>("/me"),
};

export const portalApi = {
  dashboard: () => patientClient.get<PDashboard>("/dashboard"),
  prescriptions: () => patientClient.get<PPrescription[]>("/prescriptions"),
  timeline: () => patientClient.get<{ events: PTimelineEvent[] }>("/timeline"),
  followups: () => patientClient.get<PFollowUp[]>("/followups"),
  respond: (id: string, data: { status: string; wellness?: number; notes?: string }) =>
    patientClient.post<PFollowUp>(`/followups/${id}/respond`, data),
  pdfUrl: (id: string) => `/api/v1/portal/prescriptions/${id}/pdf`,
};
