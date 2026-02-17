import { useState } from "react";
import { weatherAPI } from "../services/api";
import { geocode } from "../utils/geocoding";
import { CITIES } from "../constants/cities";

export default function LocationSearch({ onFetchSuccess }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [isError, setIsError] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

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
      onFetchSuccess?.();
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
        Choisissez une ville ou recherchez un lieu.
      </p>

      <form
        onSubmit={async (e) => {
          e.preventDefault();
          const q = searchQuery.trim();
          if (!q || loading) return;
          setMessage(null);
          setLoading(true);
          setIsError(false);
          try {
            const geo = await geocode(q);
            if (!geo) {
              setMessage(`Lieu « ${q} » introuvable.`);
              setIsError(true);
              return;
            }
            await fetchForCity(geo.lat, geo.lon, geo.label);
            setSearchQuery("");
          } catch (err) {
            setMessage(err.message || "Erreur lors de la recherche.");
            setIsError(true);
          } finally {
            setLoading(false);
          }
        }}
        className="flex gap-2 mb-4"
      >
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Ex: Louvain, Bruxelles, Tokyo…"
          className="flex-1 skapa-input px-3 py-2 text-sm"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !searchQuery.trim()}
          className="skapa-btn skapa-btn-primary px-4 py-2 text-sm"
        >
          Charger
        </button>
      </form>

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
