import "./Coach.css";

function display(value, digits = 1) {
  return Number(value ?? 0).toLocaleString(undefined, { maximumFractionDigits: digits });
}

function GoalSummary({ goal }) {
  if (!goal) return <span>No monthly goal data</span>;
  return <span>{display(goal.current)} / {display(goal.target, 0)} kg goal · {display(goal.progress)}%</span>;
}

export function CoachPanel({ data, loading, error, actions, checkedActions, onToggleAction, onRetry, onAddActivity, onTryWhatIf }) {
  const hasActivities = Boolean(data?.hasActivities);
  const hasEmissions = Boolean(data?.hasEmissions);
  const trend = data?.trend;
  const trendLabel = trend?.hasBaseline
    ? `${display(Math.abs(trend.changePercent))}% ${trend.changePercent > 0 ? "up" : trend.changePercent < 0 ? "down" : "unchanged"} vs previous 7 days`
    : "No previous 7-day baseline";
  const reductionLabel = data?.hasMonthlyReductionBaseline
    ? `${display(Math.abs(data.reductionPercent))}% ${data.reductionPercent > 0 ? "lower" : data.reductionPercent < 0 ? "higher" : "unchanged"} vs previous month`
    : "No previous-month baseline";

  return (
    <section className="panel coach-panel" id="coach" aria-labelledby="coach-heading">
      <div className="coach-top">
        <div className="coach-robot" aria-hidden="true">🌱</div>
        <div className="coach-title-wrap">
          <span className="panel-eyebrow">PERSONALIZED FOR YOU</span>
          <h2 id="coach-heading">Coach</h2>
        </div>
        <span className="coach-method">RULE-BASED</span>
      </div>

      {loading ? (
        <div className="coach-loading-state" role="status" aria-live="polite">
          <span className="coach-spinner" aria-hidden="true" />
          <div><strong>Loading your Coach</strong><span>Checking your activities, goal, and recent emissions…</span></div>
          <div className="coach-skeleton" aria-hidden="true"><i /><i /><i /></div>
        </div>
      ) : error ? (
        <div className="coach-message coach-error-state" role="alert">
          <span aria-hidden="true">!</span>
          <div><strong>Unable to load Coach recommendations.</strong><p>Please try again.</p></div>
          <button className="coach-retry" onClick={onRetry}>Try again</button>
        </div>
      ) : !hasActivities ? (
        <div className="coach-message coach-empty-state">
          <span aria-hidden="true">✳</span>
          <div><strong>Personalized guidance starts with your activity data.</strong><p>Add more activities to receive personalized Coach guidance.</p></div>
          <button className="coach-primary-action" onClick={onAddActivity}>＋ Add Activity</button>
        </div>
      ) : !hasEmissions ? (
        <div className="coach-message coach-empty-state">
          <span aria-hidden="true">🌿</span>
          <div><strong>Your logged choices have no direct emissions in this estimate.</strong><p>{data?.opportunity}</p></div>
          <button className="coach-primary-action" onClick={onAddActivity}>＋ Log another activity</button>
        </div>
      ) : (
        <>
          <div className="coach-insight">
            <span className="insight-bar" />
            <div>
              <span className="coach-section-label">OBSERVATION</span>
              <strong>{data.observation || `${data.contributor} is your largest emission category.`} · {display(data.contributionPercent, 0)}% of this month’s footprint.</strong>
              <span className="coach-section-label recommendation-label">RECOMMENDATION</span>
              <p>{data.recommendation || data.opportunity}</p>
            </div>
          </div>
          <div className="coach-data-summary" aria-label="Personal data used for this guidance">
            <div><strong>{display(data.activityCount, 0)}</strong><span>activities this month</span></div>
            <div><strong>{display(data.totalCo2e, 2)} kg</strong><span>current footprint</span></div>
            <div><strong><GoalSummary goal={data.goalProgress} /></strong><span>monthly goal progress</span></div>
            <div><strong>{display(trend?.currentPeriodCo2e, 2)} kg</strong><span>last 7 days · {trendLabel}</span></div>
            <div><strong>{reductionLabel}</strong><span>month-over-month</span></div>
          </div>
          {data.recentActivities?.length > 0 && <div className="coach-recent-activities"><span className="coach-section-label">RECENT ACTIVITIES CONSIDERED</span><div>{data.recentActivities.slice(0, 3).map((activity, index) => <span key={`${activity.activity_date}-${activity.activity_type}-${index}`}>{activity.activity_type} · {activity.category} · {display(activity.co2e, 2)} kg CO₂e</span>)}</div></div>}
          <div className="actions-heading"><span>THIS WEEK’S ACTIONS</span><small>{checkedActions.length}/{actions.length} complete</small></div>
          {actions.length ? (
            <div className="coach-actions">
              {actions.map((action, index) => (
                <label className={`coach-action ${checkedActions.includes(index) ? "done" : ""}`} key={`${action}-${index}`}>
                  <input type="checkbox" checked={checkedActions.includes(index)} onChange={() => onToggleAction(index)} />
                  <span className="custom-check">✓</span><span>{action}</span><span className="action-arrow" aria-hidden="true">↗</span>
                </label>
              ))}
            </div>
          ) : <p className="coach-no-actions">No additional actions are available for this activity yet.</p>}
          {data.contributor?.toLowerCase() === "travel" && <button className="coach-primary-action coach-try-whatif" onClick={onTryWhatIf}>Try What-If →</button>}
        </>
      )}

      <div className="coach-footer">
        <span>{data?.method === "rule_based" ? "Rule-based guidance from your account’s logged activity." : "Guidance is based on your authenticated Planet Pulse account."}</span>
        <button onClick={onRetry} disabled={loading}>{loading ? "Refreshing…" : "Refresh Coach ↻"}</button>
      </div>
    </section>
  );
}

export function CoachPreview({ data, loading, error, onRetry, onAddActivity, onOpenCoach, onOpenWhatIf }) {
  return (
    <section className="panel coach-preview" aria-labelledby="dashboard-coach-heading">
      <div className="coach-preview-heading">
        <span className="coach-preview-icon" aria-hidden="true">🌱</span>
        <div><span className="panel-eyebrow">PERSONAL GUIDANCE</span><h2 id="dashboard-coach-heading">Coach</h2></div>
        <span className="coach-method">RULE-BASED</span>
      </div>
      {loading ? (
        <div className="coach-preview-state" role="status"><span className="coach-spinner" /> Loading your guidance…</div>
      ) : error ? (
        <div className="coach-preview-state coach-preview-error" role="alert"><span>Unable to load recommendations.</span><button onClick={onRetry}>Retry</button></div>
      ) : !data?.hasActivities ? (
        <div className="coach-preview-state coach-preview-empty"><p>Add more activities to receive personalized Coach guidance.</p><button className="coach-primary-action" onClick={onAddActivity}>＋ Add Activity</button></div>
      ) : !data.hasEmissions ? (
        <div className="coach-preview-state coach-preview-empty"><p>{data.opportunity}</p><button className="coach-primary-action" onClick={onAddActivity}>＋ Add Activity</button></div>
      ) : (
          <div className="coach-preview-content">
          <strong>{data.observation || `${data.contributor} is your largest emission category`} · {display(data.contributionPercent, 0)}%.</strong>
          <p>{data.recommendation || data.opportunity}</p>
          {data.actions?.[0] && <div className="coach-preview-action"><span aria-hidden="true">✓</span><span>This week: {data.actions[0]}</span></div>}
          <div className="coach-preview-metrics">{display(data.totalCo2e, 2)} kg CO₂e · {display(data.activityCount, 0)} activities · goal {display(data.goalProgress?.progress ?? 0)}%</div>
        </div>
      )}
      <div className="coach-preview-footer">
        <button className="coach-open-button" onClick={onOpenCoach}>Open Coach <span>→</span></button>
        <button className="coach-whatif-button" onClick={onOpenWhatIf}>Explore What-If</button>
      </div>
    </section>
  );
}
