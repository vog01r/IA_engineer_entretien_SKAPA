/**
 * AuthContext - Context React pour gestion authentification JWT
 * 
 * Fonctionnalités :
 * - Login / Register : Appels API avec httpOnly cookies
 * - Auto-refresh : Renouvellement token automatique avant expiration
 * - Logout : Suppression cookies + clear state
 * - Persistence : Vérifie /auth/me au mount pour restaurer session
 * 
 * Justifications techniques :
 * - httpOnly cookies : Tokens gérés côté serveur (pas de localStorage)
 * - credentials: "include" : Envoie cookies cross-origin
 * - Auto-refresh : Appel /auth/refresh 5min avant expiration (55min)
 * - Loading states : UX fluide pendant auth/refresh
 * 
 * Sécurité :
 * - Tokens jamais accessibles JS (httpOnly cookies)
 * - Refresh automatique (pas de re-login constant)
 * - Clear state au logout (pas de données résiduelles)
 */

import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Vérifie si l'utilisateur est connecté au mount
  useEffect(() => {
    checkAuth();
  }, []);

  // Auto-refresh token toutes les 55min (avant expiration 60min)
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(
      async () => {
        try {
          await refreshToken();
        } catch (err) {
          console.error("Auto-refresh failed:", err);
          // Si refresh échoue, déconnecter l'utilisateur
          setUser(null);
        }
      },
      55 * 60 * 1000
    ); // 55 minutes

    return () => clearInterval(interval);
  }, [user]);

  async function checkAuth() {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/auth/me`, {
        credentials: "include", // Envoie cookies httpOnly
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch (err) {
      console.error("Check auth error:", err);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  async function register(email, password) {
    try {
      setError(null);
      setLoading(true);

      const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // Reçoit cookies httpOnly
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Registration failed");
      }

      const data = await response.json();
      setUser(data.user);
      return { success: true };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }

  async function login(email, password) {
    try {
      setError(null);
      setLoading(true);

      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // Reçoit cookies httpOnly
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Login failed");
      }

      const data = await response.json();
      setUser(data.user);
      return { success: true };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        credentials: "include", // Supprime cookies httpOnly
      });
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      setUser(null);
      setError(null);
    }
  }

  async function refreshToken() {
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Refresh token failed");
    }

    const data = await response.json();
    setUser(data.user);
  }

  const value = {
    user,
    loading,
    error,
    register,
    login,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
