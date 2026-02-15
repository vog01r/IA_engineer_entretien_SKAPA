import { useEffect, useState } from "react";
import { weatherAPI } from "../services/api";
import { reverseGeocode } from "../utils/geocoding";
import { groupByCoords, mergeLocationsByCity, buildDatesByLoc } from "../utils/weatherTransformers";

/**
 * Hook pour charger et structurer les données météo.
 * Gère : fetch, regroupement par coordonnées, géocodage inverse, fusion par ville.
 * @param {number} refreshTrigger - Incrémenter pour forcer un rechargement (ex: après fetch LocationSearch)
 * @returns {{ weather: array, locations: array, datesByLoc: object, loading: boolean, error: string|null }}
 */
export function useWeatherData(refreshTrigger = 0) {
  const [weather, setWeather] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [locationNames, setLocationNames] = useState({});

  useEffect(() => {
    let cancelled = false;
    async function fetchWeather() {
      try {
        setLoading(true);
        setError(null);
        const data = await weatherAPI.getAll();
        if (!cancelled) setWeather(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Erreur chargement");
          setWeather([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchWeather();
    return () => {
      cancelled = true;
    };
  }, [refreshTrigger]);

  const coordGroups = groupByCoords(weather);
  const coordKeys = coordGroups.map((g) => g.key).sort().join(",");

  useEffect(() => {
    if (coordGroups.length === 0) return;
    let cancelled = false;
    async function fetchNames() {
      const names = {};
      for (const loc of coordGroups) {
        if (cancelled) return;
        const nom = await reverseGeocode(loc.latitude, loc.longitude);
        if (!cancelled) names[loc.key] = nom;
        await new Promise((r) => setTimeout(r, 1100));
      }
      if (!cancelled) setLocationNames((prev) => ({ ...prev, ...names }));
    }
    fetchNames();
    return () => {
      cancelled = true;
    };
  }, [coordKeys]);

  const locationsWithNames = coordGroups.map((loc) => ({
    ...loc,
    nom: locationNames[loc.key] ?? `${loc.latitude.toFixed(2)}, ${loc.longitude.toFixed(2)}`,
  }));

  const locations = mergeLocationsByCity(locationsWithNames);
  const datesByLoc = buildDatesByLoc(locations);

  return { weather, locations, datesByLoc, loading, error };
}
