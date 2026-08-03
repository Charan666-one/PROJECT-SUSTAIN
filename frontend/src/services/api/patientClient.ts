import axios from "axios";
import { usePatientAuthStore } from "../../store/slices/patientAuthStore";

const patientClient = axios.create({ baseURL: "/api/v1/portal" });

patientClient.interceptors.request.use((config) => {
  const token = usePatientAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

patientClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) usePatientAuthStore.getState().logout();
    return Promise.reject(err);
  }
);

export default patientClient;
