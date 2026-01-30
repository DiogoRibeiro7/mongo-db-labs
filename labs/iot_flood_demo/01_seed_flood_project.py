from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from pymongo import MongoClient


@dataclass(frozen=True)
class MongoConfig:
    # MongoDB connection configuration.
    uri: str = "mongodb://localhost:27017"
    db_name: str = "iot_flood_demo"


def utc_now() -> datetime:
    # Return a timezone-aware UTC timestamp.
    return datetime.now(timezone.utc)


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def seed(cfg: MongoConfig) -> Dict[str, Any]:
    client = MongoClient(cfg.uri)
    db = client[cfg.db_name]

    # Clean for repeatable teaching runs
    for col in ["sites", "sensors", "ratingCurves", "samplingPolicies", "policyState", "alerts", "measurements"]:
        db[col].delete_many({})

    created_at = utc_now()

    # -----------------------
    # Sites (2 rivers, 2 stormwater, 2 rain gauges)
    # -----------------------
    sites = [
        {
            "siteCode": "RIVER_001",
            "siteType": "river",
            "name": "River A - Bridge",
            "catchmentId": "CATCH_01",
            "geo": {"type": "Point", "coordinates": [-8.610, 41.150]},
            "thresholds": {
                "watchLevelM": 1.40,
                "warningLevelM": 1.70,
                "severeLevelM": 2.00,
                "surchargeLevelM": None,
                "overflowLevelM": None,
            },
            "createdAt": created_at,
        },
        {
            "siteCode": "RIVER_002",
            "siteType": "river",
            "name": "River B - Mill",
            "catchmentId": "CATCH_02",
            "geo": {"type": "Point", "coordinates": [-8.620, 41.160]},
            "thresholds": {
                "watchLevelM": 1.10,
                "warningLevelM": 1.35,
                "severeLevelM": 1.60,
                "surchargeLevelM": None,
                "overflowLevelM": None,
            },
            "createdAt": created_at,
        },
        {
            "siteCode": "SW_001",
            "siteType": "stormwater",
            "name": "Stormwater Node 1",
            "catchmentId": "CATCH_01",
            "geo": {"type": "Point", "coordinates": [-8.605, 41.145]},
            "thresholds": {
                "watchLevelM": None,
                "warningLevelM": None,
                "severeLevelM": None,
                "surchargeLevelM": 0.55,
                "overflowLevelM": 0.80,
            },
            "createdAt": created_at,
        },
        {
            "siteCode": "SW_002",
            "siteType": "stormwater",
            "name": "Stormwater Node 2",
            "catchmentId": "CATCH_02",
            "geo": {"type": "Point", "coordinates": [-8.625, 41.165]},
            "thresholds": {
                "watchLevelM": None,
                "warningLevelM": None,
                "severeLevelM": None,
                "surchargeLevelM": 0.45,
                "overflowLevelM": 0.70,
            },
            "createdAt": created_at,
        },
        {
            "siteCode": "RG_001",
            "siteType": "rain_gauge",
            "name": "Rain Gauge Catchment 1",
            "catchmentId": "CATCH_01",
            "geo": {"type": "Point", "coordinates": [-8.607, 41.148]},
            "thresholds": {
                "watchLevelM": None,
                "warningLevelM": None,
                "severeLevelM": None,
                "surchargeLevelM": None,
                "overflowLevelM": None,
            },
            "createdAt": created_at,
        },
        {
            "siteCode": "RG_002",
            "siteType": "rain_gauge",
            "name": "Rain Gauge Catchment 2",
            "catchmentId": "CATCH_02",
            "geo": {"type": "Point", "coordinates": [-8.623, 41.162]},
            "thresholds": {
                "watchLevelM": None,
                "warningLevelM": None,
                "severeLevelM": None,
                "surchargeLevelM": None,
                "overflowLevelM": None,
            },
            "createdAt": created_at,
        },
    ]

    site_ids = db.sites.insert_many(sites).inserted_ids
    site_by_code = {sites[i]["siteCode"]: site_ids[i] for i in range(len(sites))}

    # -----------------------
    # Sensors per site
    # -----------------------
    sensors: List[Dict[str, Any]] = []

    def add_sensor(site_code: str, metric: str, unit: str, model: str, power_type: str = "battery") -> None:
        _require(site_code in site_by_code, f"Unknown site_code: {site_code}")
        sensors.append(
            {
                "siteId": site_by_code[site_code],
                "sensorCode": f"{metric.upper()}_{site_code}",
                "metric": metric,
                "unit": unit,
                "hardware": {"model": model, "vendor": "Demo"},
                "powerType": power_type,
                "installedAt": created_at,
                "status": "active",
            }
        )

    for code in ["RIVER_001", "RIVER_002"]:
        add_sensor(code, "waterLevelM", "m", "RadarLevelX")
        add_sensor(code, "flowVelocityMps", "m/s", "DopplerV1")
        add_sensor(code, "flowRateM3s", "m3/s", "Derived", power_type="mains")

    for code in ["SW_001", "SW_002"]:
        add_sensor(code, "waterLevelM", "m", "PressureLevelP1")
        add_sensor(code, "flowVelocityMps", "m/s", "DopplerV1")
        add_sensor(code, "flowRateM3s", "m3/s", "Derived", power_type="mains")

    for code in ["RG_001", "RG_002"]:
        add_sensor(code, "rainfallRateMmh", "mm/h", "TippingBucketR1")
        add_sensor(code, "rainfallAccumMm", "mm", "TippingBucketR1")

    db.sensors.insert_many(sensors)

    # -----------------------
    # Rating curves
    # -----------------------
    curves = [
        {
            "siteId": site_by_code["RIVER_001"],
            "curveType": "powerLaw",
            "version": 1,
            "validFrom": created_at,
            "validTo": None,
            "params": {"a": 18.0, "h0": 0.35, "b": 1.85},
            "range": {"minLevelM": 0.40, "maxLevelM": 2.50},
            "updatedAt": created_at,
        },
        {
            "siteId": site_by_code["RIVER_002"],
            "curveType": "powerLaw",
            "version": 1,
            "validFrom": created_at,
            "validTo": None,
            "params": {"a": 12.0, "h0": 0.25, "b": 2.05},
            "range": {"minLevelM": 0.30, "maxLevelM": 2.00},
            "updatedAt": created_at,
        },
        {
            "siteId": site_by_code["SW_001"],
            "curveType": "powerLaw",
            "version": 1,
            "validFrom": created_at,
            "validTo": None,
            "params": {"a": 2.5, "h0": 0.05, "b": 1.60},
            "range": {"minLevelM": 0.05, "maxLevelM": 1.00},
            "updatedAt": created_at,
        },
        {
            "siteId": site_by_code["SW_002"],
            "curveType": "powerLaw",
            "version": 1,
            "validFrom": created_at,
            "validTo": None,
            "params": {"a": 2.0, "h0": 0.05, "b": 1.55},
            "range": {"minLevelM": 0.05, "maxLevelM": 0.90},
            "updatedAt": created_at,
        },
    ]
    db.ratingCurves.insert_many(curves)

    # -----------------------
    # Sampling policies + initial policyState
    # -----------------------
    base_policy: Dict[str, Any] = {
        "enabled": True,
        "modes": {
            "LOW": {"intervalSec": 900, "minDurationSec": 1800},
            "NORMAL": {"intervalSec": 300, "minDurationSec": 900},
            "HIGH": {"intervalSec": 60, "minDurationSec": 900},
            "CRITICAL": {"intervalSec": 10, "minDurationSec": 600},
        },
        "hysteresisMarginM": 0.05,
        "cooldownSec": 300,
        "batteryConstraints": {"lowBatteryPct": 20, "forbidCriticalBelowPct": 15},
        "triggers": {
            "rainfallHighMmh": 8.0,
            "rainfallMediumMmh": 2.0,
            "riseHighMperMin": 0.03,
            "riseCriticalMperMin": 0.06,
        },
        "updatedAt": created_at,
    }

    for site_code, site_id in site_by_code.items():
        db.samplingPolicies.insert_one({"siteId": site_id, **base_policy})
        db.policyState.insert_one(
            {
                "siteId": site_id,
                "currentMode": "NORMAL",
                "lastChangeTs": created_at,
                "lastDecisionReason": "INIT",
                "cooldownUntilTs": created_at,
                "batteryPctLast": 100,
                "updatedAt": created_at,
            }
        )

    return {"siteByCode": {k: str(v) for k, v in site_by_code.items()}, "sensorCount": len(sensors)}


if __name__ == "__main__":
    out = seed(MongoConfig())
    print("✅ Seed complete")
    print(out)
