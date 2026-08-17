import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export function uploadDocument(formData) {
  return api.post("/documents/upload", formData);
}

export function getDocuments() {
  return api.get("/documents/");
}

export function searchDocuments(question) {
  return api.post("/search/", {
    question,
  });
}

export function getHealth() {
  return api.get("/system/health");
}

export function getMetrics() {
  return api.get("/system/metrics");
}
