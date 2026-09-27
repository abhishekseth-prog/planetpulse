import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";
import "./Readability.css";
import StatCard from "./components/StatCard.jsx";
import { api } from "./services/api.js";
import { AuthProvider } from "./context/AuthContext.jsx";
import { useAuth } from "./context/useAuth.js";
import AuthPage from "./components/AuthPage.jsx";

const EMPTY_DATA = { total_co2e: 0, total_activities: 0, travel_co2e: 0, electricity_co2e: 0, food_co2e: 0, reduction_percent: 0 };
const CATEGORIES = {
  travel: { label: "Travel", icon: "🚗", color: "green", unit: "km", examples: ["Car", "Metro", "Bus", "Bike", "Walk"] },
  electricity: { label: "Electricity", icon: "⚡", color: "blue", unit: "kWh", examples: ["Air conditioner", "Lighting", "Refrigerator", "Other appliance"] },
  food: { label: "Food", icon: "🍽️", color: "orange", unit: "meal", examples: ["Plant-based meal", "Chicken meal", "Dairy meal", "Beef meal"] },
};
const fmt = (n, max = 1) => n == null ? "—" : Number(n || 0).toLocaleString(undefined, { maximumFractionDigits: max });

function normalizeTrend(data) {
  const source = Array.isArray(data) ? data : data?.values ?? data?.co2e ?? data?.points ?? data?.trend ?? data?.series ?? [];
  const values = Array.isArray(source) ? source.map((point) => Number(point && typeof point === "object" ? point.co2e ?? point.total_co2e ?? point.value : point)).filter(Number.isFinite) : [];
  if (!values.length) return { values: [], labels: [], average: 0, demo: false, empty: true };
  const labels = (Array.isArray(data) ? null : data?.labels ?? data?.dates) ?? (Array.isArray(source) && typeof source[0] === "object" ? source.map((point) => point.label ?? point.date ?? "") : []);
  const normalizedLabels = Array.isArray(labels) ? labels.map((label) => typeof label === "object" ? label.label ?? label.date ?? "" : label) : [];
  const suppliedAverage = Array.isArray(data) ? null : data?.average_daily ?? data?.average ?? data?.avg_co2e;
  const average = suppliedAverage ?? values.reduce((sum, value) => sum + value, 0) / values.length;
  return { values, labels: normalizedLabels, average, demo: false, empty: values.every((value) => value === 0) };
}

function normalizeCoach(data) {
  if (!data || typeof data !== "object") return null;
  const actions = data.actions ?? data.weekly_actions ?? data.recommendations ?? [];
  return {
    contributor: data.largest_contributor ?? data.top_contributor ?? data.top_category ?? data.category ?? "",
    contributionPercent: data.contribution_percent ?? data.share_percent ?? data.percent ?? data.travel_percent ?? 0,
    opportunity: data.opportunity ?? data.insight ?? data.recommendation ?? "",
    actions: (Array.isArray(actions) ? actions : [actions]).map((action) => typeof action === "string" ? action : action.title ?? action.text ?? action.label ?? "Suggested action"),
    potentialImpact: data.potential_impact_kg ?? data.potential_savings ?? data.potential_reduction ?? 0,
    demo: false,
  };
}

function chartGeometry(values) {
  const source = values?.length ? values : [0];
  const max = Math.max(...source, 1);
  const points = source.map((value, index) => ({ x: source.length === 1 ? 220 : index * 440 / (source.length - 1), y: 112 - Number(value) / max * 90 }));
  const line = points.map((point, index) => `${index ? "L" : "M"}${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
  const first = points[0]; const last = points.at(-1);
  return { line, fill: `${line} L${last.x.toFixed(1)} 124 L${first.x.toFixed(1)} 124 Z`, last };
}

function PlanetPulseApp() {
  const { user, logout } = useAuth();
  const [dashboard, setDashboard] = useState(EMPTY_DATA);
  const [activities, setActivities] = useState([]);
  const [usingDemo] = useState(false);
  const [trendData, setTrendData] = useState({ values: [], labels: [], average: 0, empty: true });
  const [trendError, setTrendError] = useState("");
  const [trendLoading, setTrendLoading] = useState(true);
  const [coachData, setCoachData] = useState(null);
  const [coachError, setCoachError] = useState("");
  const [coachLoading, setCoachLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState("");
  const [loading, setLoading] = useState(true);
  const [dashboardLoaded, setDashboardLoaded] = useState(false);
  const [goalResponse, setGoalResponse] = useState({ target_co2e: 100, used_co2e: 0, progress_percent: 0, remaining_co2e: 100 });
  const [goalEditor, setGoalEditor] = useState(false);
  const [goalDraft, setGoalDraft] = useState("100");
  const [goalError, setGoalError] = useState("");
  const [goalSaving, setGoalSaving] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [activityResult, setActivityResult] = useState(null);
  const [form, setForm] = useState({ category: "travel", activity: "Car", amount: "20", date: new Date().toISOString().slice(0, 10) });
  const [simulated, setSimulated] = useState(false);
  const [simulationResponse, setSimulationResponse] = useState(null);
  const [simulating, setSimulating] = useState(false);
  const [planAdded, setPlanAdded] = useState(false);
  const [trendRange, setTrendRange] = useState("7 days");
  const [changeTo, setChangeTo] = useState("Metro");
  const [checkedActions, setCheckedActions] = useState([]);
  const [toast, setToast] = useState("");
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);
  const [view, setView] = useState("overview");

  const loadData = useCallback(async () => {
    try {
      const [data, rows, fetchedGoal] = await Promise.all([
        api.getDashboard(),
        api.getActivities(),
        api.getGoal().catch(() => null),
      ]);
      setDashboard({
        total_co2e: data.total_co2e ?? data.total_co2 ?? 0,
        total_activities: data.total_activities ?? data.activities ?? 0,
        travel_co2e: data.travel_co2e ?? data.travel ?? 0,
        electricity_co2e: data.electricity_co2e ?? data.electricity ?? 0,
        food_co2e: data.food_co2e ?? data.food ?? 0,
        reduction_percent: data.reduction_percent ?? data.reduction ?? 0,
      });
      const goalData = fetchedGoal ?? data.goal_progress ?? data.goal;
      if (goalData) setGoalResponse({
        target_co2e: goalData.target_co2e ?? goalData.target_kg ?? goalData.target ?? 100,
        used_co2e: goalData.used_co2e ?? goalData.used_kg ?? goalData.current ?? 0,
        progress_percent: goalData.progress_percent ?? goalData.progress ?? 0,
        remaining_co2e: goalData.remaining_co2e ?? goalData.remaining_kg ?? goalData.remaining ?? 100,
      });
      setActivities(Array.isArray(rows) ? rows : []);
      setDashboardError("");
      setDashboardLoaded(true);
    } catch (error) {
      setDashboardError(error.message || "Couldn't load your PlanetPulse data.");
    } finally { setLoading(false); }
  }, []);

  const loadTrend = useCallback(async (range) => {
    setTrendLoading(true);
    const period = range === "7 days" ? "7d" : range === "30 days" ? "30d" : "3m";
    try {
      const normalized = normalizeTrend(await api.getTrend(period));
      setTrendData(normalized);
      setTrendError("");
    } catch (error) {
      setTrendError(error.message || "Carbon trend is unavailable.");
      setTrendData({ values: [], labels: [], average: 0, empty: true });
    } finally { setTrendLoading(false); }
  }, []);
  const loadInsights = useCallback(async () => {
    setCoachLoading(true);
    try { setCoachData(normalizeCoach(await api.getInsights())); setCoachError(""); }
    catch (error) { setCoachData(null); setCoachError(error.message || "Insights are not available yet."); }
    finally { setCoachLoading(false); }
  }, []);

  useEffect(() => { const timer = window.setTimeout(() => { void loadData(); }, 0); return () => window.clearTimeout(timer); }, [loadData]);
  useEffect(() => { const timer = window.setTimeout(() => { void loadTrend(trendRange); }, 0); return () => window.clearTimeout(timer); }, [trendRange, loadTrend]);
  useEffect(() => { const timer = window.setTimeout(() => { void loadInsights(); }, 0); return () => window.clearTimeout(timer); }, [loadInsights]);
  useEffect(() => { if (!toast) return undefined; const timer = window.setTimeout(() => setToast(""), 3600); return () => window.clearTimeout(timer); }, [toast]);
  useEffect(() => {
    if (!modalOpen) return undefined;
    const closeOnEscape = (event) => { if (event.key === "Escape") setModalOpen(false); };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [modalOpen]);

  const total = Number(dashboard.total_co2e || 0);
  const reduction = Number(dashboard.reduction_percent || 0);
  const categoryTotal = useMemo(() => Object.keys(CATEGORIES).reduce((sum, key) => sum + Number(dashboard[`${key}_co2e`] || 0), 0), [dashboard]);
  const categoryRows = Object.entries(CATEGORIES).map(([key, item]) => {
    const amount = Number(dashboard[`${key}_co2e`] || 0);
    return { key, ...item, amount, percent: categoryTotal ? Math.round(amount / categoryTotal * 100) : 0 };
  });
  const category = CATEGORIES[form.category];
  const trendChart = chartGeometry(trendData.values);
  const goal = goalResponse.target_co2e;
  const goalUsed = goalResponse.used_co2e;
  const goalPercent = goalResponse.progress_percent;

  function updateCategory(nextCategory) {
    const next = CATEGORIES[nextCategory];
    setActivityResult(null);
    setForm((current) => ({ ...current, category: nextCategory, activity: next.examples[0], amount: "" }));
  }

  async function submitActivity(event) {
    event.preventDefault(); setFormError(""); setSaving(true);
    if (!Number(form.amount) || Number(form.amount) <= 0) { setFormError("Enter an amount greater than zero."); setSaving(false); return; }
    try {
      const result = await api.addActivity({ category: form.category, activity_type: form.activity, value: Number(form.amount), unit: category.unit, activity_date: form.date });
      setActivityResult(result); setToast("Activity added."); await loadData(); await Promise.all([loadTrend(trendRange), loadInsights()]);
    } catch (error) { setFormError(error.message || "Could not reach the activity API."); }
    finally { setSaving(false); }
  }

  async function saveGoal(event) {
    event.preventDefault();
    const target = Number(goalDraft);
    if (!Number.isFinite(target) || target <= 0) { setGoalError("Enter a target greater than zero."); return; }
    setGoalSaving(true); setGoalError("");
    try {
      const result = await api.updateGoal(target);
      setGoalResponse({
        target_co2e: result.target_co2e ?? result.target,
        used_co2e: result.used_co2e ?? result.current,
        progress_percent: result.progress_percent ?? result.progress,
        remaining_co2e: result.remaining_co2e ?? result.remaining,
      });
      setGoalEditor(false); setToast("Monthly goal updated.");
    } catch (error) {
      setGoalError(error.message || "Could not update the monthly goal.");
    } finally { setGoalSaving(false); }
  }

  function toggleAction(index) {
    setCheckedActions((current) => current.includes(index) ? current.filter((item) => item !== index) : [...current, index]);
  }

  function addSimulationToPlan() {
    setPlanAdded(true);
    setView("coach");
    setToast("The simulator option was added to your weekly plan.");
  }

  async function runSimulation() {
    setSimulated(false); setSimulating(true);
    try {
      const data = await api.simulateWhatIf({ category: "travel", current_activity: "Car", alternative_activity: changeTo, distance: 20, unit: "km" });
      setSimulationResponse({
        current: data.current_kg_co2e ?? data.current_kg ?? data.current_co2 ?? data.current?.co2e,
        alternative: data.new_kg_co2e ?? data.new_kg ?? data.new_co2 ?? data.alternative?.co2e,
        dailySaving: data.saving_kg_per_day ?? data.saved_per_day ?? data.saved_daily ?? data.savings_per_day ?? data.saving ?? data.daily_reduction,
        monthlySaving: data.saving_kg_per_month ?? data.saved_per_month ?? data.saved_monthly ?? data.savings_per_month ?? data.monthly_saving ?? data.monthly_reduction,
        reductionPercent: data.reduction_percent ?? data.reduction_pct ?? data.percent_saved,
        demo: false,
      });
      setSimulated(true);
    } catch (error) {
      setSimulationResponse(null);
      setToast(error.message || "The simulator is temporarily unavailable.");
    } finally { setSimulating(false); }
  }

  const breakdownPanel = <section className="panel breakdown-panel" id="breakdown"><div className="panel-heading"><div><span className="panel-eyebrow">YOUR FOOTPRINT</span><h2>Carbon by category</h2></div><span className="heading-glyph">◒</span></div>{loading ? <div className="data-state">Loading category breakdown…</div> : !dashboardLoaded ? <div className="data-state error-state" role="alert">Unable to load your data. Please try again.</div> : categoryTotal <= 0 ? <div className="data-state">No category data available yet.</div> : <><div className="category-list">{categoryRows.map((item) => <div className="category-item" key={item.key}><div className={`category-icon ${item.color}`}>{item.icon}</div><div className="category-detail"><div className="category-title"><strong>{item.label}</strong><span>{fmt(item.amount)} kg</span></div><div className="category-track"><span className={item.color} style={{ width: `${item.percent}%` }}/></div></div><span className="category-percent">{item.percent}%</span></div>)}</div><div className="panel-foot"><span><i/> Share of total emissions</span><span>kg CO₂e</span></div></>}</section>;
  const trendPanel = <section className="panel trend-panel" id="trend"><div className="panel-heading"><div><span className="panel-eyebrow">YOUR LAST {trendRange.toUpperCase()}</span><h2>Carbon trend</h2></div><div className="trend-controls">{["7 days", "30 days", "3 months"].map((range) => <button type="button" key={range} className={trendRange === range ? "selected" : ""} onClick={() => { setTrendRange(range); setTrendLoading(true); }}>{range === "7 days" ? "7D" : range === "30 days" ? "30D" : "3M"}</button>)}</div></div>{trendLoading ? <div className="data-state">Loading your carbon trend…</div> : trendError ? <div className="data-state error-state" role="alert">{trendError}</div> : trendData.empty ? <div className="data-state">No emissions recorded during this period yet.</div> : <><div className="chart-legend"><span><i/> Daily emissions</span><strong>{fmt(trendData.average)} <small>kg avg.</small></strong></div><div className="chart-area"><div className="chart-y"><span>{fmt(Math.max(...trendData.values), 1)}</span><span>{fmt(Math.max(...trendData.values) * .66, 1)}</span><span>{fmt(Math.max(...trendData.values) * .33, 1)}</span><span>0</span></div><div className="chart-main"><div className="chart-gridlines"><i/><i/><i/><i/></div><svg className="trend-chart" viewBox="0 0 440 130" preserveAspectRatio="none" role="img" aria-label={`Carbon emissions trend for ${trendRange}`}><defs><linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#78a881" stopOpacity=".2"/><stop offset="100%" stopColor="#78a881" stopOpacity="0"/></linearGradient></defs><path className="chart-area-fill" d={trendChart.fill}/><path className="chart-line" d={trendChart.line}/><circle cx={trendChart.last.x} cy={trendChart.last.y} r="4" className="chart-point"/></svg><div className="chart-x">{trendData.labels.filter((_, index) => index % Math.ceil(trendData.labels.length / 7) === 0).slice(0, 7).map((label, index) => <span key={`${label}-${index}`}>{label}</span>)}</div></div></div></>}<div className="trend-note"><span>↘</span> {trendLoading ? "Refreshing daily totals" : trendError ? "Trend API error" : trendData.empty ? "Add an activity to begin tracking your trend" : "Daily emissions returned by your account data."}</div></section>;
  const goalPanel = <section className="panel goal-panel" id="goal"><div className="panel-heading"><div><span className="panel-eyebrow">AIM FOR LESS</span><h2>Monthly goal</h2></div><span className="goal-badge">🎯</span></div>{loading ? <div className="data-state">Loading your monthly goal…</div> : !dashboardLoaded ? <div className="data-state error-state" role="alert">Unable to load your data. Please try again.</div> : <><div className="goal-number-row"><div><strong>{fmt(goalUsed)} <span>/ {fmt(goal, 0)} kg</span></strong><small>CO₂e this month</small></div><span className="goal-percent">{fmt(goalPercent, 0)}%</span></div><div className="goal-track"><span style={{ width: `${Math.min(goalPercent, 100)}%` }}/><i style={{ left: `${Math.min(goalPercent, 100)}%` }}/></div><div className="goal-remaining">{fmt(goalResponse.remaining_co2e)} kg remaining</div>{goalEditor ? <form className="goal-edit" onSubmit={saveGoal}><label htmlFor="goal-target">New monthly target</label><div><input id="goal-target" type="number" min="1" value={goalDraft} onChange={(event) => setGoalDraft(event.target.value)} disabled={goalSaving}/><button type="submit" disabled={goalSaving}>{goalSaving ? "Saving…" : "Save"}</button><button type="button" className="cancel-edit" onClick={() => { setGoalEditor(false); setGoalError(""); }} disabled={goalSaving}>Cancel</button></div>{goalError && <p className="form-error" role="alert">{goalError}</p>}</form> : <button className="outline-button update-goal" onClick={() => { setGoalDraft(String(goal)); setGoalError(""); setGoalEditor(true); }}>Update Goal <span>↗</span></button>}</>}</section>;
  const simulatorPanel = <section className="panel simulator-panel" id="simulator"><div className="panel-heading"><div><span className="panel-eyebrow">EXPLORE A BETTER ROUTE</span><h2><span className="sim-title-icon">✧</span> What if?</h2></div><span className="future-pill">SIMULATOR</span></div><p className="sim-intro">See how one small swap could change your impact.</p><div className="sim-controls"><div className="sim-choice"><label>YOUR CURRENT ACTIVITY</label><div><span className="sim-icon car-icon">↗</span><strong>Car <small>· 20 km/day</small></strong></div></div><div className="sim-arrow">→</div><div className="sim-choice"><label>CHANGE TO</label><div className="select-container"><span className="sim-icon transit-icon">⇢</span><select value={changeTo} onChange={(event) => { setChangeTo(event.target.value); setSimulated(false); setSimulationResponse(null); setPlanAdded(false); }}><option>Metro</option><option>Bus</option><option>Bike</option><option>Walk</option></select><span className="select-chevron">⌄</span></div></div></div><button className="simulate-button" onClick={runSimulation} disabled={simulating}>{simulating ? "Getting response…" : "Simulate this change"}<span>↗</span></button>{simulated ? <div className="sim-result" role="status"><div className="sim-result-top"><div><small>CURRENT</small><strong>{fmt(simulationResponse?.current, 2)} <i>kg/day</i></strong></div><span className="result-arrow">→</span><div><small>WITH {changeTo.toUpperCase()}</small><strong>{fmt(simulationResponse?.alternative, 2)} <i>kg/day</i></strong></div></div><div className="saving-callout"><span>✳</span><div><small>You could save · ↓ {fmt(simulationResponse?.reductionPercent, 0)}%</small><strong>{fmt(simulationResponse?.dailySaving, 2)} kg CO₂/day <i>≈ {fmt(simulationResponse?.monthlySaving, 0)} kg/month</i></strong></div></div><small className="mock-caption">{simulationResponse?.demo ? "Sample response · Waiting for the What-If API" : "Result returned by the What-If API"}</small><button className="plan-button" onClick={addSimulationToPlan} disabled={planAdded}>{planAdded ? "Added to My Plan ✓" : "Add to My Plan →"}</button></div> : <div className="sim-placeholder"><span>✧</span> Your comparison will appear here</div>}</section>;
  const actionItems = [...(coachData?.actions ?? []), ...(planAdded ? [`Try ${changeTo} instead of car for 20 km`] : [])];
  const coachPanel = <section className="panel coach-panel" id="coach"><div className="coach-top"><div className="coach-robot">✳</div><div><span className="panel-eyebrow">PERSONALIZED FOR YOU</span><h2>AI Carbon Coach</h2></div><span className="ai-pill">{coachLoading ? "LOADING" : coachError ? "UNAVAILABLE" : "INSIGHT API"}</span></div><div className="coach-insight"><span className="insight-bar"/><p>{coachLoading ? "Loading your personalized insight…" : coachError ? coachError : coachData ? <><strong>{coachData.contributor} is your largest contributor — {fmt(coachData.contributionPercent, 0)}%.</strong><br/>{coachData.opportunity}</> : "Personalized insight will appear here when available."}</p></div><div className="actions-heading"><span>THIS WEEK’S ACTIONS</span><small>{checkedActions.length}/{actionItems.length} complete</small></div>{actionItems.length ? <div className="coach-actions">{actionItems.map((action, index) => <label className={`coach-action ${checkedActions.includes(index) ? "done" : ""}`} key={action}><input type="checkbox" checked={checkedActions.includes(index)} onChange={() => toggleAction(index)}/><span className="custom-check">✓</span><span>{action}</span><span className="action-arrow">↗</span></label>)}</div> : <p className="data-state">{coachLoading ? "Loading action plan…" : "Action recommendations will appear when the Insights API returns them."}</p>}<div className="coach-footer"><span>{coachError ? "Insights are unavailable right now." : "Recommendations returned by the Insights API."}</span><button onClick={() => setToast(coachError || "Showing the latest API insight.")}>View all tips <span>→</span></button></div></section>;
  const recentPanel = <section className="panel recent-panel" id="activities"><div className="panel-heading"><div><span className="panel-eyebrow">YOUR LATEST ENTRIES</span><h2>Recent activities</h2></div><button className="text-button" onClick={() => { setFormError(""); setActivityResult(null); setModalOpen(true); }}>＋ Add activity</button></div>{loading ? <p className="no-activities">Loading your activities…</p> : !dashboardLoaded ? <p className="no-activities error-state" role="alert">Unable to load your data. Please try again.</p> : activities.length ? <div className="recent-list">{activities.slice(0, view === "activities" ? activities.length : 4).map((entry) => { const item = CATEGORIES[entry.category] || CATEGORIES.travel; return <div className="recent-row" key={entry.id}><span className={`category-icon ${item.color}`}>{item.icon}</span><div className="recent-name"><strong>{entry.activity_type || item.label}</strong><small>{item.label} · {entry.activity_date || "Today"}</small></div><span className="recent-amount">{fmt(entry.value, 2)} {entry.unit}</span><strong className="recent-carbon">{fmt(entry.co2e ?? entry.carbon_kg_co2e, 2)} <small>kg CO₂e</small></strong></div>; })}</div> : <p className="no-activities">No activity yet. Add one to get started.</p>}<div className="api-footnote">{dashboardError ? "Activity data is temporarily unavailable." : "Private activity data from your PlanetPulse account."}</div></section>;
  const analyticsCategoriesPanel = <section className="panel top-activities"><div className="panel-heading"><div><span className="panel-eyebrow">BIGGEST CONTRIBUTORS</span><h2>Top categories</h2></div></div>{loading ? <p className="data-state">Loading category data…</p> : !dashboardLoaded ? <p className="data-state error-state" role="alert">Unable to load your data. Please try again.</p> : categoryTotal <= 0 ? <p className="data-state">No category data available yet.</p> : categoryRows.map((row) => <div className="top-category-row" key={row.key}><span className={`category-icon ${row.color}`}>{row.icon}</span><strong>{row.label}</strong><span>{fmt(row.amount)} kg</span><b>{row.percent}%</b></div>)}</section>;
  const viewTitles = { overview: "Dashboard", activities: "Activities", analytics: "Analytics", simulator: "Simulator", coach: "Coach", goals: "Goals", settings: "Settings" };
  const navItems = [{ id: "overview", icon: "⌂", label: "Dashboard" }, { id: "activities", icon: "▤", label: "Activities" }, { id: "analytics", icon: "▥", label: "Analytics" }, { id: "simulator", icon: "⌁", label: "Simulator" }, { id: "coach", icon: "♧", label: "Coach" }, { id: "goals", icon: "◎", label: "Goals" }];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => setView("overview")} aria-label="PlanetPulse dashboard"><span className="brand-symbol">🌍</span><span>PlanetPulse</span></button>
        <nav className="side-nav" aria-label="Dashboard sections">{navItems.map((item) => <button key={item.id} className={`side-link ${item.id === "overview" ? "dashboard-link" : ""} ${view === item.id ? "active" : ""}`} onClick={() => setView(item.id)} aria-label={item.label} title={item.label} aria-current={view === item.id ? "page" : undefined}><span>{item.icon}</span>{item.label}</button>)}</nav>
        <button className={`side-link settings-link ${view === "settings" ? "active" : ""}`} onClick={() => setView("settings")} aria-label="Settings" title="Settings" aria-current={view === "settings" ? "page" : undefined}><span>⚙</span>Settings</button>
        <div className="sidebar-bottom"><div className="sidebar-tip"><span>✳</span><strong>Small choices.<br/>Big change.</strong></div><div className="account-row"><div className="account-avatar">{(user?.name || "P").slice(0,1).toUpperCase()}</div><div><strong>{user?.name}</strong><small>Personal account</small></div><button className="account-more" onClick={logout} aria-label="Sign out" title="Sign out">↪</button></div></div>
      </aside>

      <main className="main-content" id="top">
        <header className="topbar"><div className="crumb"><strong>{viewTitles[view]}</strong></div><div className="topbar-actions"><label className="search-box"><span>⌕</span><input aria-label="Search activities" placeholder="Search activities…" onKeyDown={(event) => { if (event.key === "Enter") setView("activities"); }}/></label><button className="notification-button" aria-label="Notifications">♧</button>{dashboardError ? <span className="demo-badge"><i/> Data unavailable</span> : <span className="connected-badge"><i/> Live data</span>}<button className="refresh-button" onClick={() => { setLoading(true); loadData(); }} aria-label="Refresh dashboard" title="Refresh dashboard">↻</button><button className="top-avatar" onClick={logout} aria-label="Sign out" title="Sign out">{(user?.name || "P").slice(0,1).toUpperCase()}</button></div></header>

        <div className="page-content">
          {view === "overview" && <>
            <section className="welcome-row"><div><div className="overline"><span/> PERSONAL CARBON INTELLIGENCE</div><h1>Good morning, {user?.name?.split(" ")[0] || "there"} <span className="wave">👋</span></h1><p>Understand your impact. Make better choices for a cleaner tomorrow.</p></div><button className="primary-button add-main" onClick={() => { setFormError(""); setActivityResult(null); setModalOpen(true); }}><span>＋</span> Add Activity</button></section>
            {dashboardError && <div className="data-banner error-state" role="alert">{dashboardError} <button onClick={() => { setLoading(true); loadData(); }}>Try again</button></div>}
            <section className="stat-grid four-stats" aria-label="Carbon summary">
              <StatCard variant="stat-total" label="TOTAL CO₂e" icon="🌱" value={loading || !dashboardLoaded ? "—" : fmt(total)} unit="kg" footer="All activities recorded"/>
              <StatCard label="ACTIVITIES" icon="▥" iconClass="activity-icon" value={loading || !dashboardLoaded ? "—" : fmt(dashboard.total_activities, 0)} footer="Activities tracked"/>
              <StatCard label="MONTHLY GOAL" icon="◎" iconClass="goal-icon" value={loading || !dashboardLoaded ? "—" : fmt(goalUsed)} unit={loading || !dashboardLoaded ? "" : ` / ${fmt(goal, 0)} kg`} footer={`${loading || !dashboardLoaded ? "—" : fmt(goalPercent, 0)}% complete`}><div className="mini-progress"><span style={{ width: `${loading || !dashboardLoaded ? 0 : Math.min(goalPercent, 100)}%` }}/></div></StatCard>
              <StatCard label={reduction < 0 ? "INCREASE" : "REDUCTION"} icon={reduction < 0 ? "↗" : "↘"} iconClass="trend-icon" value={loading || !dashboardLoaded ? "—" : fmt(Math.abs(reduction))} unit="%" footer={<><span className="positive-tag">{loading || !dashboardLoaded ? "—" : `${reduction < 0 ? "↑" : "↓"} ${fmt(Math.abs(reduction))}%`}</span><span>vs. last month</span></>}><div className="sparkline" aria-hidden="true"/></StatCard>
            </section>
            <div className="overview-middle">{breakdownPanel}{goalPanel}<section className="panel opportunity-panel"><div className="opportunity-heading"><span className="panel-eyebrow">YOUR BIGGEST OPPORTUNITY</span><span className="ai-pill">{coachError ? "INSIGHT UNAVAILABLE" : "INSIGHT API"}</span></div><div className="opportunity-content"><span className="opportunity-icon">↗</span><p><strong>{coachData?.contributor ? `${coachData.contributor} contributes ${fmt(coachData.contributionPercent, 0)}% of your footprint.` : "Your personalized opportunity"}</strong><br/>{coachData?.opportunity || coachError || "Your insight will appear when available."}</p></div><button className="opportunity-button" onClick={() => setView("simulator")}>Explore What‑If <span>→</span></button></section></div>
            <div className="overview-bottom">{trendPanel}{recentPanel}</div>
          </>}
          {view === "activities" && <><section className="page-title-row"><div><div className="overline"><span/> YOUR DAILY FOOTPRINT</div><h1>Activities</h1><p>Track and review the choices that shape your carbon impact.</p></div><button className="primary-button add-main" onClick={() => { setFormError(""); setActivityResult(null); setModalOpen(true); }}>＋ Add Activity</button></section>{recentPanel}</>}
          {view === "analytics" && <><section className="page-title-row"><div><div className="overline"><span/> YOUR IMPACT, OVER TIME</div><h1>Analytics</h1><p>See the patterns behind your carbon footprint.</p></div><button className="range-button">Last 30 days⌄</button></section><div className="analytics-grid">{trendPanel}{breakdownPanel}<section className="panel analytics-bars"><div className="panel-heading"><div><span className="panel-eyebrow">DAILY EMISSIONS</span><h2>Trend detail</h2></div></div>{trendLoading ? <p className="data-state">Loading daily totals…</p> : trendError ? <p className="data-state error-state">{trendError}</p> : trendData.empty ? <p className="data-state">No emissions recorded during this period.</p> : <div className="trend-day-list">{trendData.values.map((value,index) => <div className="trend-day-row" key={trendData.labels[index] + index}><span>{trendData.labels[index]}</span><div><i style={{width:`${Math.max(value / Math.max(...trendData.values,1) * 100, value ? 2 : 0)}%`}} /></div><strong>{fmt(value,2)} kg</strong></div>)}</div>}</section>{analyticsCategoriesPanel}</div></>}
          {view === "simulator" && <><section className="page-title-row"><div><div className="overline"><span/> EXPLORE YOUR OPTIONS</div><h1>Impact Simulator</h1><p>Try a different choice and compare the returned carbon impact.</p></div></section><div className="simulator-page-grid">{simulatorPanel}<aside className="panel simulator-note"><span>✧</span><h2>One small swap can add up.</h2><p>Compare your current activity with a lower-impact alternative. The simulator result is supplied by the impact API.</p><div><strong>Calculation source</strong><small>{usingDemo ? "Illustrative demo response" : "Agreed simulator API"}</small></div></aside></div></>}
          {view === "coach" && <><section className="page-title-row"><div><div className="overline"><span/> A PLAN THAT FITS YOUR LIFE</div><h1>AI Carbon Coach</h1><p>Personalized insights and actions to help lighten your footprint.</p></div></section><div className="coach-page-grid">{coachPanel}<aside className="panel impact-panel"><span className="panel-eyebrow">POTENTIAL IMPACT</span><div className="impact-leaf">🌱</div><strong>{fmt(coachData?.potentialImpact, 1)} kg CO₂e</strong><span>per month</span><button className="outline-button" onClick={() => setView("goals")}>See your monthly goal →</button></aside></div></>}
          {view === "goals" && <><section className="page-title-row"><div><div className="overline"><span/> STEADY PROGRESS</div><h1>My Goals</h1><p>Set a monthly target and track your pace.</p></div></section><div className="goals-page-grid">{goalPanel}<section className="panel pace-panel"><span className="panel-eyebrow">CURRENT PACE</span><div className="pace-icon">⌁</div><p>Your average so far is <strong>{fmt(goalUsed / Math.max(new Date().getDate(), 1), 2)} kg/day</strong>.</p><p>At this pace, your estimated monthly footprint is <strong>{fmt((goalUsed / Math.max(new Date().getDate(), 1)) * 30, 1)} kg</strong>.</p><div className="pace-warning">ⓘ Estimate based on this month’s actual logged emissions.</div><button className="outline-button" onClick={() => setView("simulator")}>Explore the simulator →</button></section></div></>}
          {view === "settings" && <><section className="page-title-row"><div><div className="overline"><span/> YOUR PLANETPULSE ACCOUNT</div><h1>Settings</h1><p>Manage your profile and see how your footprint data is connected.</p></div></section><div className="settings-grid"><section className="panel settings-card"><div className="settings-card-head"><span className="settings-icon">◉</span><div><span className="panel-eyebrow">ACCOUNT</span><h2>Profile</h2></div></div><div className="settings-profile"><div className="settings-avatar">{(user?.name || "P").slice(0,1).toUpperCase()}</div><div><strong>{user?.name}</strong><span>{user?.email}</span></div><span className="settings-state">Active</span></div><p className="settings-help">Your personal activity history and monthly goals are shown in this workspace.</p><button className="outline-button" onClick={logout}>Sign out</button></section><section className="panel settings-card"><div className="settings-card-head"><span className="settings-icon">↗</span><div><span className="panel-eyebrow">DATA CONNECTION</span><h2>Activity data</h2></div></div><div className={`connection-status ${usingDemo ? "demo" : "live"}`}><i/>{dashboardError ? "Connection issue" : "Connected to PlanetPulse API"}</div><p className="settings-help">{dashboardError || "Dashboard totals and activity history are loaded from your connected API."}</p><button className="outline-button settings-refresh" onClick={() => { setLoading(true); loadData(); }} disabled={loading}>{loading ? "Refreshing…" : "Refresh connection"} <span>↻</span></button></section><section className="panel settings-card settings-units"><div className="settings-card-head"><span className="settings-icon">CO₂</span><div><span className="panel-eyebrow">DISPLAY</span><h2>Carbon units</h2></div></div><div className="unit-setting"><div><strong>Emissions display</strong><span>Used consistently across the dashboard and activity results.</span></div><span className="unit-chip">kg CO₂e</span></div></section></div></>}
          <footer className="page-footer"><span><span>🌍</span> PlanetPulse <i>·</i> Make every day a little lighter.</span><span>Private figures returned by the PlanetPulse API</span></footer>
        </div>
      </main>

      {modalOpen && <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setModalOpen(false); }}><section className="activity-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><div className="modal-heading"><div><span className="panel-eyebrow">LOG A NEW CHOICE</span><h2 id="modal-title">{activityResult ? "Activity impact" : "Add Activity"}</h2></div><button className="modal-close" onClick={() => setModalOpen(false)} aria-label="Close dialog">×</button></div><p className="modal-description">{activityResult ? "Here’s the result returned for your activity." : "Track a choice you’ve made today."}</p>{activityResult ? <div className="activity-result"><span className="result-leaf">🌱</span><div><small>ESTIMATED IMPACT</small><strong>{fmt(activityResult.carbon_kg_co2e ?? activityResult.co2e ?? activityResult.carbon, 2)} kg CO₂e</strong></div><button type="button" onClick={() => setModalOpen(false)}>Done</button></div> : <form onSubmit={submitActivity}><div className="modal-categories">{Object.entries(CATEGORIES).map(([key, item]) => <button type="button" className={`modal-category ${form.category === key ? "selected" : ""}`} key={key} onClick={() => updateCategory(key)}><span className={`category-icon ${item.color}`}>{item.icon}</span>{item.label}</button>)}</div><label className="form-label" htmlFor="activity-kind">{form.category === "travel" ? "Transport mode" : form.category === "electricity" ? "Appliance" : "Meal type"}</label><select className="modal-select" id="activity-kind" value={form.activity} onChange={(event) => setForm({ ...form, activity: event.target.value })}>{category.examples.map((item) => <option key={item}>{item}</option>)}</select><label className="form-label" htmlFor="activity-amount">{form.category === "travel" ? "Distance" : form.category === "electricity" ? "Usage" : "Meals"}<span>{category.unit}</span></label><div className="amount-input"><input id="activity-amount" type="number" min="0.01" step="0.01" placeholder="Enter amount" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} required/><span>{category.unit}⌄</span></div><label className="form-label" htmlFor="activity-date">Date</label><input className="modal-date" id="activity-date" type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })}/>{formError && <p className="form-error" role="alert">{formError}</p>}<div className="modal-actions"><button className="modal-cancel" type="button" onClick={() => setModalOpen(false)}>Cancel</button><button className="primary-button calculate-button" type="submit" disabled={saving}>{saving ? "Getting result…" : "Calculate impact"}<span>↗</span></button></div><p className="modal-note">{usingDemo ? "Impact is calculated by the activity API using your account data." : "Impact is calculated by the activity API."}</p></form>}</section></div>}
      {toast && <div className="toast" role="status"><span>✓</span>{toast}</div>}
    </div>
  );
}

function AuthenticatedApp() {
  const { user, ready } = useAuth();
  if (!ready) return <div className="auth-loading">🌍 Loading PlanetPulse…</div>;
  return user ? <PlanetPulseApp /> : <AuthPage />;
}

export default function App() {
  return <AuthProvider><AuthenticatedApp /></AuthProvider>;
}
