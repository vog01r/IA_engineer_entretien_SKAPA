/**
 * RegisterForm - Formulaire de création de compte
 * 
 * Features :
 * - Validation côté client (email format, password min 8 chars, confirmation)
 * - Loading state pendant création
 * - Affichage erreurs API
 * - Lien vers login
 * 
 * Design :
 * - Cohérent avec design system SKAPA (teal accent, DM Sans)
 * - Card centrée, responsive
 * - Focus states accessibles
 */

import { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";

export default function RegisterForm({ onSuccess, onSwitchToLogin }) {
  const { register, loading, error: authError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    // Validation côté client
    if (!email || !password || !confirmPassword) {
      setError("All fields are required");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    const result = await register(email, password);
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
          Créer un compte
        </h2>
        <p className="text-sm mb-6" style={{ color: "var(--color-muted)" }}>
          Inscrivez-vous pour accéder à l'application météo
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
            <p className="text-xs mt-1" style={{ color: "var(--color-muted)" }}>
              Minimum 8 caractères
            </p>
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1" style={{ color: "var(--color-text)" }}>
              Confirmer le mot de passe
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
            {loading ? "Création..." : "Créer mon compte"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm" style={{ color: "var(--color-muted)" }}>
            Déjà un compte ?{" "}
            <button
              onClick={onSwitchToLogin}
              className="font-medium"
              style={{ color: "var(--color-accent)" }}
              disabled={loading}
            >
              Se connecter
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
