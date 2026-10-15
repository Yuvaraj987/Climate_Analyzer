export default function SummaryCards({ result }) {
  const metrics = result.metrics || {};
  const trend = metrics.trend || {};
  const format = (value, suffix = "") => value === null || value === undefined ? "—" : `${value}${suffix}`;
  return (
    <div className="summary-grid">
      <article className="metric-card">
        <span className="metric-label">Detected events / observations</span>
        <strong>{format(metrics.total_events)}</strong>
        <small>Across selected years</small>
      </article>
      <article className="metric-card">
        <span className="metric-label">Average event duration</span>
        <strong>{format(metrics.average_duration_days, " days")}</strong>
        <small>Available for event-based hazards</small>
      </article>
      <article className="metric-card">
        <span className="metric-label">Annual trend slope</span>
        <strong>{format(trend.slope_events_per_year)}</strong>
        <small>{(trend.direction || "unknown").replaceAll("_", " ")}</small>
      </article>
      <article className="metric-card">
        <span className="metric-label">Comparison change</span>
        <strong>{format(metrics.annual_frequency_change_percent, "%")}</strong>
        <small>Earlier vs later half of period</small>
      </article>
    </div>
  );
}
