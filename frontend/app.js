// Visitor counter: calls the Azure Function, which adds 1 in Table Storage
// and returns the new total. If the API can't be reached, the page shows "—".
const COUNTER_API = "https://func-hisham-visits.azurewebsites.net/api/visits";

async function loadVisits() {
  const el = document.getElementById("visits");
  try {
    const res = await fetch(COUNTER_API, { method: "POST" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    el.textContent = Number(data.count).toLocaleString();
  } catch (err) {
    console.warn("Visitor counter not available:", err);
    el.textContent = "—";
  }
}

loadVisits();
