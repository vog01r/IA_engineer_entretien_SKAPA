import WeatherDashboard from "./components/WeatherDashboard";
import LocationSearch from "./components/LocationSearch";
import ChatInterface from "./components/ChatInterface";
import "./App.css";

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
          SKAPA - Météo & Agent IA
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Colonne gauche */}
          <div className="space-y-8">
            <section className="bg-white shadow rounded-lg p-6">
              <LocationSearch />
            </section>
            <section className="bg-white shadow rounded-lg p-6">
              <ChatInterface />
            </section>
          </div>

          {/* Colonne droite */}
          <section className="bg-white shadow rounded-lg p-6">
            <WeatherDashboard />
          </section>
        </div>
      </div>
    </div>
  );
}

export default App;
