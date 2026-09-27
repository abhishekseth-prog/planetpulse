# PlanetPulse — decisions and assumptions

## Decision 1 — Keep one emission calculation engine

Activity creation and What-if scenarios both call `backend/services/calculator.py`. Factors live centrally in `backend/carbon/factors.py` and can be overridden using `PLANETPULSE_FACTOR_*` environment variables. This keeps the scenario comparison consistent with recorded activities and avoids carbon formulas in route handlers.

## Decision 2 — Treat emission values as transparent screening estimates

The factors are estimates for a hackathon prototype; they are not a personal carbon audit. Electricity defaults to 0.716 kg CO2 per kWh, based on the Central Electricity Authority's Indian power-sector weighted-average grid factor reported in its Version 19 database for FY 2022–23. This is a dated national average and should be updated to the latest CEA dataset before public/production use. CEA's current baseline database landing page publishes newer versions: https://cea.nic.in/cdm-co2-baseline-database/?lang=en Appliance-hour inputs are converted with explicit typical draw assumptions (AC 1.2 kWh/hour, lighting 0.08, refrigerator 0.12, other appliance 0.5); users with measured kWh should submit kWh directly.

Travel defaults (car 0.29, metro 0.105, bus 0.10 kg CO2e per km) are prototype per-passenger estimates calibrated to the supplied What-if example (20 km car = 5.8 kg and metro = 2.1 kg). They are intentionally explicit/configurable, not claimed as an official India fleet average. Government conversion-factor datasets such as UK DESNZ's annual GHG factors publish mode-specific passenger-km references, but factors depend on geography, occupancy, fleet, and boundary: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026

Meal defaults (plant-based 0.5, chicken 1.5, dairy 1.2, beef 5.0 kg CO2e per meal) are serving-level prototype assumptions, not direct values from a single global meal database. Their relative ordering follows global food life-cycle evidence. Our World in Data documents that its food-impact data is based on Poore & Nemecek's meta-analysis of 38,700 farms and 40 products and reports per-product footprints, not standardized prepared meals: https://ourworldindata.org/environmental-impacts-of-food

Bike and walking are assigned zero direct activity emissions in this prototype; lifecycle impacts of vehicles, food consumed, and infrastructure are outside this simplified boundary.

## Decision 3 — Preserve the team's API contract and existing database

The API is available at both `/api/...` (team contract) and root paths (existing frontend compatibility). Activity requests accept both canonical (`activity`, `amount`, `date`) and previously integrated frontend (`activity_type`, `value`, `activity_date`) names. Existing MySQL `activities` and `carbon_records` tables remain the activity store; `users` and `user_goals` tables are added when needed. Registration/login use scrypt password hashes and signed JWT bearer tokens. Private API handlers derive the user ID from the validated token so activities, goals, dashboard totals, trends, and insights are scoped to that account. Legacy users migrated from existing rows receive disabled local-only accounts rather than having their history reassigned. The additive migration widens old two-decimal activity and carbon columns to three decimals without dropping rows.

## Other product boundaries

- Dashboard figures and trends are aggregated for the current month/date range from persisted activities.
- Month-over-month change is unavailable when there is no prior-month emission baseline; the API returns `null` and the UI shows an empty comparison state.
- Monthly comparison labels the current month-to-date total separately from the previous full calendar month and derives all values in the authenticated dashboard query.
- The Planet Pulse Carbon Score is a product metric, not an official environmental rating: `70% × max(0, 100 − monthly goal usage percent) + 30% × min(100, distinct activity days this month ÷ elapsed days this month × 100)`, rounded to a whole number. It is shown only after an activity has been logged this month.
- Category comparisons use current-month and previous-calendar-month emissions for the same category. A comparison is omitted when that category has no previous-month emissions.
- What-if monthly savings multiply the per-day difference by 30.
- AI insight generation and action-plan logic remain Person 3's responsibility.
- API errors do not return SQL or database-driver details.
