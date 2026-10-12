// Calls the visitor counter API (built in Week 2, Step 4).
// Until the API exists, the counter just shows "—" instead of breaking the page.

async function loadVisits() {
  const el = document.getElementById("visits");
  try {
    const res = await fetch("/api/visits");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    el.textContent = data.count;
  } catch (err) {
    console.warn("Visitor counter not available yet:", err);
    el.textContent = "—";
  }
}

loadVisits();
