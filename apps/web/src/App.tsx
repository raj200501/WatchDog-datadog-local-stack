import { useEffect, useState } from "react";

type Service = {
  id: number;
  name: string;
  env: string;
};

type Alert = {
  id: number;
  monitor_id: number;
  status: string;
  fired_at: string;
};

type Slo = {
  id: number;
  name: string;
  target: number;
  window_days: number;
};

type Incident = {
  id: number;
  title: string;
  severity: string;
  status: string;
};

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const apiKey = import.meta.env.VITE_API_KEY ?? "dev-watchdog-key";

async function apiFetch<T>(path: string): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, {
    headers: {
      "X-API-Key": apiKey,
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}`);
  }
  return response.json() as Promise<T>;
}

export function App() {
  const [services, setServices] = useState<Service[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [slos, setSlos] = useState<Slo[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<Service[]>("/api/v1/services"),
      apiFetch<Alert[]>("/api/v1/monitors/alerts"),
      apiFetch<Slo[]>("/api/v1/slo"),
      apiFetch<Incident[]>("/api/v1/incidents"),
    ])
      .then(([servicesData, alertsData, sloData, incidentsData]) => {
        setServices(servicesData);
        setAlerts(alertsData);
        setSlos(sloData);
        setIncidents(incidentsData);
      })
      .catch((err) => setError(err.message));
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/50">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
          <div>
            <h1 className="text-2xl font-semibold">WatchDog</h1>
            <p className="text-sm text-slate-400">
              Local observability + incident control plane
            </p>
          </div>
          <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300">
            Demo Mode
          </span>
        </div>
      </header>

      <section className="mx-auto grid max-w-6xl gap-6 px-6 py-8 lg:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-sm text-slate-400">Services</p>
          <p className="mt-2 text-3xl font-semibold">{services.length}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-sm text-slate-400">Active Alerts</p>
          <p className="mt-2 text-3xl font-semibold">
            {alerts.filter((alert) => alert.status === "firing").length}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-sm text-slate-400">SLOs</p>
          <p className="mt-2 text-3xl font-semibold">{slos.length}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-sm text-slate-400">Incidents</p>
          <p className="mt-2 text-3xl font-semibold">{incidents.length}</p>
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-6 px-6 pb-12 lg:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
          <h2 className="text-lg font-semibold">Services</h2>
          <ul className="mt-4 space-y-2 text-sm text-slate-300">
            {services.map((service) => (
              <li key={service.id} className="flex items-center justify-between">
                <span>{service.name}</span>
                <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs">
                  {service.env}
                </span>
              </li>
            ))}
            {!services.length && <li>No services ingested yet.</li>}
          </ul>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
          <h2 className="text-lg font-semibold">Alerts</h2>
          <ul className="mt-4 space-y-2 text-sm text-slate-300">
            {alerts.slice(0, 5).map((alert) => (
              <li key={alert.id}>
                Monitor {alert.monitor_id} · {alert.status}
              </li>
            ))}
            {!alerts.length && <li>No alerts triggered.</li>}
          </ul>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
          <h2 className="text-lg font-semibold">Incidents</h2>
          <ul className="mt-4 space-y-2 text-sm text-slate-300">
            {incidents.slice(0, 5).map((incident) => (
              <li key={incident.id}>
                {incident.title} · {incident.status}
              </li>
            ))}
            {!incidents.length && <li>No incidents yet.</li>}
          </ul>
        </div>
      </section>

      {error && (
        <div className="mx-auto max-w-6xl px-6 pb-12 text-sm text-rose-300">
          {error}
        </div>
      )}
    </main>
  );
}
