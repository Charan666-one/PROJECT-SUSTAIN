import { create } from "zustand";

interface ConsultationState {
  currentVisitId: string | null;
  symptoms: any;
  recommendation: any;
  redFlags: any[];
  approved: boolean;
  setVisitId: (id: string) => void;
  setSymptoms: (s: any) => void;
  setRecommendation: (r: any) => void;
  setRedFlags: (f: any[]) => void;
  approve: () => void;
  reset: () => void;
}

export const useConsultationStore = create<ConsultationState>((set) => ({
  currentVisitId: null,
  symptoms: null,
  recommendation: null,
  redFlags: [],
  approved: false,
  setVisitId: (id) => set({ currentVisitId: id }),
  setSymptoms: (s) => set({ symptoms: s }),
  setRecommendation: (r) => set({ recommendation: r }),
  setRedFlags: (f) => set({ redFlags: f }),
  approve: () => set({ approved: true }),
  reset: () => set({ currentVisitId: null, symptoms: null, recommendation: null, redFlags: [], approved: false }),
}));
