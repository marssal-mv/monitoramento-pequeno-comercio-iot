import { useEffect, useState } from "react";
import { fetchDashboardData } from "./api";
import StatusBanner from "./components/StatusBanner";
import StatsGrid from "./components/StatsGrid";
import EventList from "./components/EventList";
import "./App.css";

const POLL_INTERVAL_MS = 5000;

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const result = await fetchDashboardData();
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }

    load();
    const interval = setInterval(load, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Monitoramento Padaria Rosa de Saron</h1>
      </header>

      {error && (
        <div className="error-banner">
          Não foi possível conectar à API. Verifique se o backend está rodando.
          <br />
          <small>{error}</small>
        </div>
      )}

      {data && (
        <>
          <StatusBanner status={data.status} lastMotion={data.last_motion} />
          <StatsGrid statistics={data.statistics} />

          <div className="event-columns">
            <EventList
              title="Eventos recentes"
              events={data.recent_events}
              emptyMessage="Nenhum evento registrado ainda."
            />
            <EventList
              title="Alertas (fora do horário)"
              events={data.alerts}
              emptyMessage="Nenhum alerta registrado."
              variant="alert-list"
            />
          </div>
        </>
      )}

      {!data && !error && <p className="loading">Carregando...</p>}
    </div>
  );
}

export default App;
