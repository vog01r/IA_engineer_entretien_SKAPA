/**
 * Formateurs pour affichage des dates/heures
 */

export function formatHeure(timeStr) {
  if (!timeStr || timeStr.length < 16) return timeStr ?? "-";
  return timeStr.slice(11, 16);
}

export function formatDateLabel(timeStr) {
  if (!timeStr || timeStr.length < 10) return "";
  const [y, m, d] = timeStr.slice(0, 10).split("-");
  const date = new Date(y, m - 1, d);
  const today = new Date();
  const isToday = date.toDateString() === today.toDateString();
  return isToday
    ? "Aujourd'hui"
    : date.toLocaleDateString("fr-FR", { weekday: "short", day: "numeric", month: "short" });
}
