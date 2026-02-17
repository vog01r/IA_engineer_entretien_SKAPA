/**
 * Géocodage direct : nom de lieu → lat, lon
 * @param {string} query - Nom du lieu (ville, pays)
 * @returns {Promise<{lat: number, lon: number, label: string}|null>}
 */
export async function geocode(query) {
  const q = query?.trim();
  if (!q || q.length < 2) return null;
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=1`,
      { headers: { "Accept-Language": "fr", "User-Agent": "SKAPA-Meteo/1.0" } }
    );
    if (!res.ok) return null;
    const data = await res.json();
    const r = data[0];
    if (!r?.lat || !r?.lon) return null;
    const label = r.display_name?.split(",")[0] || q;
    return { lat: parseFloat(r.lat), lon: parseFloat(r.lon), label };
  } catch {
    return null;
  }
}

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
