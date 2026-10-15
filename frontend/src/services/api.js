import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api",
  timeout: 180000,
});

export async function getRegions() {
  const { data } = await api.get("/regions");
  return data.regions;
}

export async function analyzeHazards(payload) {
  const { data } = await api.post("/hazards/analyze", payload);
  return data;
}
