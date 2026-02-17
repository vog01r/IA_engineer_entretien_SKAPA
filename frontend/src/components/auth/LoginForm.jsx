/**
 * LoginForm - Formulaire de connexion
 * 
 * Features :
 * - Validation côté client (email format, password min 8 chars)
 * - Loading state pendant auth
 * - Affichage erreurs API
 * - Lien vers register
 * 
 * Design :
 * - Cohérent avec design system SKAPA (teal accent, DM Sans)
 * - Card centrée, responsive
 * - Focus states accessibles
 */

import { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";

export default function LoginForm({ onSuccess, onSwitchToRegister }) {
  const { login, loading, error: authError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    // Validation côté client
    if (!email || !password) {
      setError("Email and password are required");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    const result = await login(email, password);
    if (result.success) {
      if (onSuccess) onSuccess();
    } else {
      setError(result.error);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--color-bg)" }}>
      <div className="skapa-card w-full max-w-md p-8">
        <h2 className="text-2xl font-semibold mb-2" style={{ color: "var(--color-text)" }}>
          Connexion
        </h2>
        <p className="text-sm mb-6" style={{ color: "var(--color-muted)" }}>
          Connectez-vous pour accéder à l'application météo
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-1" style={{ color: "var(--color-text)" }}>
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="skapa-input w-full"
              placeholder="alice@example.com"
              disabled={loading}
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-1" style={{ color: "var(--color-text)" }}>
              Mot de passe
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="skapa-input w-full"
              placeholder="••••••••"
              disabled={loading}
              required
              minLength={8}
            />
          </div>

          {(error || authError) && (
            <div className="p-3 rounded-lg text-sm" style={{ background: "#fee", color: "#c00" }}>
              {error || authError}
            </div>
          )}

          <button type="submit" className="skapa-btn skapa-btn-primary w-full" disabled={loading}>
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm" style={{ color: "var(--color-muted)" }}>
            Pas encore de compte ?{" "}
            <button
              onClick={onSwitchToRegister}
              className="font-medium"
              style={{ color: "var(--color-accent)" }}
              disabled={loading}
            >
              Créer un compte
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
