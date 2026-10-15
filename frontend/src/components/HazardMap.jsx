import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";

export default function HazardMap({ result }) {
  const { latitude, longitude } = result.region;
  const frequency = result.metrics?.total_events ?? 0;
  const radius = Math.min(22, 8 + Math.log1p(frequency) * 2);
  return (
    <section className="panel map-panel">
      <div className="section-heading">
        <div>
          <h2>Selected location</h2>
          <p>Point-based analysis; not a full regional grid map</p>
        </div>
      </div>
      <MapContainer center={[latitude, longitude]} zoom={5} scrollWheelZoom={false} className="leaflet-map">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <CircleMarker center={[latitude, longitude]} radius={radius} pathOptions={{ color: "#0f766e", fillColor: "#14b8a6", fillOpacity: 0.65 }}>
          <Popup>
            <strong>{result.hazard.replaceAll("_", " ")}</strong><br />
            {latitude}, {longitude}<br />
            Total metric: {frequency}
          </Popup>
        </CircleMarker>
      </MapContainer>
      <p className="map-coordinates">Latitude {latitude} · Longitude {longitude}</p>
    </section>
  );
}
