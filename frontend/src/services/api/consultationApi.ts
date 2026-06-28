import apiClient from "./client";

export const consultationApi = {
  getRecommendation: (visitId: string, symptoms: any) =>
    apiClient.post(`/consultations/${visitId}/recommend`, symptoms),

  getClarifyingQuestions: (visitId: string, partialSymptoms: any) =>
    apiClient.post(`/consultations/${visitId}/clarify`, partialSymptoms),

  approveRecommendation: (visitId: string, prescription: any) =>
    apiClient.post(`/consultations/${visitId}/approve`, prescription),
};
