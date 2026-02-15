import { useState } from "react";
import { weatherAPI } from "../services/api";
import { CITIES } from "../constants/cities";

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
    <div>
      <h2 className="text-base font-semibold mb-1" style={{ color: "var(--color-text)" }}>
        Charger des prévisions
      </h2>
      <p className="text-sm mb-4" style={{ color: "var(--color-muted)" }}>
        Choisissez une ville pour enregistrer sa météo.
      </p>

      <div className="flex flex-wrap gap-2">
        {CITIES.map((ville) => (
          <button
            key={ville.nom}
            type="button"
            onClick={() => fetchForCity(ville.lat, ville.lon, ville.nom)}
            disabled={loading}
            className="skapa-btn skapa-btn-primary px-4 py-2 text-sm"
          >
            {ville.nom}
          </button>
        ))}
      </div>

      {message && (
        <div
          className="mt-4 px-3 py-2.5 rounded-lg text-sm"
          style={{
            background: isError ? "var(--color-error-bg)" : "var(--color-success-bg)",
            color: isError ? "var(--color-error)" : "var(--color-success)",
          }}
        >
          {message}
        </div>
      )}
    </div>
  );
}
