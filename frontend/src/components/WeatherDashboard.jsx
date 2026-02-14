import { useEffect, useState } from "react";
import { weatherAPI } from "../services/api";

export default function WeatherDashboard() {
  const [weather, setWeather] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchWeather() {
      try {
        setLoading(true);
        setError(null);
        const data = await weatherAPI.getAll();
        if (!cancelled) {
          setWeather(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Erreur lors du chargement des données météo");
          setWeather([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchWeather();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Données météo</h2>
        <p className="text-gray-600">Chargement...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Données météo</h2>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  // Regrouper par lieu (latitude, longitude)
  const groupByLocation = (data) => {
    const groups = {};
    data.forEach((item) => {
      const key = `${item.latitude},${item.longitude}`;
      if (!groups[key]) {
        groups[key] = {
          latitude: item.latitude,
          longitude: item.longitude,
          forecasts: [],
        };
      }
      groups[key].forecasts.push(item);
    });
    return Object.values(groups);
  };

  const locations = groupByLocation(weather);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Données météo</h2>

      {weather.length === 0 ? (
        <p className="text-gray-600">Aucune donnée météo stockée.</p>
      ) : (
        <div className="space-y-6">
          {locations.map((loc) => {
            const sortedForecasts = [...loc.forecasts].sort((a, b) =>
              (a.time || "").localeCompare(b.time || "")
            );
            const next24h = sortedForecasts.slice(0, 24);

            return (
              <div key={`${loc.latitude},${loc.longitude}`}>
                <h3 className="text-lg font-semibold mb-3 text-gray-700">
                  {loc.latitude}°, {loc.longitude}°
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                  {next24h.map((item) => (
                    <div
                      key={item.id ?? `${item.latitude}-${item.longitude}-${item.time}`}
                      className="bg-white border border-gray-200 rounded-lg shadow p-4 text-gray-800"
                    >
                      <div className="font-medium text-sm truncate" title={item.time}>
                        {item.time?.slice(0, 13) ?? "-"}
                      </div>
                      <div className="text-lg font-bold mt-1">
                        {item.temperature_2m != null
                          ? `${item.temperature_2m}°C`
                          : "-"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
