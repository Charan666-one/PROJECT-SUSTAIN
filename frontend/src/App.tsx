import { Suspense, lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./store/slices/authStore";
import { usePatientAuthStore } from "./store/slices/patientAuthStore";
import { Loading } from "./components/ui/State";
import DoctorShell from "./features/doctor/DoctorShell";
import LoginPage from "./features/auth/LoginPage";
import DashboardPage from "./features/doctor/DashboardPage";
import PatientsListPage from "./features/patients/PatientsListPage";
import PatientProfilePage from "./features/patients/PatientProfilePage";
import ConsultationPage from "./features/consultation/ConsultationPage";
import SurveillancePage from "./features/surveillance/SurveillancePage";
import FollowUpsPage from "./features/followups/FollowUpsPage";
import KnowledgeBasePage from "./features/knowledge/KnowledgeBasePage";
// Charts are heavy — load Analytics only when visited.
const AnalyticsPage = lazy(() => import("./features/analytics/AnalyticsPage"));
import AuditLogPage from "./features/audit/AuditLogPage";
import SettingsPage from "./features/settings/SettingsPage";
// Patient portal
import PatientShell from "./features/portal/PatientShell";
import PatientLoginPage from "./features/portal/PatientLoginPage";
import PatientDashboardPage from "./features/portal/PatientDashboardPage";
import PatientPrescriptionsPage from "./features/portal/PatientPrescriptionsPage";
import PatientCheckinsPage from "./features/portal/PatientCheckinsPage";
import PatientTimelinePage from "./features/portal/PatientTimelinePage";

function Doctor({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <DoctorShell>{children}</DoctorShell>;
}

function Patient({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = usePatientAuthStore();
  if (!isAuthenticated) return <Navigate to="/portal/login" replace />;
  return <PatientShell>{children}</PatientShell>;
}

export default function App() {
  return (
    <Routes>
      {/* Doctor portal */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Doctor><DashboardPage /></Doctor>} />
      <Route path="/patients" element={<Doctor><PatientsListPage /></Doctor>} />
      <Route path="/patients/:id" element={<Doctor><PatientProfilePage /></Doctor>} />
      <Route path="/consultation/:visitId" element={<Doctor><ConsultationPage /></Doctor>} />
      <Route path="/consultations" element={<Doctor><PatientsListPage /></Doctor>} />
      <Route path="/surveillance" element={<Doctor><SurveillancePage /></Doctor>} />
      <Route path="/followups" element={<Doctor><FollowUpsPage /></Doctor>} />
      <Route path="/knowledge" element={<Doctor><KnowledgeBasePage /></Doctor>} />
      <Route path="/analytics" element={<Doctor><Suspense fallback={<Loading />}><AnalyticsPage /></Suspense></Doctor>} />
      <Route path="/audit" element={<Doctor><AuditLogPage /></Doctor>} />
      <Route path="/settings" element={<Doctor><SettingsPage /></Doctor>} />

      {/* Patient portal */}
      <Route path="/portal/login" element={<PatientLoginPage />} />
      <Route path="/portal" element={<Patient><PatientDashboardPage /></Patient>} />
      <Route path="/portal/prescriptions" element={<Patient><PatientPrescriptionsPage /></Patient>} />
      <Route path="/portal/checkins" element={<Patient><PatientCheckinsPage /></Patient>} />
      <Route path="/portal/timeline" element={<Patient><PatientTimelinePage /></Patient>} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
