import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../services/api.js";
import { AuthContext } from "./AuthContextValue.js";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(() => !localStorage.getItem(api.TOKEN_KEY));

  const logout = useCallback(() => {
    localStorage.removeItem(api.TOKEN_KEY);
    setUser(null);
  }, []);

  useEffect(() => {
    const onUnauthorized = () => logout();
    window.addEventListener("planetpulse:unauthorized", onUnauthorized);
    const token = localStorage.getItem(api.TOKEN_KEY);
    if (!token) return () => window.removeEventListener("planetpulse:unauthorized", onUnauthorized);
    api.getMe().then(setUser).catch(logout).finally(() => setReady(true));
    return () => window.removeEventListener("planetpulse:unauthorized", onUnauthorized);
  }, [logout]);

  const login = useCallback(async (credentials) => {
    const result = await api.login(credentials);
    localStorage.setItem(api.TOKEN_KEY, result.access_token);
    setUser(result.user);
    return result.user;
  }, []);
  const register = useCallback(async (details) => {
    const result = await api.register(details);
    localStorage.setItem(api.TOKEN_KEY, result.access_token);
    setUser(result.user);
    return result.user;
  }, []);
  const value = useMemo(() => ({ user, ready, login, register, logout }), [user, ready, login, register, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
