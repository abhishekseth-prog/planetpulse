import { useState } from "react";
import { useAuth } from "../context/useAuth.js";

export default function AuthPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [visible, setVisible] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault(); setError("");
    if (mode === "register" && password !== confirm) { setError("Your passwords do not match."); return; }
    setBusy(true);
    try {
      const credentials = { email: email.trim(), password };
      if (mode === "register") await register({ ...credentials, name: name.trim() });
      else await login(credentials);
    } catch (reason) { setError(reason.message || "We couldn't complete sign in. Please try again."); }
    finally { setBusy(false); }
  }

  return <main className="auth-screen">
    <section className="auth-visual"><div className="auth-brand"><span>🌍</span> PlanetPulse</div><div className="auth-message"><span className="auth-eyebrow">PERSONAL CARBON INTELLIGENCE</span><h1>Small choices.<br/><em>Big change.</em></h1><p>Understand your footprint, build better habits, and make every day a little lighter.</p><div className="auth-orbit" aria-hidden="true"><span>🌱</span></div></div><div className="auth-visual-foot">A clearer view of your impact.</div></section>
    <section className="auth-form-side"><form className="auth-card" onSubmit={submit}>
      <span className="auth-kicker">WELCOME TO PLANETPULSE</span><h2>{mode === "login" ? "Welcome back" : "Create your account"}</h2><p>{mode === "login" ? "Sign in to see your personal carbon footprint." : "Start tracking your impact with a private account."}</p>
      {mode === "register" && <label className="auth-field">Full name<input autoComplete="name" value={name} onChange={(event) => setName(event.target.value)} placeholder="Your name" minLength="2" maxLength="100" required/></label>}
      <label className="auth-field">Email address<input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" maxLength="254" required/></label>
      <label className="auth-field">Password<div className="password-wrap"><input type={visible ? "text" : "password"} autoComplete={mode === "login" ? "current-password" : "new-password"} value={password} onChange={(event) => setPassword(event.target.value)} placeholder={mode === "register" ? "At least 10 characters" : "Enter your password"} minLength={mode === "register" ? 10 : 1} maxLength="128" required/><button type="button" onClick={() => setVisible(!visible)}>{visible ? "Hide" : "Show"}</button></div></label>
      {mode === "register" && <label className="auth-field">Confirm password<input type={visible ? "text" : "password"} autoComplete="new-password" value={confirm} onChange={(event) => setConfirm(event.target.value)} placeholder="Enter password again" required/></label>}
      {error && <div className="auth-error" role="alert">{error}</div>}
      <button className="auth-submit" type="submit" disabled={busy}>{busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}<span>→</span></button>
      <div className="auth-switch">{mode === "login" ? "New to PlanetPulse?" : "Already have an account?"}<button type="button" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>{mode === "login" ? "Create an account" : "Sign in"}</button></div>
      {mode === "register" && <small className="auth-password-hint">Use 10 or more characters for your password.</small>}
    </form><div className="auth-privacy">🔒 Your activity history and goals are private to your account.</div></section>
  </main>;
}
