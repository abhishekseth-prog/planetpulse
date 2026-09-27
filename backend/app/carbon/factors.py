"""Centralized emission factors repository for PlanetPulse.

Every factor represents the greenhouse gas emissions (in kg CO2e) per unit of activity.
Sources and assumptions are explicitly documented for every factor.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class EmissionFactor:
    """Metadata and conversion factor for a specific activity and unit."""
    category: str
    activity: str
    unit: str
    factor: float  # kg CO2e per 1 unit
    co2e_unit: str = "kg CO2e"
    source: str = ""
    assumptions: str = ""
    is_assumption: bool = False


# Centralized dictionary keyed by (activity, unit) in lowercase.
EMISSION_FACTORS: Dict[Tuple[str, str], EmissionFactor] = {
    # -------------------------------------------------------------------------
    # TRAVEL CATEGORY
    # -------------------------------------------------------------------------
    ("car", "km"): EmissionFactor(
        category="travel",
        activity="car",
        unit="km",
        factor=0.21,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Average petrol passenger car)",
        assumptions="Average passenger combustion car under mixed urban and highway driving (~0.21 kg CO2e/km).",
        is_assumption=False,
    ),
    ("car", "miles"): EmissionFactor(
        category="travel",
        activity="car",
        unit="miles",
        factor=0.33796,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Converted: 1 mile = 1.60934 km)",
        assumptions="Average passenger car conversion factor scaled to miles (0.21 * 1.60934).",
        is_assumption=False,
    ),
    ("bus", "km"): EmissionFactor(
        category="travel",
        activity="bus",
        unit="km",
        factor=0.10,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Average local bus)",
        assumptions="Average passenger bus occupancy in urban/suburban transit.",
        is_assumption=False,
    ),
    ("bus", "miles"): EmissionFactor(
        category="travel",
        activity="bus",
        unit="miles",
        factor=0.16093,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Converted: 1 mile = 1.60934 km)",
        assumptions="Average local bus per passenger-mile.",
        is_assumption=False,
    ),
    ("train", "km"): EmissionFactor(
        category="travel",
        activity="train",
        unit="km",
        factor=0.04,
        source="UK DEFRA / DESNZ GHG Conversion Factors (National / regional rail)",
        assumptions="National rail passenger-km average grid mix.",
        is_assumption=False,
    ),
    ("train", "miles"): EmissionFactor(
        category="travel",
        activity="train",
        unit="miles",
        factor=0.06437,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Converted: 1 mile = 1.60934 km)",
        assumptions="National rail passenger-mile.",
        is_assumption=False,
    ),
    ("metro", "km"): EmissionFactor(
        category="travel",
        activity="metro",
        unit="km",
        factor=0.03,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Light rail and metro)",
        assumptions="Standard electrified rapid transit / subway passenger-km.",
        is_assumption=False,
    ),
    ("metro", "miles"): EmissionFactor(
        category="travel",
        activity="metro",
        unit="miles",
        factor=0.04828,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Converted: 1 mile = 1.60934 km)",
        assumptions="Standard electrified rapid transit per passenger-mile.",
        is_assumption=False,
    ),
    ("flight", "km"): EmissionFactor(
        category="travel",
        activity="flight",
        unit="km",
        factor=0.25,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Domestic & short-haul passenger flight)",
        assumptions="Economy passenger including radiative forcing factor.",
        is_assumption=False,
    ),
    ("flight", "miles"): EmissionFactor(
        category="travel",
        activity="flight",
        unit="miles",
        factor=0.40234,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Converted: 1 mile = 1.60934 km)",
        assumptions="Economy passenger flight per passenger-mile.",
        is_assumption=False,
    ),
    ("plane", "km"): EmissionFactor(
        category="travel",
        activity="plane",
        unit="km",
        factor=0.25,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Alias for flight)",
        assumptions="Economy passenger including radiative forcing factor.",
        is_assumption=False,
    ),
    ("plane", "miles"): EmissionFactor(
        category="travel",
        activity="plane",
        unit="miles",
        factor=0.40234,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Converted: 1 mile = 1.60934 km)",
        assumptions="Economy passenger flight per passenger-mile.",
        is_assumption=False,
    ),
    ("motorcycle", "km"): EmissionFactor(
        category="travel",
        activity="motorcycle",
        unit="km",
        factor=0.11,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Medium motorbike)",
        assumptions="Average petrol motorcycle.",
        is_assumption=False,
    ),
    ("motorcycle", "miles"): EmissionFactor(
        category="travel",
        activity="motorcycle",
        unit="miles",
        factor=0.17703,
        source="UK DEFRA / DESNZ GHG Conversion Factors (Converted: 1 mile = 1.60934 km)",
        assumptions="Average petrol motorcycle per mile.",
        is_assumption=False,
    ),
    ("bike", "km"): EmissionFactor(
        category="travel",
        activity="bike",
        unit="km",
        factor=0.0,
        source="Zero operational tailpipe emission standard",
        assumptions="Direct operational emissions only (human powered).",
        is_assumption=False,
    ),
    ("bike", "miles"): EmissionFactor(
        category="travel",
        activity="bike",
        unit="miles",
        factor=0.0,
        source="Zero operational tailpipe emission standard",
        assumptions="Direct operational emissions only (human powered).",
        is_assumption=False,
    ),
    ("walk", "km"): EmissionFactor(
        category="travel",
        activity="walk",
        unit="km",
        factor=0.0,
        source="Zero operational tailpipe emission standard",
        assumptions="Direct operational emissions only (human walking).",
        is_assumption=False,
    ),
    ("walk", "miles"): EmissionFactor(
        category="travel",
        activity="walk",
        unit="miles",
        factor=0.0,
        source="Zero operational tailpipe emission standard",
        assumptions="Direct operational emissions only (human walking).",
        is_assumption=False,
    ),

    # -------------------------------------------------------------------------
    # ELECTRICITY CATEGORY
    # Baseline grid electricity emission intensity: 0.45 kg CO2e / kWh
    # Source: IEA (International Energy Agency) global average grid emission factor
    # -------------------------------------------------------------------------
    ("ac", "kwh"): EmissionFactor(
        category="electricity",
        activity="ac",
        unit="kwh",
        factor=0.45,
        source="IEA Global Average Electricity Grid Intensity (~0.45 kg CO2e/kWh)",
        assumptions="Direct electricity consumption at grid factor.",
        is_assumption=False,
    ),
    ("ac", "hours"): EmissionFactor(
        category="electricity",
        activity="ac",
        unit="hours",
        factor=0.675,
        source="Project Assumption (1.5 kW rating × 0.45 kg CO2e/kWh grid intensity)",
        assumptions="Assumes residential 1.5-ton AC unit with 1.5 kW average continuous power draw.",
        is_assumption=True,
    ),
    ("fan", "kwh"): EmissionFactor(
        category="electricity",
        activity="fan",
        unit="kwh",
        factor=0.45,
        source="IEA Global Average Electricity Grid Intensity (~0.45 kg CO2e/kWh)",
        assumptions="Direct electricity consumption at grid factor.",
        is_assumption=False,
    ),
    ("fan", "hours"): EmissionFactor(
        category="electricity",
        activity="fan",
        unit="hours",
        factor=0.027,
        source="Project Assumption (0.06 kW rating × 0.45 kg CO2e/kWh grid intensity)",
        assumptions="Assumes standard 60W ceiling or standing fan.",
        is_assumption=True,
    ),
    ("heater", "kwh"): EmissionFactor(
        category="electricity",
        activity="heater",
        unit="kwh",
        factor=0.45,
        source="IEA Global Average Electricity Grid Intensity (~0.45 kg CO2e/kWh)",
        assumptions="Direct electricity consumption at grid factor.",
        is_assumption=False,
    ),
    ("heater", "hours"): EmissionFactor(
        category="electricity",
        activity="heater",
        unit="hours",
        factor=0.675,
        source="Project Assumption (1.5 kW rating × 0.45 kg CO2e/kWh grid intensity)",
        assumptions="Assumes standard 1500W electric resistance space heater.",
        is_assumption=True,
    ),
    ("lighting", "kwh"): EmissionFactor(
        category="electricity",
        activity="lighting",
        unit="kwh",
        factor=0.45,
        source="IEA Global Average Electricity Grid Intensity (~0.45 kg CO2e/kWh)",
        assumptions="Direct electricity consumption at grid factor.",
        is_assumption=False,
    ),
    ("lighting", "hours"): EmissionFactor(
        category="electricity",
        activity="lighting",
        unit="hours",
        factor=0.0135,
        source="Project Assumption (0.03 kW rating × 0.45 kg CO2e/kWh grid intensity)",
        assumptions="Assumes 30W average active residential LED/CFL lighting.",
        is_assumption=True,
    ),
    ("refrigerator", "kwh"): EmissionFactor(
        category="electricity",
        activity="refrigerator",
        unit="kwh",
        factor=0.45,
        source="IEA Global Average Electricity Grid Intensity (~0.45 kg CO2e/kWh)",
        assumptions="Direct electricity consumption at grid factor.",
        is_assumption=False,
    ),
    ("refrigerator", "hours"): EmissionFactor(
        category="electricity",
        activity="refrigerator",
        unit="hours",
        factor=0.045,
        source="Project Assumption (0.10 kW rating × 0.45 kg CO2e/kWh grid intensity)",
        assumptions="Assumes typical refrigerator compressor duty cycle average 100W.",
        is_assumption=True,
    ),
    ("computer", "kwh"): EmissionFactor(
        category="electricity",
        activity="computer",
        unit="kwh",
        factor=0.45,
        source="IEA Global Average Electricity Grid Intensity (~0.45 kg CO2e/kWh)",
        assumptions="Direct electricity consumption at grid factor.",
        is_assumption=False,
    ),
    ("computer", "hours"): EmissionFactor(
        category="electricity",
        activity="computer",
        unit="hours",
        factor=0.0675,
        source="Project Assumption (0.15 kW rating × 0.45 kg CO2e/kWh grid intensity)",
        assumptions="Assumes desktop or laptop + external monitor drawing 150W under active use.",
        is_assumption=True,
    ),
    ("tv", "kwh"): EmissionFactor(
        category="electricity",
        activity="tv",
        unit="kwh",
        factor=0.45,
        source="IEA Global Average Electricity Grid Intensity (~0.45 kg CO2e/kWh)",
        assumptions="Direct electricity consumption at grid factor.",
        is_assumption=False,
    ),
    ("tv", "hours"): EmissionFactor(
        category="electricity",
        activity="tv",
        unit="hours",
        factor=0.045,
        source="Project Assumption (0.10 kW rating × 0.45 kg CO2e/kWh grid intensity)",
        assumptions="Assumes 100W average television active power draw.",
        is_assumption=True,
    ),
    ("appliances", "kwh"): EmissionFactor(
        category="electricity",
        activity="appliances",
        unit="kwh",
        factor=0.45,
        source="IEA Global Average Electricity Grid Intensity (~0.45 kg CO2e/kWh)",
        assumptions="Direct electricity consumption at grid factor.",
        is_assumption=False,
    ),
    ("appliances", "hours"): EmissionFactor(
        category="electricity",
        activity="appliances",
        unit="hours",
        factor=0.225,
        source="Project Assumption (0.50 kW rating × 0.45 kg CO2e/kWh grid intensity)",
        assumptions="Blended household appliance power draw assumption (500W).",
        is_assumption=True,
    ),

    # -------------------------------------------------------------------------
    # FOOD CATEGORY
    # References: Poore & Nemecek (2018), Science; Our World in Data
    # -------------------------------------------------------------------------
    ("chicken_meal", "meal"): EmissionFactor(
        category="food",
        activity="chicken_meal",
        unit="meal",
        factor=1.8,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Average poultry meal serving (~200g portion + accompaniments).",
        is_assumption=False,
    ),
    ("chicken_meal", "servings"): EmissionFactor(
        category="food",
        activity="chicken_meal",
        unit="servings",
        factor=1.8,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Single serving of chicken meal.",
        is_assumption=False,
    ),
    ("chicken_meal", "kg"): EmissionFactor(
        category="food",
        activity="chicken_meal",
        unit="kg",
        factor=7.0,
        source="Poore & Nemecek (2018), Science (Poultry meat ~6-9 kg CO2e/kg)",
        assumptions="Average emissions per kilogram of retail poultry meat.",
        is_assumption=False,
    ),
    ("beef_meal", "meal"): EmissionFactor(
        category="food",
        activity="beef_meal",
        unit="meal",
        factor=6.5,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Standard beef meal serving (~150g portion).",
        is_assumption=False,
    ),
    ("beef_meal", "servings"): EmissionFactor(
        category="food",
        activity="beef_meal",
        unit="servings",
        factor=6.5,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Single serving of beef meal.",
        is_assumption=False,
    ),
    ("beef_meal", "kg"): EmissionFactor(
        category="food",
        activity="beef_meal",
        unit="kg",
        factor=60.0,
        source="Poore & Nemecek (2018), Science (Beef herd average ~60 kg CO2e/kg)",
        assumptions="Average emissions per kilogram of retail beef meat.",
        is_assumption=False,
    ),
    ("fish_meal", "meal"): EmissionFactor(
        category="food",
        activity="fish_meal",
        unit="meal",
        factor=1.4,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Average seafood / fish meal serving (~150g portion).",
        is_assumption=False,
    ),
    ("fish_meal", "servings"): EmissionFactor(
        category="food",
        activity="fish_meal",
        unit="servings",
        factor=1.4,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Single serving of fish meal.",
        is_assumption=False,
    ),
    ("fish_meal", "kg"): EmissionFactor(
        category="food",
        activity="fish_meal",
        unit="kg",
        factor=5.5,
        source="Poore & Nemecek (2018), Science (Farmed & wild marine fish average)",
        assumptions="Average emissions per kilogram of fish.",
        is_assumption=False,
    ),
    ("vegetarian_meal", "meal"): EmissionFactor(
        category="food",
        activity="vegetarian_meal",
        unit="meal",
        factor=0.8,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Lacto-ovo vegetarian meal (dairy, grains, legumes, vegetables).",
        is_assumption=False,
    ),
    ("vegetarian_meal", "servings"): EmissionFactor(
        category="food",
        activity="vegetarian_meal",
        unit="servings",
        factor=0.8,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Single serving of vegetarian meal.",
        is_assumption=False,
    ),
    ("vegetarian_meal", "kg"): EmissionFactor(
        category="food",
        activity="vegetarian_meal",
        unit="kg",
        factor=3.0,
        source="Poore & Nemecek (2018), Science",
        assumptions="Composite kilogram of mixed vegetarian food products.",
        is_assumption=False,
    ),
    ("vegan_meal", "meal"): EmissionFactor(
        category="food",
        activity="vegan_meal",
        unit="meal",
        factor=0.5,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="100% plant-based meal (legumes, grains, tubers, vegetables).",
        is_assumption=False,
    ),
    ("vegan_meal", "servings"): EmissionFactor(
        category="food",
        activity="vegan_meal",
        unit="servings",
        factor=0.5,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Single serving of vegan meal.",
        is_assumption=False,
    ),
    ("vegan_meal", "kg"): EmissionFactor(
        category="food",
        activity="vegan_meal",
        unit="kg",
        factor=2.0,
        source="Poore & Nemecek (2018), Science",
        assumptions="Composite kilogram of plant-based whole food ingredients.",
        is_assumption=False,
    ),
    ("dairy", "meal"): EmissionFactor(
        category="food",
        activity="dairy",
        unit="meal",
        factor=0.6,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Standard dairy portion (milk, cheese, yogurt equivalent).",
        is_assumption=False,
    ),
    ("dairy", "servings"): EmissionFactor(
        category="food",
        activity="dairy",
        unit="servings",
        factor=0.6,
        source="Poore & Nemecek (2018), Science; Our World in Data",
        assumptions="Single dairy serving.",
        is_assumption=False,
    ),
    ("dairy", "kg"): EmissionFactor(
        category="food",
        activity="dairy",
        unit="kg",
        factor=3.5,
        source="Poore & Nemecek (2018), Science (Blended milk and dairy products)",
        assumptions="Average kilogram of mixed dairy products.",
        is_assumption=False,
    ),
}


def get_emission_factor(activity: str, unit: str) -> Optional[EmissionFactor]:
    """Retrieve the emission factor metadata for an activity and unit pair."""
    key = (activity.strip().lower(), unit.strip().lower())
    return EMISSION_FACTORS.get(key)


def get_supported_activities() -> List[str]:
    """Return all unique supported activity names."""
    return sorted(list({key[0] for key in EMISSION_FACTORS.keys()}))


def get_supported_units_for_activity(activity: str) -> List[str]:
    """Return all supported units for a given activity."""
    act_norm = activity.strip().lower()
    return sorted([key[1] for key in EMISSION_FACTORS.keys() if key[0] == act_norm])
