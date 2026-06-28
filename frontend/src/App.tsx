import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./store/slices/authStore";
import DashboardPage        from "./pages/doctor/DashboardPage";
import ConsultationPage     from "./pages/doctor/ConsultationPage";
import PatientProfilePage   from "./pages/doctor/PatientProfilePage";
import PatientsListPage     from "./pages/doctor/PatientsListPage";
import AppointmentsPage     from "./pages/doctor/AppointmentsPage";
import AnalyticsPage        from "./pages/doctor/AnalyticsPage";
import KnowledgeBasePage    from "./pages/doctor/KnowledgeBasePage";
import PatientIntakePage    from "./pages/patient/PatientIntakePage";
import LoginPage            from "./pages/auth/LoginPage";
import RegisterPage         from "./pages/auth/RegisterPage";

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login"    element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/intake/:token" element={<PatientIntakePage />} />

      {/* Protected doctor routes */}
      <Route path="/" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
      <Route path="/patients"              element={<PrivateRoute><PatientsListPage /></PrivateRoute>} />
      <Route path="/patients/:id"          element={<PrivateRoute><PatientProfilePage /></PrivateRoute>} />
      <Route path="/consultation/:visitId" element={<PrivateRoute><ConsultationPage /></PrivateRoute>} />
      <Route path="/appointments"          element={<PrivateRoute><AppointmentsPage /></PrivateRoute>} />
      <Route path="/analytics"             element={<PrivateRoute><AnalyticsPage /></PrivateRoute>} />
      <Route path="/knowledge"             element={<PrivateRoute><KnowledgeBasePage /></PrivateRoute>} />
    </Routes>
  );
}
