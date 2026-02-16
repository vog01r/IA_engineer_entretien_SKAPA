import { useState } from "react";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import WeatherDashboard from "./components/WeatherDashboard";
import LocationSearch from "./components/LocationSearch";
import ChatInterface from "./components/ChatInterface";
import "./App.css";

function AppContent() {
  const [dashboardRefresh, setDashboardRefresh] = useState(0);
  const { user, logout } = useAuth();

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
          {user && (
            <div className="mt-4 flex items-center justify-center gap-4">
              <p className="text-sm" style={{ color: "var(--color-muted)" }}>
                Connecté : <span style={{ color: "var(--color-text)" }}>{user.email}</span>
              </p>
              <button
                onClick={logout}
                className="text-sm px-3 py-1 rounded-lg"
                style={{ background: "var(--color-border)", color: "var(--color-text)" }}
              >
                Déconnexion
              </button>
            </div>
          )}
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-8">
            <section className="skapa-card p-6">
              <LocationSearch onFetchSuccess={() => setDashboardRefresh((k) => k + 1)} />
            </section>
            <section className="skapa-card p-6">
              <ChatInterface />
            </section>
          </div>
          <section className="skapa-card p-6">
            <WeatherDashboard refreshTrigger={dashboardRefresh} />
          </section>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <AppContent />
      </ProtectedRoute>
    </AuthProvider>
  );
}

export default App;
