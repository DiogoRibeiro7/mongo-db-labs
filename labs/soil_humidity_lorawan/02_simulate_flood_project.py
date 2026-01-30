from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from pymongo import MongoClient


@dataclass(frozen=True)
class MongoConfig:
    uri: str = "mongodb://localhost:27017"
    db_name: str = "iot_flood_demo"


@dataclass(frozen=True)
class SimConfig:
    hours: int
    base_step_sec: int
    seed: int
    batch_size: int = 5000


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _power_law_flow(level_m: float, a: float, h0: float, b: float) -> float:
    # Rating curve: Q = a * (h - h0)^b, clipped at zero.
    x = max(0.0, level_m - h0)
    return a * (x**b)


def _qc_flags(metric: str, value: float) -> List[str]:
    # Simple QC flags for teaching.
    flags: List[str] = []
    if metric == "waterLevelM" and not (0.0 <= value <= 5.0):
        flags.append("RANGE_VIOLATION")
    if metric == "flowVelocityMps" and not (0.0 <= value <= 5.0):
        flags.append("RANGE_VIOLATION")
    if metric == "rainfallRateMmh" and not (0.0 <= value <= 200.0):
        flags.append("RANGE_VIOLATION")
    if not flags:
        flags.append("OK")
    return flags


def _mode_rank(mode: str) -> int:
    return {"LOW": 0, "NORMAL": 1, "HIGH": 2, "CRITICAL": 3}[mode]


def _mode_from_rank(rank: int) -> str:
    return ["LOW", "NORMAL", "HIGH", "CRITICAL"][max(0, min(3, rank))]


def _decide_mode(
    *,
    site: Dict[str, Any],
    policy: Dict[str, Any],
    state: Dict[str, Any],
    now_ts: datetime,
    water_level_m: Optional[float],
    dlevel_dt_m_per_min: Optional[float],
    rainfall_rate_mmh: float,
    battery_pct: float,
) -> Tuple[str, str, datetime]:
    # Decide sampling mode with:
    # - site thresholds (river vs stormwater)
    # - rise rate and rainfall triggers
    # - cooldown + min duration + hysteresis
    # - battery constraints
    modes = policy["modes"]
    hyst = float(policy.get("hysteresisMarginM", 0.05))
    cooldown_sec = int(policy.get("cooldownSec", 300))
    triggers = policy["triggers"]
    bc = policy["batteryConstraints"]

    current_mode = str(state["currentMode"])
    last_change_ts: datetime = state["lastChangeTs"]
    cooldown_until_ts: datetime = state.get("cooldownUntilTs", last_change_ts)

    if now_ts < cooldown_until_ts:
        return current_mode, "COOLDOWN", cooldown_until_ts

    min_dur = int(modes[current_mode]["minDurationSec"])
    if (now_ts - last_change_ts).total_seconds() < min_dur:
        return current_mode, "MIN_DURATION", cooldown_until_ts

    forbid_critical = battery_pct < float(bc["forbidCriticalBelowPct"])
    rank = _mode_rank(current_mode)

    if rainfall_rate_mmh >= float(triggers["rainfallHighMmh"]):
        rank = max(rank, 2)
    elif rainfall_rate_mmh >= float(triggers["rainfallMediumMmh"]):
        rank = max(rank, 1)

    if dlevel_dt_m_per_min is not None:
        if dlevel_dt_m_per_min >= float(triggers["riseCriticalMperMin"]):
            rank = max(rank, 3)
        elif dlevel_dt_m_per_min >= float(triggers["riseHighMperMin"]):
            rank = max(rank, 2)

    st = site["siteType"]
    thr = site["thresholds"]

    if water_level_m is not None:
        if st == "river":
            watch = float(thr["watchLevelM"])
            warn = float(thr["warningLevelM"])
            sev = float(thr["severeLevelM"])
            if water_level_m >= sev:
                rank = max(rank, 3)
            elif water_level_m >= warn:
                rank = max(rank, 2)
            elif water_level_m >= watch:
                rank = max(rank, 1)

            if water_level_m < (watch - hyst) and rainfall_rate_mmh < 1.0:
                rank = min(rank, 1)

        else:
            sur = float(thr["surchargeLevelM"])
            ovf = float(thr["overflowLevelM"])
            if water_level_m >= ovf:
                rank = max(rank, 3)
            elif water_level_m >= sur:
                rank = max(rank, 2)

            if water_level_m < (sur - hyst) and rainfall_rate_mmh < 1.0:
                rank = min(rank, 1)

    if forbid_critical and rank == 3:
        rank = 2

    if battery_pct < float(bc["lowBatteryPct"]) and rank >= 2 and rainfall_rate_mmh < 1.0:
        rank = 1

    new_mode = _mode_from_rank(rank)
    if new_mode == current_mode:
        return current_mode, "NO_CHANGE", cooldown_until_ts

    reason = f"MODE_CHANGE:{current_mode}->{new_mode}"
    new_cooldown_until = now_ts + timedelta(seconds=cooldown_sec)
    return new_mode, reason, new_cooldown_until


def _alert_type_for_site(site: Dict[str, Any], water_level_m: Optional[float]) -> Optional[Tuple[str, str]]:
    if water_level_m is None:
        return None

    st = site["siteType"]
    thr = site["thresholds"]

    if st == "river":
        watch = float(thr["watchLevelM"])
        warn = float(thr["warningLevelM"])
        sev = float(thr["severeLevelM"])
        if water_level_m >= sev:
            return "FLOOD_SEVERE", "critical"
        if water_level_m >= warn:
            return "FLOOD_WARNING", "high"
        if water_level_m >= watch:
            return "FLOOD_WATCH", "medium"
        return None

    if st == "stormwater":
        sur = float(thr["surchargeLevelM"])
        ovf = float(thr["overflowLevelM"])
        if water_level_m >= ovf:
            return "STORMWATER_OVERFLOW", "critical"
        if water_level_m >= sur:
            return "STORMWATER_SURCHARGE", "high"
        return None

    return None


def _should_resolve_alert(site: Dict[str, Any], water_level_m: float, alert_type: str, hyst_margin: float) -> bool:
    thr = site["thresholds"]
    st = site["siteType"]

    if st == "river":
        if alert_type == "FLOOD_WATCH":
            return water_level_m < float(thr["watchLevelM"]) - hyst_margin
        if alert_type == "FLOOD_WARNING":
            return water_level_m < float(thr["warningLevelM"]) - hyst_margin
        if alert_type == "FLOOD_SEVERE":
            return water_level_m < float(thr["severeLevelM"]) - hyst_margin

    if st == "stormwater":
        if alert_type == "STORMWATER_SURCHARGE":
            return water_level_m < float(thr["surchargeLevelM"]) - hyst_margin
        if alert_type == "STORMWATER_OVERFLOW":
            return water_level_m < float(thr["overflowLevelM"]) - hyst_margin

    return False


def simulate(cfg: MongoConfig, sim: SimConfig) -> Dict[str, Any]:
    _require(sim.hours >= 1, "--hours must be >= 1")
    _require(sim.base_step_sec in (5, 10, 15, 30, 60), "--base-step-sec should be 5/10/15/30/60 for teaching")

    random.seed(sim.seed)

    client = MongoClient(cfg.uri)
    db = client[cfg.db_name]

    sites = list(db.sites.find({}))
    _require(len(sites) > 0, "No sites found. Run 01_seed_flood_project.py first.")

    sensors = list(db.sensors.find({}))
    sensor_by_site_metric: Dict[Tuple[Any, str], Dict[str, Any]] = {(s["siteId"], s["metric"]): s for s in sensors}

    policy_by_site: Dict[Any, Dict[str, Any]] = {p["siteId"]: p for p in db.samplingPolicies.find({"enabled": True})}
    state_by_site: Dict[Any, Dict[str, Any]] = {st["siteId"]: st for st in db.policyState.find({})}

    curve_by_site: Dict[Any, Dict[str, Any]] = {}
    for c in db.ratingCurves.find({}):
        sid = c["siteId"]
        if sid not in curve_by_site or int(c["version"]) > int(curve_by_site[sid]["version"]):
            curve_by_site[sid] = c

    db.measurements.delete_many({})
    db.alerts.delete_many({})

    start_ts = utc_now().replace(microsecond=0)
    end_ts = start_ts + timedelta(hours=sim.hours)
    step = timedelta(seconds=sim.base_step_sec)

    catchments = sorted({s["catchmentId"] for s in sites})
    storm_events: Dict[str, List[Tuple[datetime, datetime, float]]] = {}
    for c in catchments:
        events: List[Tuple[datetime, datetime, float]] = []
        for _ in range(random.randint(1, 3)):
            t0 = start_ts + timedelta(minutes=random.randint(10, max(10, sim.hours * 60 - 30)))
            dur_min = random.randint(10, 35)
            intensity = random.uniform(5.0, 25.0)
            events.append((t0, t0 + timedelta(minutes=dur_min), intensity))
        storm_events[c] = events

    hydro: Dict[Any, Dict[str, float]] = {}
    for site in sites:
        if site["siteType"] in ("river", "stormwater"):
            base_level = 0.8 if site["siteType"] == "river" else 0.15
            hydro[site["_id"]] = {
                "level": base_level + random.uniform(-0.05, 0.05),
                "velocity": 0.2 if site["siteType"] == "river" else 0.4,
                "battery": 100.0,
                "last_emit_level": base_level,
                "last_emit_ts_epoch": float(start_ts.timestamp()),
            }

    rain_accum_mm: Dict[str, float] = {c: 0.0 for c in catchments}
    open_alert_by_site: Dict[Any, Optional[str]] = {s["_id"]: None for s in sites}

    next_emit_ts: Dict[Any, datetime] = {}
    for site in sites:
        sid = site["_id"]
        pol = policy_by_site[sid]
        pst = state_by_site[sid]
        interval = int(pol["modes"][pst["currentMode"]]["intervalSec"])
        next_emit_ts[sid] = start_ts

    docs_batch: List[Dict[str, Any]] = []
    inserted = 0
    alerts_inserted = 0
    policy_updates = 0

    t = start_ts
    while t <= end_ts:
        rain_rate_by_catch: Dict[str, float] = {}
        for c in catchments:
            rate = 0.0
            for (a, b, inten) in storm_events[c]:
                if a <= t < b:
                    rate += max(0.0, inten + random.gauss(0.0, 1.5))
            if rate == 0.0 and random.random() < 0.01:
                rate = random.uniform(0.2, 1.0)
            rain_rate_by_catch[c] = rate
            rain_accum_mm[c] += rate * (sim.base_step_sec / 3600.0)

        for site in sites:
            sid = site["_id"]
            stype = site["siteType"]
            catch = site["catchmentId"]

            if stype == "river":
                rain = rain_rate_by_catch[catch]
                x = hydro[sid]["level"]
                target = 0.9 + 0.015 * rain
                x = 0.985 * x + 0.015 * target + random.gauss(0.0, 0.002)
                hydro[sid]["level"] = max(0.1, x)
                hydro[sid]["velocity"] = max(0.05, 0.15 + 0.25 * (hydro[sid]["level"] - 0.8))

            elif stype == "stormwater":
                rain = rain_rate_by_catch[catch]
                x = hydro[sid]["level"]
                target = 0.12 + 0.02 * rain
                x = 0.93 * x + 0.07 * target + random.gauss(0.0, 0.003)
                hydro[sid]["level"] = max(0.02, x)
                hydro[sid]["velocity"] = max(0.05, 0.30 + 0.60 * (hydro[sid]["level"] - 0.12))

            if stype in ("river", "stormwater"):
                pol = policy_by_site[sid]
                pst = state_by_site[sid]
                mode = pst["currentMode"]
                drain_per_hour = {"LOW": 0.10, "NORMAL": 0.18, "HIGH": 0.40, "CRITICAL": 0.90}[mode]
                hydro[sid]["battery"] = max(0.0, hydro[sid]["battery"] - drain_per_hour * (sim.base_step_sec / 3600.0))

        for site in sites:
            sid = site["_id"]
            stype = site["siteType"]
            catch = site["catchmentId"]

            if t < next_emit_ts[sid]:
                continue

            pol = policy_by_site[sid]
            pst = state_by_site[sid]
            mode = str(pst["currentMode"])
            interval_sec = int(pol["modes"][mode]["intervalSec"])

            if stype == "rain_gauge":
                rr = float(rain_rate_by_catch[catch])
                ra = float(rain_accum_mm[catch])
                for metric, val in [("rainfallRateMmh", rr), ("rainfallAccumMm", ra)]:
                    sensor = sensor_by_site_metric[(sid, metric)]
                    docs_batch.append(
                        {
                            "ts": t,
                            "meta": {"siteId": sid, "sensorId": sensor["_id"], "metric": metric},
                            "value": float(round(val, 3)),
                            "batteryPct": 100,
                            "signalQuality": float(round(random.uniform(0.85, 0.99), 3)),
                            "qcFlags": _qc_flags(metric, float(val)),
                        }
                    )
                next_emit_ts[sid] = t + timedelta(seconds=interval_sec)
                continue

            wl = float(hydro[sid]["level"])
            vel = float(hydro[sid]["velocity"])
            battery = float(hydro[sid]["battery"])

            last_emit_ts_epoch = float(hydro[sid]["last_emit_ts_epoch"])
            last_emit_level = float(hydro[sid]["last_emit_level"])
            dt_min = max(1e-6, (t.timestamp() - last_emit_ts_epoch) / 60.0)
            dlevel_dt = (wl - last_emit_level) / dt_min

            curve = curve_by_site.get(sid)
            flow = 0.0
            if curve is not None and curve["curveType"] == "powerLaw":
                p = curve["params"]
                flow = _power_law_flow(wl, float(p["a"]), float(p["h0"]), float(p["b"]))

            for metric, val in [("waterLevelM", wl), ("flowVelocityMps", vel), ("flowRateM3s", float(flow))]:
                sensor = sensor_by_site_metric[(sid, metric)]
                docs_batch.append(
                    {
                        "ts": t,
                        "meta": {"siteId": sid, "sensorId": sensor["_id"], "metric": metric},
                        "value": float(round(val, 4)) if metric != "flowRateM3s" else float(round(val, 3)),
                        "batteryPct": int(round(battery)),
                        "signalQuality": float(round(random.uniform(0.70, 0.98), 3)),
                        "qcFlags": _qc_flags(metric, float(val)),
                    }
                )

            hydro[sid]["last_emit_level"] = wl
            hydro[sid]["last_emit_ts_epoch"] = float(t.timestamp())

            new_mode, reason, new_cooldown_until = _decide_mode(
                site=site,
                policy=pol,
                state=pst,
                now_ts=t,
                water_level_m=wl,
                dlevel_dt_m_per_min=dlevel_dt,
                rainfall_rate_mmh=float(rain_rate_by_catch[catch]),
                battery_pct=battery,
            )

            if new_mode != mode:
                pst["currentMode"] = new_mode
                pst["lastChangeTs"] = t
                pst["lastDecisionReason"] = reason
                pst["cooldownUntilTs"] = new_cooldown_until
                pst["batteryPctLast"] = int(round(battery))
                pst["updatedAt"] = t
                policy_updates += 1

                db.policyState.update_one(
                    {"siteId": sid},
                    {"$set": {
                        "currentMode": pst["currentMode"],
                        "lastChangeTs": pst["lastChangeTs"],
                        "lastDecisionReason": pst["lastDecisionReason"],
                        "cooldownUntilTs": pst["cooldownUntilTs"],
                        "batteryPctLast": pst["batteryPctLast"],
                        "updatedAt": pst["updatedAt"],
                    }},
                    upsert=True,
                )
                interval_sec = int(pol["modes"][new_mode]["intervalSec"])

            hyst_margin = float(pol.get("hysteresisMarginM", 0.05))
            desired = _alert_type_for_site(site, wl)
            open_type = open_alert_by_site[sid]

            if desired is not None:
                desired_type, severity = desired
                if open_type is None or open_type != desired_type:
                    db.alerts.insert_one(
                        {
                            "ts": t,
                            "siteId": sid,
                            "alertType": desired_type,
                            "status": "OPEN",
                            "severity": severity,
                            "context": {
                                "waterLevelM": round(wl, 3),
                                "dLevelDtMperMin": round(dlevel_dt, 4),
                                "rainfallRateMmh": round(float(rain_rate_by_catch[catch]), 3),
                                "mode": pst["currentMode"],
                                "batteryPct": int(round(battery)),
                            },
                            "createdAt": t,
                        }
                    )
                    alerts_inserted += 1
                    open_alert_by_site[sid] = desired_type
            else:
                if open_type is not None and _should_resolve_alert(site, wl, open_type, hyst_margin):
                    db.alerts.insert_one(
                        {
                            "ts": t,
                            "siteId": sid,
                            "alertType": open_type,
                            "status": "RESOLVED",
                            "severity": "info",
                            "context": {
                                "waterLevelM": round(wl, 3),
                                "rainfallRateMmh": round(float(rain_rate_by_catch[catch]), 3),
                                "mode": pst["currentMode"],
                            },
                            "createdAt": t,
                        }
                    )
                    alerts_inserted += 1
                    open_alert_by_site[sid] = None

            next_emit_ts[sid] = t + timedelta(seconds=interval_sec)

            if len(docs_batch) >= sim.batch_size:
                db.measurements.insert_many(docs_batch, ordered=False)
                inserted += len(docs_batch)
                docs_batch = []

        t += step

    if docs_batch:
        db.measurements.insert_many(docs_batch, ordered=False)
        inserted += len(docs_batch)

    return {"measurementsInserted": inserted, "alertsInserted": alerts_inserted, "policyUpdates": policy_updates}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=6)
    parser.add_argument("--base-step-sec", type=int, default=10)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--batch-size", type=int, default=5000)
    args = parser.parse_args()

    out = simulate(
        MongoConfig(),
        SimConfig(hours=args.hours, base_step_sec=args.base_step_sec, seed=args.seed, batch_size=args.batch_size),
    )
    print("✅ Simulation complete")
    print(out)


if __name__ == "__main__":
    main()
