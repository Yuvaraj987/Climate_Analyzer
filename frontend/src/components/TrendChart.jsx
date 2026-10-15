import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend,
} from "recharts";

export default function TrendChart({ result }) {
  const data = result.timeseries || [];
  const isHeatwave = result.hazard === "heatwave";
  const isRain = result.hazard === "heavy_rainfall";
  return (
    <section className="panel chart-panel">
      <div className="section-heading">
        <div>
          <h2>Annual hazard trend</h2>
          <p>Computed from historical daily observations</p>
        </div>
        <span className="chart-tag">{result.hazard.replaceAll("_", " ")}</span>
      </div>
      {data.length ? (
        <ResponsiveContainer width="100%" height={300}>
          {isRain ? (
            <BarChart data={data} margin={{ top: 10, right: 12, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" minTickGap={24} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="frequency" name="Heavy-rain days" fill="#0f766e" radius={[4, 4, 0, 0]} />
            </BarChart>
          ) : (
            <LineChart data={data} margin={{ top: 10, right: 12, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" minTickGap={24} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="frequency" name={isHeatwave ? "Heatwave events" : "Qualifying drought-proxy days"} stroke="#0f766e" strokeWidth={2.5} dot={false} />
              {isHeatwave && <Line type="monotone" dataKey="average_duration_days" name="Average duration (days)" stroke="#d97706" strokeWidth={2} dot={false} />}
            </LineChart>
          )}
        </ResponsiveContainer>
      ) : <div className="empty-state">No time-series observations to plot.</div>}
    </section>
  );
}
