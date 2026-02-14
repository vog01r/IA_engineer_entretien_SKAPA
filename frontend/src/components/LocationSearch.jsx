import { useState } from "react";
import { weatherAPI } from "../services/api";

// Villes prédéfinies : nom → [lat, lon] (conforme à la consigne "lieu donné")
const VILLES = [
  { nom: "Paris", lat: 48.8566, lon: 2.3522 },
  { nom: "Lyon", lat: 45.764, lon: 4.8357 },
  { nom: "Marseille", lat: 43.2965, lon: 5.3698 },
  { nom: "Toulouse", lat: 43.6047, lon: 1.4442 },
  { nom: "Bordeaux", lat: 44.8378, lon: -0.5792 },
];

export default function LocationSearch() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [isError, setIsError] = useState(false);

  const fetchForCity = async (lat, lon, nom) => {
    setMessage(null);
    setLoading(true);
    setIsError(false);
    try {
      const data = await weatherAPI.fetchWeather(lat, lon);
      const summary = data.summary;
      const msg =
        summary?.current_temp != null && summary?.weather_label
          ? `${nom} : ${Math.round(summary.current_temp)}°C, ${summary.weather_label}. Prévisions enregistrées.`
          : `Prévisions pour ${nom} enregistrées.`;
      setMessage(msg);
      setIsError(false);
    } catch (err) {
      setMessage(err.message || "Erreur lors de la récupération de la météo.");
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800">Récupérer la météo</h2>
      <p className="text-sm text-gray-600 mb-4">
        Sélectionnez une ville pour récupérer les prévisions météo.
      </p>

      <div className="flex flex-wrap gap-2">
        {VILLES.map((ville) => (
          <button
            key={ville.nom}
            type="button"
            onClick={() => fetchForCity(ville.lat, ville.lon, ville.nom)}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-md transition-colors"
          >
            {ville.nom}
          </button>
        ))}
      </div>

      {message && (
        <div
          className={`mt-4 p-3 rounded ${
            isError ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"
          }`}
        >
          {message}
        </div>
      )}
    </div>
  );
}
