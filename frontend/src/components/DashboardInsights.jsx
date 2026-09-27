import "./DashboardInsights.css";

const CATEGORY_TIPS = {
  travel: "Consider public transport or combining nearby trips.",
  electricity: "Review appliance use and switch off idle devices.",
  food: "Try a lower-impact meal for one of your usual choices.",
};
const CATEGORY_NAMES = { travel: "Travel", electricity: "Electricity", food: "Food" };
const fmt = (value, digits = 1) => Number(value ?? 0).toLocaleString(undefined, { maximumFractionDigits: digits });

function CarbonScore({ loading, error, dashboard, activities }) {
  const now = new Date();
  const monthKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  const monthlyActivities = activities.filter((activity) => String(activity.activity_date ?? "").slice(0, 7) === monthKey);
  const trackedDays = new Set(monthlyActivities.map((activity) => String(activity.activity_date).slice(0, 10))).size;
  const goalProgress = Number(dashboard.goal_progress?.progress_percent ?? dashboard.goal?.progress_percent ?? 0);
  const elapsedDays = Math.max(new Date().getDate(), 1);
  const goalHeadroom = Math.max(0, Math.min(100, 100 - goalProgress));
  const trackingConsistency = Math.min(100, (trackedDays / elapsedDays) * 100);
  const score = Math.round(goalHeadroom * 0.7 + trackingConsistency * 0.3);

  return <section className="panel dashboard-extra-card score-card" aria-labelledby="carbon-score-heading">
    <div className="dashboard-extra-heading"><span className="dashboard-extra-icon">◉</span><div><span className="panel-eyebrow">PRODUCT METRIC</span><h2 id="carbon-score-heading">Carbon Score</h2></div></div>
    {loading ? <p className="dashboard-extra-state" role="status">Loading your score…</p>
      : error ? <p className="dashboard-extra-state error-state" role="alert">Unable to load this information. Please try again.</p>
        : monthlyActivities.length === 0 ? <p className="dashboard-extra-state">Track activities this month to calculate your score.</p>
          : <><div className="score-value">{score}<span> / 100</span></div><p className="score-explanation">Your Planet Pulse score reflects goal headroom (70%) and the share of elapsed days with a logged activity (30%). It is a product metric, not an official environmental rating.</p></>}
  </section>;
}
function MonthlyComparison({ loading, error, dashboard }) {
  const current = Number(dashboard.total_co2e ?? dashboard.total_co2 ?? 0);
  const previous = dashboard.previous_month;
  const hasPrevious = Boolean(previous?.has_data ?? dashboard.has_previous_month_data);
  const delta = current - Number(previous?.total_co2e ?? 0);
  return <section className="panel dashboard-extra-card monthly-comparison" aria-labelledby="monthly-comparison-heading">
    <div className="dashboard-extra-heading"><span className="dashboard-extra-icon">↗</span><div><span className="panel-eyebrow">YOUR MONTHLY PROGRESS</span><h2 id="monthly-comparison-heading">Monthly Comparison</h2></div></div>
    {loading ? <p className="dashboard-extra-state" role="status">Loading monthly totals…</p>
      : error ? <p className="dashboard-extra-state error-state" role="alert">Unable to load this information. Please try again.</p>
        : !hasPrevious ? <div className="dashboard-extra-state"><strong>Not enough previous data yet.</strong><span>Keep tracking activities to see your progress.</span></div>
          : <><div className="comparison-values"><div><span>This month · to date</span><strong>{fmt(current, 2)} <small>kg CO₂e</small></strong></div><div><span>{previous.label} · full month</span><strong>{fmt(previous.total_co2e, 2)} <small>kg CO₂e</small></strong></div></div><div className={`comparison-change ${delta <= 0 ? "lower" : "higher"}`}><span>{delta <= 0 ? "↓" : "↑"}</span>{fmt(Math.abs(delta), 2)} kg CO₂e {delta <= 0 ? "lower" : "higher"} so far</div><p className="comparison-note">Periods are labeled separately because the current month is still in progress.</p></>}
  </section>;
}

function TodaysAction({ loading, error, coach, onAddActivity, onOpenCoach, onOpenWhatIf }) {
  const contributor = coach?.contributor?.toLowerCase() ?? "";
  const hasAction = Boolean(coach?.hasEmissions && coach.actions?.length && contributor);
  return <section className="panel dashboard-extra-card todays-action" aria-labelledby="todays-action-heading">
    <div className="dashboard-extra-heading"><span className="dashboard-extra-icon">🌱</span><div><span className="panel-eyebrow">ONE PRACTICAL NEXT STEP</span><h2 id="todays-action-heading">Today’s Action</h2></div></div>
    {loading ? <p className="dashboard-extra-state" role="status">Finding an action from your activity…</p>
      : error ? <p className="dashboard-extra-state error-state" role="alert">Unable to load this information. Please try again.</p>
        : hasAction ? <><p className="today-action-copy">{coach.actions[0]}</p><small className="today-action-source">Based on your {coach.contributor} emissions this month.</small><button className="dashboard-extra-cta" onClick={contributor === "travel" ? onOpenWhatIf : onOpenCoach}>{contributor === "travel" ? "Try What-If →" : "Review Coach →"}</button></>
          : <><p className="dashboard-extra-state">Track more activities to receive personalized actions.</p><button className="dashboard-extra-cta" onClick={onAddActivity}>＋ Add Activity</button></>}
  </section>;
}

export function DashboardInsights({ loading, error, dashboard, activities, coach, coachLoading, coachError, onAddActivity, onOpenCoach, onOpenWhatIf }) {
  return <div className="dashboard-insights-grid">
    <MonthlyComparison loading={loading} error={error} dashboard={dashboard} />
    <CarbonScore loading={loading} error={error} dashboard={dashboard} activities={activities} />
    <TodaysAction loading={coachLoading} error={coachError} coach={coach} onAddActivity={onAddActivity} onOpenCoach={onOpenCoach} onOpenWhatIf={onOpenWhatIf} />
  </div>;
}

export function CategoryInsightsPanel({ loading, error, dashboard }) {
  const categories = dashboard.category_totals ?? {
    travel: dashboard.travel_co2e ?? 0,
    electricity: dashboard.electricity_co2e ?? 0,
    food: dashboard.food_co2e ?? 0,
  };
  const values = Object.keys(CATEGORY_NAMES).map((key) => ({ key, name: CATEGORY_NAMES[key], amount: Number(categories[key] ?? 0), previous: Number(dashboard.previous_month?.categories?.[key] ?? 0) }));
  const total = values.reduce((sum, category) => sum + category.amount, 0);
  return <section className="panel category-insights-panel" aria-labelledby="category-insights-heading">
    <div className="dashboard-extra-heading"><span className="dashboard-extra-icon">◒</span><div><span className="panel-eyebrow">CATEGORY INSIGHTS</span><h2 id="category-insights-heading">Carbon by category</h2></div></div>
    {loading ? <p className="dashboard-extra-state" role="status">Loading category insights…</p>
      : error ? <p className="dashboard-extra-state error-state" role="alert">Unable to load this information. Please try again.</p>
        : total <= 0 ? <p className="dashboard-extra-state">Add an activity to see category shares and personalized tips.</p>
          : <div className="category-insight-list">{values.map(({ key, name, amount, previous }) => {
            const share = total ? Math.round((amount / total) * 100) : 0;
            const comparison = previous > 0 ? ((amount - previous) / previous) * 100 : null;
            return <article className="category-insight-item" key={key}>
              <div className="category-insight-top"><strong>{name}</strong><span>{fmt(share, 0)}% · {fmt(amount, 2)} kg CO₂e</span></div>
              <div className="category-insight-track"><i style={{ width: `${share}%` }} /></div>
              <p>Coach: {amount > 0 ? CATEGORY_TIPS[key] : "No emissions recorded in this category this month."}</p>
              <small>{comparison == null ? "Not enough historical data for comparison." : `${comparison > 0 ? "↑" : comparison < 0 ? "↓" : "→"} ${fmt(Math.abs(comparison))}% vs previous month`}</small>
            </article>;
          })}</div>}
  </section>;
}
