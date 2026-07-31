import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./store/slices/authStore";
import Layout from "./components/Layout";
import LoginPage from "./pages/auth/LoginPage";
import DashboardPage from "./pages/doctor/DashboardPage";
import PatientsListPage from "./pages/doctor/PatientsListPage";
import ConsultationPage from "./pages/doctor/ConsultationPage";
import SurveillancePage from "./pages/doctor/SurveillancePage";

function Private({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Private><DashboardPage /></Private>} />
      <Route path="/patients" element={<Private><PatientsListPage /></Private>} />
      <Route path="/surveillance" element={<Private><SurveillancePage /></Private>} />
      <Route path="/consultation/:visitId" element={<Private><ConsultationPage /></Private>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
