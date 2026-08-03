import apiClient from "./client";

// ---- Types ----
export interface Doctor {
  id: string; full_name: string; email: string; clinic_name?: string;
  registration_no?: string; qualifications?: string[]; languages?: string[];
}
export interface Patient {
  id: string; full_name: string; date_of_birth: string; gender: string;
  phone: string; email?: string; language_pref?: string; consent_given?: boolean;
}
export interface Visit {
  id: string; patient_id: string; doctor_id: string; status: string;
  chief_complaint?: string; ai_confidence_score?: string; doctor_approved?: boolean;
}
export interface RedFlag { severity: string; message: string; matched: string[]; }
export interface EvidenceMateria { remedy?: string; source?: string; score?: number; snippet: string; matched_terms: string[]; }
export interface EvidenceCase { case_id?: string; remedy?: string; outcome?: string; score?: number; snippet: string; }
export interface EvidenceNote { doc_id?: string; title?: string; score?: number; snippet: string; }
export interface Evidence { materia_medica: EvidenceMateria[]; similar_cases: EvidenceCase[]; doctor_notes: EvidenceNote[]; }
export interface Recommendation {
  recommendation: string; red_flags: RedFlag[];
  sources: { materia_medica: string[]; similar_cases: string[]; doctor_notes: string[] };
  confidence: string; disclaimer: string; evidence?: Evidence;
}
export interface TimelineEvent { type: string; label: string; at: string | null; ref_id: string; meta?: any; }
export interface AuditEntry { id: string; event_type: string; label: string; patient_id?: string | null; visit_id?: string | null; payload: any; created_at: string; }
export interface Remedy {
  name: string; potency?: string; dosage?: string; frequency?: string; duration?: string;
}
export interface Prescription {
  id: string; visit_id: string; remedies: Remedy[]; dietary_advice?: string;
  precautions?: string; whatsapp_sent?: boolean;
}
export interface FollowUp {
  id: string; visit_id: string; patient_id: string; followup_type: string;
  scheduled_at: string; responded_at?: string; outcome: string; needs_escalation?: boolean;
}
export interface SurveillanceEpisode {
  visit_id: string; patient_id: string; patient_name: string; chief_complaint?: string;
  surveillance_status: string; trend: string; anomaly: string; severity: string;
  recovered: boolean; days_under_surveillance: number; latest_score?: number | null;
  recommended_action: string; suggest_re_evaluation: boolean; rationale: string;
  next_check_at?: string | null; doctor_in_loop: boolean;
}
export interface AnalyticsSummary {
  total_patients: number; total_visits: number; visits_last_30d: number;
  outcome_distribution: Record<string, number>; improvement_rate_pct: number | null;
  top_remedies: [string, number][]; pending_followups: number;
}

// ---- Auth ----
export const authApi = {
  register: (data: any) => apiClient.post<Doctor>("/auth/register", data),
  login: (email: string, password: string) =>
    apiClient.post<{ access_token: string }>("/auth/login-json", { email, password }),
  me: () => apiClient.get<Doctor>("/auth/me"),
};

// ---- Patients ----
export const patientApi = {
  list: (q = "") => apiClient.get<Patient[]>("/patients", { params: { q } }),
  create: (data: any) => apiClient.post<Patient>("/patients", data),
  get: (id: string) => apiClient.get<Patient>(`/patients/${id}`),
  timeline: (id: string) =>
    apiClient.get<{ patient: { id: string; full_name: string }; events: TimelineEvent[] }>(`/patients/${id}/timeline`),
  access: (id: string, regenerate = false) =>
    apiClient.get<{ phone: string; access_code: string; portal_url: string }>(`/patients/${id}/access`, { params: { regenerate } }),
};

// ---- Global search ----
export const searchApi = {
  query: (q: string) => apiClient.get<{
    query: string;
    patients: { id: string; full_name: string; phone: string }[];
    visits: { id: string; patient_id: string; chief_complaint?: string; status: string }[];
    prescriptions: { id: string; visit_id: string; remedies: string }[];
  }>("/search", { params: { q } }),
};

// ---- Audit / activity ----
export const auditApi = {
  list: (limit = 100) => apiClient.get<AuditEntry[]>("/audit", { params: { limit } }),
  verify: () => apiClient.get<{ ok: boolean; count: number; first_broken_index?: number }>("/audit/verify"),
};

// ---- Knowledge base ----
export const knowledgeApi = {
  addNote: (title: string, text: string) =>
    apiClient.post<{ doc_id: string; indexed: boolean }>("/knowledge/notes", { title, text }),
  status: () => apiClient.get<{ vector_backend: string; embeddings: string }>("/knowledge/status"),
};

// ---- Visits ----
export const visitApi = {
  create: (patient_id: string, chief_complaint = "") =>
    apiClient.post<Visit>("/visits", { patient_id, chief_complaint }),
  get: (id: string) => apiClient.get<Visit>(`/visits/${id}`),
};

// ---- Consultation ----
export const consultationApi = {
  clarify: (visitId: string, symptoms: any) =>
    apiClient.post<{ questions: string[] }>(`/consultations/${visitId}/clarify`, symptoms),
  recommend: (visitId: string, symptoms: any) =>
    apiClient.post<Recommendation>(`/consultations/${visitId}/recommend`, symptoms),
  reRecommend: (visitId: string, symptoms: any) =>
    apiClient.post<Recommendation>(`/consultations/${visitId}/re-recommend`, symptoms),
  approve: (visitId: string, approval: any) =>
    apiClient.post<Prescription>(`/consultations/${visitId}/approve`, approval),
};

// ---- Recovery surveillance ----
export const surveillanceApi = {
  list: (includeRecovered = false) =>
    apiClient.get<SurveillanceEpisode[]>("/surveillance", { params: { include_recovered: includeRecovered } }),
  close: (visitId: string) => apiClient.post<SurveillanceEpisode>(`/surveillance/${visitId}/close`),
};

// ---- Prescriptions ----
export const prescriptionApi = {
  pdfUrl: (id: string) => `/api/v1/prescriptions/${id}/pdf`,
  sendWhatsapp: (id: string) => apiClient.post<Prescription>(`/prescriptions/${id}/send-whatsapp`),
};

// ---- Follow-ups ----
export const followupApi = {
  list: (dueOnly = false) => apiClient.get<FollowUp[]>("/followups", { params: { due_only: dueOnly } }),
  respond: (id: string, data: any) => apiClient.post<FollowUp>(`/followups/${id}/respond`, data),
};

// ---- Analytics ----
export const analyticsApi = {
  summary: () => apiClient.get<AnalyticsSummary>("/analytics/summary"),
};
