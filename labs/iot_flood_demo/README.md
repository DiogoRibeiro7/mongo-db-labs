# IoT Flood Demo (MongoDB)

Teaching bundle for a flood-risk IoT project:
- Rivers + stormwater network + rain gauges
- Time series measurements
- Adaptive sampling (LOW/NORMAL/HIGH/CRITICAL)
- Alerts (OPEN/RESOLVED)

## Files

- `00_setup_mongodb.js` — creates collections, time-series config, and indexes
- `01_seed_flood_project.py` — seeds `sites`, `sensors`, `ratingCurves`, `samplingPolicies`, `policyState`
- `02_simulate_flood_project.py` — generates synthetic telemetry into `measurements`, updates `policyState`, emits `alerts`
- `03_queries_exam.js` — exam-style aggregation queries
- `DATABASE.md` — data dictionary (every key documented)
- `docker-compose.yml` — optional MongoDB container for labs
- `requirements.txt` — Python dependency for the seed/simulator scripts

## Quick start (local MongoDB)

1) Setup DB + indexes:
```bash
mongosh 00_setup_mongodb.js
```

2) Install Python dependency:
```bash
python -m pip install -r requirements.txt
```

3) Seed master/config data:
```bash
python 01_seed_flood_project.py
```

4) Generate time series:
```bash
python 02_simulate_flood_project.py --hours 6 --base-step-sec 10 --seed 7
```

5) Run the query sheet:
```bash
mongosh 03_queries_exam.js
```

## Quick start (Docker)

```bash
docker compose up -d
mongosh "mongodb://localhost:27017" 00_setup_mongodb.js
python -m pip install -r requirements.txt
python 01_seed_flood_project.py
python 02_simulate_flood_project.py --hours 6 --base-step-sec 10 --seed 7
mongosh "mongodb://localhost:27017" 03_queries_exam.js
```


## Schema validation (teaching)

This bundle applies MongoDB collection validation using `$jsonSchema` in `00_setup_mongodb.js`.

- Default: `validationLevel="strict"` and `validationAction="error"`
- To disable validation for a lab (example for `measurements`):

```bash
mongosh --eval 'db.getSiblingDB("iot_flood_demo").runCommand({collMod:"measurements",validationLevel:"off"})'
```
