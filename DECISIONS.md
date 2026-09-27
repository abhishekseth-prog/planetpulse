# PlanetPulse — Decision Points

PlanetPulse is a personal carbon-footprint tracking application that helps users understand the impact of their everyday choices and identify practical ways to reduce their footprint.

This document explains three important product and engineering decisions made while building PlanetPulse.

---

## Decision Point 1 — Deterministic Carbon Calculation

### Decision

We chose a deterministic carbon-calculation system based on predefined emission factors rather than generating carbon estimates dynamically.

### Why

Carbon calculations need to be predictable and reproducible. If a user logs the same activity twice with the same inputs, the estimated carbon footprint should remain consistent.

A deterministic calculation engine also makes the results easier to test, explain, and connect with other parts of the product.

### What we considered

**Option 1 — Dynamic or AI-generated estimates**

This could provide flexible estimates, but the same activity could potentially produce different results and would be harder to validate consistently.

**Option 2 — Predefined emission factors**

This provides predictable calculations and allows the same calculation logic to be reused throughout the application.

### Outcome

We implemented a deterministic carbon-calculation engine using predefined emission factors.

The same calculation logic is used when activities are logged and when users compare choices in the What-if Impact Simulator.

This keeps the carbon calculations consistent across PlanetPulse.

---

## Decision Point 2 — Connecting the What-if Simulator to User Activities

### Decision

We chose to connect the What-if Impact Simulator with the user's actual activity data instead of relying only on predefined example scenarios.

### Why

A generic simulator can show the difference between two choices, but it does not necessarily reflect the choices a particular user is making.

By connecting the simulator to the user's logged activities, PlanetPulse can help users understand the potential impact of changing one of their actual choices.

For example, a user who regularly logs car travel can compare that activity with an alternative transportation choice.

### What we considered

**Option 1 — Generic scenarios**

Predefined scenarios would be simpler to implement, but the results would be less connected to the user's personal footprint.

**Option 2 — User-linked scenarios**

Using the user's existing activity data makes the simulation more relevant and connects the simulator with the rest of the application.

### Outcome

The What-if Simulator uses the user's activity information to compare a current choice with an alternative.

It calculates:

- Current carbon impact
- Alternative carbon impact
- Carbon saved
- Percentage reduction
- Estimated monthly impact

This allows users to understand the potential effect of changing a real behavior rather than only viewing a generic example.

---

## Decision Point 3 — Rule-Based Carbon Coach

### Decision

We chose a rule-based Carbon Coach that generates recommendations using the user's actual carbon-footprint data.

### Why

The main purpose of the Carbon Coach is to turn carbon data into practical actions.

Instead of providing generic environmental advice, the Carbon Coach looks at the user's carbon contributors and identifies areas where a change could have a meaningful impact.

A rule-based approach also keeps the recommendations predictable, explainable, and independent of external AI services.

### What we considered

**Option 1 — Generic recommendations**

Generic recommendations would be easier to implement, but they would not be strongly connected to the user's actual footprint.

**Option 2 — Rule-based recommendations based on user data**

This allows recommendations to be generated from the user's actual carbon contribution while keeping the logic predictable and understandable.

### Outcome

The Carbon Coach identifies the user's largest carbon contributor and provides relevant actions based on that information.

The recommendations are connected to the user's logged activities and carbon calculations.

This makes the Carbon Coach part of the product's decision-support flow rather than a separate generic information section.

---

## Summary

The three decisions were made to keep PlanetPulse:

1. **Consistent** — carbon calculations produce predictable results.
2. **Personalized** — the What-if Simulator works with the user's actual activity data.
3. **Actionable** — the Carbon Coach turns the user's footprint data into practical recommendations.

These choices were made to ensure that the five core product features work together as one end-to-end carbon-tracking experience.
