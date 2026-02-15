import WeatherDashboard from "./components/WeatherDashboard";
import LocationSearch from "./components/LocationSearch";
import ChatInterface from "./components/ChatInterface";
import "./App.css";

function App() {
  return (
    <div className="min-h-screen" style={{ background: "var(--color-bg)" }}>
      <div className="max-w-6xl mx-auto px-5 py-10">
        <header className="text-center mb-12">
          <h1 className="text-2xl font-semibold tracking-tight" style={{ color: "var(--color-text)" }}>
            SKAPA
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--color-muted)" }}>
            Météo & agent conversationnel
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-8">
            <section className="skapa-card p-6">
              <LocationSearch />
            </section>
            <section className="skapa-card p-6">
              <ChatInterface />
            </section>
          </div>
          <section className="skapa-card p-6">
            <WeatherDashboard />
          </section>
        </div>
      </div>
    </div>
  );
}

export default App;
