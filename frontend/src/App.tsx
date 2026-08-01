import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./store/slices/authStore";
import DoctorShell from "./features/doctor/DoctorShell";
import LoginPage from "./features/auth/LoginPage";
import DashboardPage from "./features/doctor/DashboardPage";
import PatientsListPage from "./features/patients/PatientsListPage";
import PatientProfilePage from "./features/patients/PatientProfilePage";
import ConsultationPage from "./features/consultation/ConsultationPage";
import SurveillancePage from "./features/surveillance/SurveillancePage";
import FollowUpsPage from "./features/followups/FollowUpsPage";
import KnowledgeBasePage from "./features/knowledge/KnowledgeBasePage";
import AnalyticsPage from "./features/analytics/AnalyticsPage";
import AuditLogPage from "./features/audit/AuditLogPage";
import SettingsPage from "./features/settings/SettingsPage";

function Doctor({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <DoctorShell>{children}</DoctorShell>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Doctor><DashboardPage /></Doctor>} />
      <Route path="/patients" element={<Doctor><PatientsListPage /></Doctor>} />
      <Route path="/patients/:id" element={<Doctor><PatientProfilePage /></Doctor>} />
      <Route path="/consultation/:visitId" element={<Doctor><ConsultationPage /></Doctor>} />
      <Route path="/consultations" element={<Doctor><PatientsListPage /></Doctor>} />
      <Route path="/surveillance" element={<Doctor><SurveillancePage /></Doctor>} />
      <Route path="/followups" element={<Doctor><FollowUpsPage /></Doctor>} />
      <Route path="/knowledge" element={<Doctor><KnowledgeBasePage /></Doctor>} />
      <Route path="/analytics" element={<Doctor><AnalyticsPage /></Doctor>} />
      <Route path="/audit" element={<Doctor><AuditLogPage /></Doctor>} />
      <Route path="/settings" element={<Doctor><SettingsPage /></Doctor>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
