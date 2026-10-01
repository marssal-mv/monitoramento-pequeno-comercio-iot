export default function StatsGrid({ statistics }) {
  const cards = [
    { label: "Total de eventos", value: statistics?.total_events ?? 0 },
    { label: "Eventos hoje", value: statistics?.today_events ?? 0 },
    { label: "Alertas fora do horário", value: statistics?.alerts ?? 0 },
  ];

  return (
    <div className="stats-grid">
      {cards.map((card) => (
        <div className="stat-card" key={card.label}>
          <span className="stat-value">{card.value}</span>
          <span className="stat-label">{card.label}</span>
        </div>
      ))}
    </div>
  );
}
