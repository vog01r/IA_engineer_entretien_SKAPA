import { useState } from "react";
import { useWeatherData } from "../hooks/useWeatherData";
import { formatHeure, formatDateLabel } from "../utils/formatters";

export default function WeatherDashboard() {
  const { weather, locations, datesByLoc, loading, error } = useWeatherData();
  const [selectedLoc, setSelectedLoc] = useState("");
  const [selectedDate, setSelectedDate] = useState("");

  const selectedLocData = locations.find((l) => l.key === selectedLoc);
  const datesForLoc = selectedLoc ? (datesByLoc[selectedLoc] ?? []) : [];
  const selectedDateData =
    selectedDate && selectedLocData
      ? selectedLocData.forecasts
          .filter((f) => f.time?.slice(0, 10) === selectedDate)
          .sort((a, b) => (a.time || "").localeCompare(b.time || ""))
      : [];

  const handleLocChange = (e) => {
    const key = e.target.value;
    setSelectedLoc(key);
    setSelectedDate("");
    if (key && datesByLoc[key]?.length > 0) setSelectedDate(datesByLoc[key][0]);
  };

  const handleDateChange = (e) => setSelectedDate(e.target.value);

  if (loading) {
    return (
      <div>
        <h2 className="text-base font-semibold mb-1" style={{ color: "var(--color-text)" }}>
          Prévisions
        </h2>
        <p className="text-sm" style={{ color: "var(--color-muted)" }}>
          Chargement…
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h2 className="text-base font-semibold mb-1" style={{ color: "var(--color-text)" }}>
          Prévisions
        </h2>
        <p className="text-sm" style={{ color: "var(--color-error)" }}>
          {error}
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-base font-semibold mb-1" style={{ color: "var(--color-text)" }}>
        Prévisions
      </h2>
      <p className="text-sm mb-5" style={{ color: "var(--color-muted)" }}>
        Consultez les prévisions par ville et date.
      </p>

      {weather.length === 0 ? (
        <p className="text-sm py-2" style={{ color: "var(--color-muted)" }}>
          Chargez une ville à gauche pour afficher les prévisions.
        </p>
      ) : (
        <>
          <div className="flex flex-wrap gap-5 mb-6">
            <div>
              <label
                htmlFor="ville-select"
                className="block text-xs font-medium mb-1.5 uppercase tracking-wider"
                style={{ color: "var(--color-muted)" }}
              >
                Ville
              </label>
              <select
                id="ville-select"
                value={selectedLoc}
                onChange={handleLocChange}
                className="skapa-input px-3 py-2 min-w-[140px] text-sm"
              >
                <option value="">Choisir</option>
                {locations.map((loc) => (
                  <option key={loc.key} value={loc.key}>
                    {loc.nom}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label
                htmlFor="date-select"
                className="block text-xs font-medium mb-1.5 uppercase tracking-wider"
                style={{ color: "var(--color-muted)" }}
              >
                Date
              </label>
              <select
                id="date-select"
                value={selectedDate}
                onChange={handleDateChange}
                disabled={!selectedLoc}
                className="skapa-input px-3 py-2 min-w-[160px] text-sm disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <option value="">Choisir</option>
                {datesForLoc.map((d) => (
                  <option key={d} value={d}>
                    {formatDateLabel(d)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {selectedDateData.length > 0 ? (
            <div
              className="overflow-hidden rounded-lg"
              style={{ border: "1px solid var(--color-border)" }}
            >
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ background: "var(--color-bg)" }}>
                    <th
                      className="text-left px-4 py-2.5 text-xs font-medium uppercase tracking-wider"
                      style={{ color: "var(--color-muted)" }}
                    >
                      Heure
                    </th>
                    <th
                      className="text-left px-4 py-2.5 text-xs font-medium uppercase tracking-wider"
                      style={{ color: "var(--color-muted)" }}
                    >
                      Température
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {selectedDateData.map((f, idx) => (
                    <tr
                      key={f.time}
                      className="border-t"
                      style={{
                        borderColor: "var(--color-border)",
                        background: idx % 2 === 1 ? "var(--color-bg)" : "transparent",
                      }}
                    >
                      <td className="px-4 py-2.5" style={{ color: "var(--color-text)" }}>
                        {formatHeure(f.time)}
                      </td>
                      <td className="px-4 py-2.5 font-medium" style={{ color: "var(--color-text)" }}>
                        {f.temperature_2m != null ? `${Math.round(f.temperature_2m)}°C` : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : selectedLoc && datesForLoc.length === 0 ? (
            <p className="text-sm" style={{ color: "var(--color-muted)" }}>
              Aucune donnée pour ce lieu.
            </p>
          ) : selectedLoc ? (
            <p className="text-sm" style={{ color: "var(--color-muted)" }}>
              Sélectionnez une date.
            </p>
          ) : null}
        </>
      )}
    </div>
  );
}
