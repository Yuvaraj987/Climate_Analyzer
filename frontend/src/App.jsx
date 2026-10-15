import { useState } from "react";
import Filters from "./components/Filters.jsx";
import SummaryCards from "./components/SummaryCards.jsx";
import TrendChart from "./components/TrendChart.jsx";
import HazardMap from "./components/HazardMap.jsx";
import { analyzeHazards } from "./services/api.js";

const initialFilters = {
  regionName: "Kerala, India",
  latitude: 10.0,
  longitude: 76.3,
  hazard: "heatwave",
  startYear: 1990,
  endYear: 2020,
};

export default function App() {
  const [filters, setFilters] = useState(initialFilters);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runAnalysis() {
    setLoading(true);
    setError("");
    try {
      const data = await analyzeHazards({
        latitude: Number(filters.latitude),
        longitude: Number(filters.longitude),
        start_year: Number(filters.startYear),
        end_year: Number(filters.endYear),
        hazard: filters.hazard,
        min_consecutive_days: 3,
      });
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Unable to analyze this request.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark">☼</span>
          <span>Climate<span className="brand-light">Lens</span></span>
        </a>
        <span className="topbar-caption">Historical hazard explorer</span>
      </header>

      <main className="main-content">
        <section className="hero">
          <div className="eyebrow">CLIMATE DATA · LONG-TERM TRENDS</div>
          <h1>Understand how climate hazards change over time.</h1>
          <p>Explore historical weather patterns, compare years, and inspect hazard frequency at a selected location.</p>
        </section>

        <div className="dashboard-layout">
          <aside className="panel filter-panel">
            <div className="section-heading">
              <div><h2>Analysis settings</h2><p>Choose a place and time period</p></div>
            </div>
            <Filters values={filters} onChange={setFilters} onAnalyze={runAnalysis} loading={loading} />
          </aside>

          <div className="results-column">
            {error && <div className="error-banner"><strong>Analysis failed</strong><span>{String(error)}</span></div>}
            {!result && !error && (
              <section className="welcome-panel">
                <div className="welcome-icon">↗</div>
                <h2>Your climate analysis starts here</h2>
                <p>Choose a region and select <strong>Analyze hazards</strong>. The backend will fetch historical weather observations, cache them, and calculate hazard trends.</p>
                <div className="welcome-pills"><span>Historical data</span><span>Hazard detection</span><span>Trend analysis</span></div>
              </section>
            )}
            {loading && <div className="loading-line"><span className="spinner" /> Processing historical data. The first request can take some time.</div>}
            {result && (
              <>
                <div className="result-title">
                  <div><div className="eyebrow">ANALYSIS RESULT</div><h2>{result.hazard.replaceAll("_", " ")} overview</h2></div>
                  <span className="period-pill">{result.period.start_year}–{result.period.end_year}</span>
                </div>
                <SummaryCards result={result} />
                <section className="insight-panel">
                  <span className="insight-icon">✦</span>
                  <div><h3>Key insight</h3><p>{result.insight}</p></div>
                </section>
                <TrendChart result={result} />
                <HazardMap result={result} />
                <section className="panel methodology">
                  <h2>Methodology & limitations</h2>
                  <p>{result.methodology?.definition}</p>
                  <p>{result.methodology?.caveat}</p>
                  {result.threshold !== null && result.threshold !== undefined && (
                    <p><strong>Calculated threshold:</strong> {result.threshold} {result.hazard === "heavy_rainfall" ? "mm/day" : "°C"}</p>
                  )}
                </section>
                <section className="panel events-panel">
                  <div className="section-heading"><div><h2>Detected events</h2><p>Showing up to 500 returned records</p></div></div>
                  {result.events?.length ? (
                    <div className="table-wrap"><table><thead><tr><th>Start</th><th>End</th><th>Duration</th><th>Peak / details</th></tr></thead>
                      <tbody>{result.events.map((event, index) => <tr key={`${event.start_date}-${index}`}>
                        <td>{event.start_date}</td><td>{event.end_date}</td><td>{event.duration_days} day(s)</td>
                        <td>{event.peak_temperature_c != null ? `${event.peak_temperature_c} °C` : event.peak_rainfall_mm != null ? `${event.peak_rainfall_mm} mm` : "Qualifying drought-proxy day"}</td>
                      </tr>)}</tbody></table></div>
                  ) : <p className="empty-state">No individual events were returned for this hazard and period.</p>}
                </section>
              </>
            )}
          </div>
        </div>
      </main>
      <footer>ClimateLens · Historical data analysis only · Not an official warning system</footer>
    </div>
  );
}
