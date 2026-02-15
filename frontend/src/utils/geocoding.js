/**
 * Géocodage inverse via Nominatim (OpenStreetMap)
 * @param {number} lat
 * @param {number} lon
 * @returns {Promise<string>} Nom de la localité ou coordonnées en fallback
 */
export async function reverseGeocode(lat, lon) {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`,
      { headers: { "Accept-Language": "fr", "User-Agent": "SKAPA-Meteo/1.0" } }
    );
    if (!res.ok) return null;
    const data = await res.json();
    const addr = data.address || {};
    return (
      addr.city ||
      addr.town ||
      addr.village ||
      addr.municipality ||
      addr.county ||
      data.display_name?.split(",")[0] ||
      `${lat.toFixed(2)}, ${lon.toFixed(2)}`
    );
  } catch {
    return `${lat.toFixed(2)}, ${lon.toFixed(2)}`;
  }
}
