# mongo-db-labs

A teaching repository that bundles multiple **MongoDB lab databases** as self-contained folders.
Each lab includes: a data model, seed + simulation scripts (when applicable), and an exam-style query sheet.

## Goals

* Provide realistic NoSQL datasets for students to practice schema design, indexing, aggregation, and time-series analytics.
* Keep each lab reproducible and isolated (so one lab never breaks another).
* Encourage good engineering habits: versioned datasets, clear documentation, and consistent naming.

## Repository structure

Each lab lives in its own folder under `labs/`.

```
mongo-db-labs/
  labs/
    flood-risk-mongodb/
      00_setup_mongodb.js
      01_seed_flood_project.py
      02_simulate_flood_project.py
      03_queries_exam.js
      DATABASE.md
      README.md
      docker-compose.yml
      requirements.txt
    <next-lab>/
      ...
```

### What each lab folder must contain

* `DATABASE.md`
  Data dictionary. Every key documented.
* `README.md`
  How to run the lab and what students should do.
* `00_setup_mongodb.js`
  Creates collections, indexes, and (optionally) schema validation.
* `01_seed_*.py`
  Inserts master/config data (sites, sensors, policies, etc.).
* `02_simulate_*.py` (optional)
  Generates time-series/telemetry and events.
* `03_queries_exam.js`
  Query sheet with exercises and reference queries.
* `docker-compose.yml` (optional but recommended)
  Standard MongoDB environment for students.
* `requirements.txt` (optional)
  Python dependencies for the lab scripts.

## Conventions

* **Database names** are unique per lab (example: `iot_flood_demo`).
* **All keys are in English**, using `camelCase`.
* Timestamps:

  * `ts` is always UTC `Date`.
  * `createdAt`, `updatedAt` are UTC `Date`.
* Metrics should be explicit and stable:

  * Prefer `waterLevelM`, `flowRateM3s`, `rainfallRateMmh`, etc.

## Requirements

* MongoDB 6+ (MongoDB 5+ if the lab uses `$dateTrunc` / `$setWindowFields`)
* `mongosh`
* Python 3.10+ (only required for labs that ship Python scripts)
* Optional: Docker + Docker Compose

## Running a lab (general)

Go into the lab folder and follow its `README.md`.
Typical sequence:

```bash
cd labs/<lab-name>

# 1) Create collections + indexes (+ schema validation if included)
mongosh 00_setup_mongodb.js

# 2) Install Python deps (if requirements.txt exists)
python -m pip install -r requirements.txt

# 3) Seed the database
python 01_seed_*.py

# 4) Simulate / generate time series (if the lab includes it)
python 02_simulate_*.py

# 5) Run the query sheet
mongosh 03_queries_exam.js
```

## Running a lab with Docker (general)

If the lab includes `docker-compose.yml`:

```bash
cd labs/<lab-name>
docker compose up -d

mongosh "mongodb://localhost:27017" 00_setup_mongodb.js
python -m pip install -r requirements.txt
python 01_seed_*.py
python 02_simulate_*.py
mongosh "mongodb://localhost:27017" 03_queries_exam.js
```

## Labs

### Flood Risk Monitoring (rivers + stormwater + rain gauges)

Folder: `labs/flood-risk-mongodb/`

Topics covered:

* Time-series collection design
* Adaptive sampling policies
* Alert/event logging
* Indexing strategies
* Aggregations + window functions

## How to add a new lab

1. Create a folder: `labs/<your-lab-name>/`
2. Copy the template structure listed above.
3. Ensure `DATABASE.md` documents every key.
4. Keep it runnable from scratch (clean setup + deterministic seed options).

