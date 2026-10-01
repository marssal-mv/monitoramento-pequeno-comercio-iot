function formatDateTime(isoString) {
  if (!isoString) return "—";
  return new Date(isoString).toLocaleString("pt-BR");
}

export default function StatusBanner({ status, lastMotion }) {
  const isOpen = status?.establishment === "Aberta";

  return (
    <div className={`status-banner ${isOpen ? "status-open" : "status-closed"}`}>
      <div className="status-dot" />
      <div>
        <strong>Estabelecimento {status?.establishment ?? "—"}</strong>
        <p>Último movimento: {formatDateTime(lastMotion)}</p>
      </div>
    </div>
  );
}
