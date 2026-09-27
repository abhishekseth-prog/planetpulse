import { useState } from "react";
import { api } from "../services/api.js";

const TRAVEL_OPTIONS = ["Metro", "Bus", "Bike", "Walk", "Car"];
const FOOD_OPTIONS = ["Plant-based meal", "Chicken meal", "Dairy meal", "Beef meal"];
const CATEGORY_ICON = { travel: "🚗", electricity: "⚡", food: "🍽️" };
const fmt = (value, digits = 2) => Number(value ?? 0).toLocaleString(undefined, { maximumFractionDigits: digits });
const unitName = (unit) => String(unit ?? "").toLowerCase() === "kwh" ? "kWh" : String(unit ?? "");
const activityName = (activity) => String(activity?.activity_type ?? activity?.activity ?? "Activity");

function alternativesFor(activity) {
  if (activity?.category === "travel") return TRAVEL_OPTIONS.filter((option) => option.toLowerCase() !== activityName(activity).toLowerCase());
  if (activity?.category === "electricity") return ["Reduce electricity usage"];
  if (activity?.category === "food") return FOOD_OPTIONS.filter((option) => option.toLowerCase() !== activityName(activity).toLowerCase());
  return [];
}

function activityOptionLabel(activity) {
  return `${activityName(activity)} · ${fmt(activity.value, 2)} ${unitName(activity.unit)} · ${fmt(activity.co2e, 2)} kg CO₂e`;
}

export default function ImpactSimulator({ activities, loading, error, selectedActivityId, onSelectActivity, onAddActivity, onRetry, onAddToPlan, planAdded }) {
  const selected = activities.find((activity) => String(activity.id) === String(selectedActivityId)) ?? activities[0] ?? null;
  const [alternative, setAlternative] = useState("");
  const [alternativeAmount, setAlternativeAmount] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [simulating, setSimulating] = useState(false);
  const [validationError, setValidationError] = useState("");
  const [requestError, setRequestError] = useState(false);
  const availableAlternatives = alternativesFor(selected);
  const activeAlternative = availableAlternatives.includes(alternative) ? alternative : availableAlternatives[0] ?? "";
  const amount = Number(selected?.value);
  const alternativeValue = selected?.category === "electricity" ? (alternativeAmount === null ? amount : Number(alternativeAmount)) : amount;
  const supportedCategory = ["travel", "electricity", "food"].includes(selected?.category);
  const usageValid = Number.isFinite(amount) && amount > 0 && Number.isFinite(alternativeValue) && alternativeValue > 0;
  const unitValid = Boolean(selected?.unit);

  async function runSimulation(event) {
    event.preventDefault();
    setValidationError("");
    setRequestError(false);
    setSimulation(null);
    if (!selected || !supportedCategory) {
      setValidationError("Choose a recorded travel, electricity, or food activity to compare.");
      return;
    }
    if (!usageValid || !unitValid) {
      setValidationError("This activity needs a valid recorded amount and unit before it can be compared.");
      return;
    }
    if (!activeAlternative) {
      setValidationError("No supported alternative is available for this activity.");
      return;
    }
    if (selected.category === "electricity" && String(selected.unit).toLowerCase() === "hours" && alternativeValue > 24) {
      setValidationError("Electricity usage cannot exceed 24 hours per day.");
      return;
    }

    const alternativeActivity = selected.category === "electricity" ? activityName(selected) : activeAlternative;
    setSimulating(true);
    try {
      const response = await api.simulateWhatIf({
        category: selected.category,
        current: { activity: activityName(selected), amount, unit: selected.unit },
        alternative: { activity: alternativeActivity, amount: alternativeValue, unit: selected.unit },
      });
      const currentImpact = Number(response.current_kg_co2e ?? response.current_co2);
      const alternativeImpact = Number(response.new_kg_co2e ?? response.new_co2);
      if (!Number.isFinite(currentImpact) || !Number.isFinite(alternativeImpact)) throw new Error("Incomplete comparison response");
      setSimulation({
        currentImpact,
        alternativeImpact,
        reductionPercent: response.reduction_percent == null ? null : Number(response.reduction_percent),
        currentActivity: activityName(selected),
        alternativeActivity: selected.category === "electricity" ? "Reduced usage" : activeAlternative,
        currentAmount: amount,
        alternativeAmount: alternativeValue,
        unit: selected.unit,
      });
    } catch {
      setRequestError(true);
      setSimulation(null);
    } finally {
      setSimulating(false);
    }
  }

  return <section className="panel simulator-panel" id="simulator" aria-labelledby="simulator-heading">
    <div className="panel-heading"><div><span className="panel-eyebrow">PERSONALIZED TO YOUR LOGGED ACTIVITIES</span><h2 id="simulator-heading"><span className="sim-title-icon">✧</span> Impact Simulator</h2></div><span className="future-pill">WHAT-IF</span></div>
    <p className="sim-intro">See how a different choice could change the impact of an activity you recorded.</p>

    {loading ? <div className="simulator-state" role="status"><span className="coach-spinner"/> Loading your recent activities…</div>
      : error ? <div className="simulator-state error-state" role="alert"><span>Unable to load your activities. Please try again.</span><button className="simulator-retry" onClick={onRetry}>Try again</button></div>
        : activities.length === 0 ? <div className="simulator-empty"><span>🌱</span><div><strong>No activity available yet</strong><p>Add your first activity to explore how different choices could change your carbon impact.</p></div><button className="dashboard-extra-cta" onClick={onAddActivity}>Add Activity →</button></div>
          : <form onSubmit={runSimulation}>
            {activities.length > 1 && <label className="simulator-field"><span>Select activity</span><select value={selected ? String(selected.id) : ""} onChange={(event) => { onSelectActivity(event.target.value); setAlternative(""); setAlternativeAmount(""); setSimulation(null); setValidationError(""); setRequestError(false); }}><option value="">Choose a recorded activity</option>{activities.slice(0, 25).map((activity) => <option key={activity.id} value={String(activity.id)}>{activityOptionLabel(activity)}</option>)}</select></label>}
            {selected && <>
              {!supportedCategory ? <p className="simulator-validation" role="alert">This activity category is not supported by the What-If calculator.</p> : <>
                <div className="sim-controls">
                  <div className="sim-choice"><label>YOUR CURRENT ACTIVITY</label><div className="simulator-activity"><span className="sim-icon">{CATEGORY_ICON[selected.category]}</span><strong>{activityName(selected)}<small>· {fmt(amount, 2)} {unitName(selected.unit)}</small></strong></div><span className="sim-current-impact">Current impact · {fmt(selected.co2e, 2)} kg CO₂e</span></div>
                  <div className="sim-arrow" aria-hidden="true">→</div>
                  <div className="sim-choice"><label>CHANGE TO</label><div className="select-container"><span className="sim-icon transit-icon">⇢</span><select aria-label="Change activity to" value={activeAlternative} onChange={(event) => { setAlternative(event.target.value); setSimulation(null); setRequestError(false); }} disabled={!availableAlternatives.length}>{availableAlternatives.map((option) => <option key={option}>{option}</option>)}</select><span className="select-chevron">⌄</span></div>{selected.category === "electricity" && <label className="simulator-alt-usage">Alternative usage<input type="number" min="0.01" step="0.01" value={alternativeAmount ?? selected.value ?? ""} onChange={(event) => { setAlternativeAmount(event.target.value); setSimulation(null); setRequestError(false); }} /><span>{unitName(selected.unit)}</span></label>}</div>
                </div>
                {validationError && <p className="simulator-validation" role="alert">{validationError}</p>}
                {requestError && <p className="simulator-validation" role="alert">We couldn’t calculate this comparison. Please try again.</p>}
                <button className="simulate-button" type="submit" disabled={simulating || !supportedCategory || !usageValid || !unitValid || !activeAlternative}>{simulating ? "Calculating impact…" : "Simulate this change"}<span>↗</span></button>
                {simulation ? <div className="sim-result" role="status"><div className="sim-result-heading"><span className="panel-eyebrow">IMPACT COMPARISON</span></div><div className="sim-result-top"><div><small>CURRENT</small><strong>{simulation.currentImpact} <i>kg CO₂e</i></strong><span>{simulation.currentActivity} · {fmt(simulation.currentAmount, 2)} {unitName(simulation.unit)}</span></div><span className="result-arrow">→</span><div><small>ALTERNATIVE</small><strong>{simulation.alternativeImpact} <i>kg CO₂e</i></strong><span>{simulation.alternativeActivity} · {fmt(simulation.alternativeAmount, 2)} {unitName(simulation.unit)}</span></div></div><div className={`saving-callout ${simulation.currentImpact >= simulation.alternativeImpact ? "" : "sim-increase"}`}><span>{simulation.currentImpact >= simulation.alternativeImpact ? "↓" : "↑"}</span><div>{simulation.currentImpact >= simulation.alternativeImpact ? <><small>Potential reduction</small><strong>{fmt(simulation.currentImpact - simulation.alternativeImpact)} kg CO₂e</strong>{simulation.currentImpact > 0 && <small>{fmt(simulation.reductionPercent, 1)}% lower impact</small>}</> : <><small>This alternative would add</small><strong>{fmt(simulation.alternativeImpact - simulation.currentImpact)} kg CO₂e</strong>{simulation.currentImpact > 0 && <small>{fmt(Math.abs(simulation.reductionPercent), 1)}% higher impact</small>}</>}</div></div><small className="source-caption">Both values returned by the authenticated What-If API.</small><button className="plan-button" type="button" onClick={() => onAddToPlan(simulation.alternativeActivity)} disabled={planAdded}>{planAdded ? "Added to My Plan ✓" : "Add to My Plan →"}</button></div> : <div className="sim-placeholder"><span>✧</span> Select a supported alternative and simulate to compare API-calculated emissions.</div>}
              </>}
            </>}
          </form>}
  </section>;
}
