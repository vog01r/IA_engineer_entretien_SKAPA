/**
 * ProtectedRoute - Wrapper pour routes nécessitant authentification
 * 
 * Features :
 * - Redirige vers login si pas authentifié
 * - Loading state pendant vérification auth
 * - Switch login/register
 * 
 * Usage :
 * <ProtectedRoute>
 *   <WeatherDashboard />
 * </ProtectedRoute>
 */

import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import LoginForm from "./auth/LoginForm";
import RegisterForm from "./auth/RegisterForm";

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  // Loading state pendant vérification auth
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--color-bg)" }}>
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" style={{ color: "var(--color-accent)" }}></div>
          <p className="mt-4 text-sm" style={{ color: "var(--color-muted)" }}>
            Vérification...
          </p>
        </div>
      </div>
    );
  }

  // Pas authentifié : afficher login ou register
  if (!user) {
    if (showRegister) {
      return <RegisterForm onSuccess={() => {}} onSwitchToLogin={() => setShowRegister(false)} />;
    }
    return <LoginForm onSuccess={() => {}} onSwitchToRegister={() => setShowRegister(true)} />;
  }

  // Authentifié : afficher le contenu protégé
  return children;
}
