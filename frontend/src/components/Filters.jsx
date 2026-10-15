const PRESETS = [
  { name: "Kerala, India", latitude: 10.0, longitude: 76.3 },
  { name: "Delhi, India", latitude: 28.6139, longitude: 77.2090 },
  { name: "Mumbai, India", latitude: 19.0760, longitude: 72.8777 },
  { name: "Chennai, India", latitude: 13.0827, longitude: 80.2707 },
  { name: "New York, USA", latitude: 40.7128, longitude: -74.0060 },
];

export default function Filters({ values, onChange, onAnalyze, loading }) {
  const set = (key, value) => onChange({ ...values, [key]: value });
  const choosePreset = (name) => {
    const preset = PRESETS.find((item) => item.name === name);
    if (preset) onChange({ ...values, regionName: preset.name, latitude: preset.latitude, longitude: preset.longitude });
  };

  return (
    <form className="filters" onSubmit={(event) => { event.preventDefault(); onAnalyze(); }}>
      <label>
        Region preset
        <select value={values.regionName} onChange={(e) => choosePreset(e.target.value)}>
          {PRESETS.map((item) => <option key={item.name}>{item.name}</option>)}
          <option value="Custom coordinates">Custom coordinates</option>
        </select>
      </label>
      <div className="two-fields">
        <label>Latitude
          <input type="number" min="-90" max="90" step="any" value={values.latitude}
            onChange={(e) => set("latitude", Number(e.target.value))} required />
        </label>
        <label>Longitude
          <input type="number" min="-180" max="180" step="any" value={values.longitude}
            onChange={(e) => set("longitude", Number(e.target.value))} required />
        </label>
      </div>
      <label>Hazard type
        <select value={values.hazard} onChange={(e) => set("hazard", e.target.value)}>
          <option value="heatwave">Heatwave</option>
          <option value="heavy_rainfall">Heavy rainfall</option>
          <option value="drought">Drought (exploratory proxy)</option>
        </select>
      </label>
      <div className="two-fields">
        <label>Start year
          <input type="number" min="1940" max={values.endYear} value={values.startYear}
            onChange={(e) => set("startYear", Number(e.target.value))} required />
        </label>
        <label>End year
          <input type="number" min={values.startYear} max="2100" value={values.endYear}
            onChange={(e) => set("endYear", Number(e.target.value))} required />
        </label>
      </div>
      <button className="primary-button" type="submit" disabled={loading}>
        {loading ? "Analyzing historical data…" : "Analyze hazards"}
      </button>
      <p className="hint">First analysis may take a few minutes while daily historical data is fetched and cached.</p>
    </form>
  );
}
