/**
 * DashboardPage — clinic overview for the doctor
 * Shows: today appointments, recent patients, outcome stats, clinic analytics
 */
import AppointmentsWidget   from "../../components/dashboard/AppointmentsWidget";
import OutcomeStatsWidget   from "../../components/dashboard/OutcomeStatsWidget";
import RecentPatientsWidget from "../../components/dashboard/RecentPatientsWidget";
import ClinicAnalyticsWidget from "../../components/dashboard/ClinicAnalyticsWidget";

export default function DashboardPage() {
  return (
    <div className="dashboard-grid">
      <AppointmentsWidget />
      <RecentPatientsWidget />
      <OutcomeStatsWidget />
      <ClinicAnalyticsWidget />
    </div>
  );
}
