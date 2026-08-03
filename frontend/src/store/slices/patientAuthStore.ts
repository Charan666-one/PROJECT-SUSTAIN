import { create } from "zustand";
import { persist } from "zustand/middleware";

interface PatientProfile { id: string; full_name: string; phone: string; gender: string; language_pref?: string; }

interface PatientAuthState {
  isAuthenticated: boolean;
  patient: PatientProfile | null;
  token: string | null;
  login: (patient: PatientProfile, token: string) => void;
  logout: () => void;
}

// Separate store + storage key so a patient session never collides with a doctor session.
export const usePatientAuthStore = create<PatientAuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      patient: null,
      token: null,
      login: (patient, token) => set({ isAuthenticated: true, patient, token }),
      logout: () => set({ isAuthenticated: false, patient: null, token: null }),
    }),
    { name: "sustain-patient-auth" }
  )
);
