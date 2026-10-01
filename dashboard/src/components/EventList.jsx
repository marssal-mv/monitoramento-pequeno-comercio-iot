function formatDateTime(isoString) {
  return new Date(isoString).toLocaleString("pt-BR");
}

export default function EventList({ title, events, emptyMessage, variant }) {
  return (
    <div className={`event-list ${variant ?? ""}`}>
      <h2>{title}</h2>
      {events.length === 0 ? (
        <p className="empty-message">{emptyMessage}</p>
      ) : (
        <ul>
          {events.map((event) => (
            <li key={event.id}>
              <span className="event-location">{event.location}</span>
              <span className="event-sensor">{event.sensor_id}</span>
              <span className="event-time">{formatDateTime(event.timestamp)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
