import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Doctor } from "../../services/api/endpoints";

interface AuthState {
  isAuthenticated: boolean;
  doctor: Doctor | null;
  token: string | null;
  login: (doctor: Doctor, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      doctor: null,
      token: null,
      login: (doctor, token) => set({ isAuthenticated: true, doctor, token }),
      logout: () => set({ isAuthenticated: false, doctor: null, token: null }),
    }),
    { name: "homoeo-auth" }
  )
);
