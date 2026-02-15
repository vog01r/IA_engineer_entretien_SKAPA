/**
 * Transformations des données météo (fonctions pures, testables).
 */

export function groupByCoords(data) {
  const groups = {};
  data.forEach((item) => {
    const key = `${item.latitude},${item.longitude}`;
    if (!groups[key])
      groups[key] = { key, latitude: item.latitude, longitude: item.longitude, forecasts: [] };
    groups[key].forecasts.push(item);
  });
  return Object.values(groups);
}

export function mergeLocationsByCity(locationsWithNames) {
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

export function buildDatesByLoc(locations) {
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
