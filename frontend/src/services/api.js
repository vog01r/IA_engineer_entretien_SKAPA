/**
 * Service API pour le frontend SKAPA
 * Utilise VITE_API_URL et VITE_API_KEY (variables d'environnement)
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "";

const headers = {
  "Content-Type": "application/json",
  "X-API-Key": API_KEY,
};

async function handleResponse(response) {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Erreur ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export const weatherAPI = {
  async getAll() {
    const data = await fetch(`${BASE_URL}/weather/`, { headers }).then(handleResponse);
    return data.weather;
  },

  async fetchWeather(latitude, longitude) {
    const params = new URLSearchParams({ latitude, longitude });
    const data = await fetch(`${BASE_URL}/weather/fetch?${params}`, { headers }).then(
      handleResponse
    );
    return data;
  },

  async getByLocation(latitude, longitude) {
    const params = new URLSearchParams({ latitude, longitude });
    const data = await fetch(`${BASE_URL}/weather/location?${params}`, {
      headers,
    }).then(handleResponse);
    return data.weather;
  },
};

export const agentAPI = {
  async ask(question) {
    const data = await fetch(`${BASE_URL}/agent/ask`, {
      method: "POST",
      headers,
      body: JSON.stringify({ question }),
    }).then(handleResponse);
    return data;
  },
};
