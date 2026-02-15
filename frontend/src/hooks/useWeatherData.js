import { useEffect, useState } from "react";
import { weatherAPI } from "../services/api";
import { reverseGeocode } from "../utils/geocoding";

function groupByCoords(data) {
  const groups = {};
  data.forEach((item) => {
    const key = `${item.latitude},${item.longitude}`;
    if (!groups[key])
      groups[key] = { key, latitude: item.latitude, longitude: item.longitude, forecasts: [] };
    groups[key].forecasts.push(item);
  });
  return Object.values(groups);
}

function mergeLocationsByCity(locationsWithNames) {
  const locationsByCity = {};
  locationsWithNames.forEach((loc) => {
    const nom = loc.nom;
    if (!locationsByCity[nom]) locationsByCity[nom] = { key: nom, nom, forecasts: [] };
    locationsByCity[nom].forecasts.push(...loc.forecasts);
  });
  Object.keys(locationsByCity).forEach((nom) => {
    const seen = new Set();
    locationsByCity[nom].forecasts = locationsByCity[nom].forecasts.filter((f) => {
      if (seen.has(f.time)) return false;
      seen.add(f.time);
      return true;
    });
  });
  return Object.values(locationsByCity);
}

function buildDatesByLoc(locations) {
  const datesByLoc = {};
  locations.forEach((loc) => {
    const days = new Set();
    loc.forecasts.forEach((f) => {
      const day = f.time?.slice(0, 10);
      if (day) days.add(day);
    });
    datesByLoc[loc.key] = [...days].sort();
  });
  return datesByLoc;
}

/**
 * Hook pour charger et structurer les données météo.
 * Gère : fetch, regroupement par coordonnées, géocodage inverse, fusion par ville.
 * @returns {{ weather: array, locations: array, datesByLoc: object, loading: boolean, error: string|null }}
 */
export function useWeatherData() {
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
  }, []);

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
