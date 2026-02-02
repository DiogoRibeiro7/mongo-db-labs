# MongoDB Teaching Labs Catalog

*Auto-generated on 2026-01-30 16:11*

## Overview

This repository contains **5 teaching labs** for MongoDB, covering various domains and difficulty levels.

## Quick Navigation

- [Cold Chain Monitoring System](#cold-chain-monitoring-mongodb)
- [Smart Grid Energy Monitoring System](#energy-monitoring-smart-grid)
- [IoT Flood Risk Monitoring](#iot_flood_demo)
- [Smart Parking Occupancy System](#smart-parking-occupancy)
- [Soil Humidity LoRaWAN Monitoring](#soil_humidity_lorawan)

---

## Lab Details

### Cold Chain Monitoring System {#cold-chain-monitoring-mongodb}

**Slug:** `cold-chain-monitoring-mongodb`
**Domain:** Logistics & Supply Chain
**Difficulty:** Intermediate
**Database:** `coldchain_db`
**Estimated Time:** 2-3 hours

#### Learning Outcomes

- Design time-series collections for temperature monitoring
- Implement cold chain compliance tracking
- Build adaptive sampling for temperature deviations
- Create geospatial queries for transport tracking
- Analyze temperature excursions with aggregations
- Generate compliance reports for auditing

#### Collections

6 collections: `assets`, `sensors`, `measurements`, `events`, `routes`, `alerts`

#### Key Topics

- Cold chain logistics
- Temperature monitoring
- Time-series data
- Adaptive sampling
- Asset tracking
- Compliance monitoring
- Real-time alerts

#### Sensors/Metrics

`temperature`, `humidity`, `door_status`, `gps_location`, `battery_level`, `shock_vibration`

#### Features

[✓] Time Series | [✓] Geospatial | [✓] Schema Validation | [✓] Aggregation Pipelines | [✓] Real Time Monitoring | [✓] Adaptive Sampling

#### Files

- **Setup:** `00_setup_mongodb.js`
- **Seed:** `01_seed_data.py`
- **Simulate:** `02_simulate_telemetry.py`
- **Queries:** `03_queries_exam.js`
- **Validation:** `04_bad_inserts.js`

#### Prerequisites

- MongoDB 6.0+ (7.0+ recommended for time-series)
- Basic understanding of supply chain logistics
- Familiarity with temperature monitoring concepts

#### Tags

`#logistics` `#cold-chain` `#temperature` `#iot` `#time-series` `#compliance` `#transport`

#### Quick Start

```bash
cd labs/cold-chain-monitoring-mongodb
mongosh 00_setup_mongodb.js
python 01_seed_*.py
python 02_simulate_*.py --hours 1
mongosh 03_queries_exam.js
```

---

### Smart Grid Energy Monitoring System {#energy-monitoring-smart-grid}

**Slug:** `energy-monitoring-smart-grid`
**Domain:** Energy & Utilities
**Difficulty:** Intermediate
**Database:** `energygrid_db`
**Estimated Time:** 2-3 hours

#### Learning Outcomes

- Design time-series collections for energy data
- Implement time-of-use tariff calculations
- Build peak demand detection algorithms
- Create consumption pattern analysis
- Develop cost estimation pipelines
- Analyze power quality metrics

#### Collections

6 collections: `buildings`, `meters`, `tariffs`, `readings`, `events`, `bills`

#### Key Topics

- Smart grid infrastructure
- Energy consumption patterns
- Time-of-use tariffs
- Peak demand management
- Power quality monitoring
- Cost optimization
- Outage detection

#### Features

[✓] Time Series | [✓] Real Time Monitoring | [✓] Schema Validation | [✓] Aggregation Pipelines | [✓] Peak Detection | [✓] Cost Calculation

#### Files

- **Setup:** `00_setup_mongodb.js`
- **Seed:** `01_seed_infrastructure.py`
- **Simulate:** `02_simulate_consumption.py`
- **Queries:** `03_queries_exam.js`
- **Validation:** `04_bad_inserts.js`

#### Prerequisites

- MongoDB 6.0+ (7.0+ recommended for time-series)
- Basic understanding of electrical systems
- Familiarity with utility billing concepts

#### Tags

`#smart-grid` `#energy` `#utilities` `#smart-meters` `#time-series` `#iot` `#tariffs` `#sustainability`

#### Quick Start

```bash
cd labs/energy-monitoring-smart-grid
mongosh 00_setup_mongodb.js
python 01_seed_*.py
python 02_simulate_*.py --hours 1
mongosh 03_queries_exam.js
```

---

### IoT Flood Risk Monitoring {#iot_flood_demo}

**Slug:** `iot_flood_demo`
**Domain:** Environmental Monitoring
**Difficulty:** Intermediate
**Database:** `iot_flood_demo`
**Estimated Time:** 2-3 hours

#### Learning Outcomes

- Design time-series collections for IoT data
- Implement adaptive sampling strategies
- Create geospatial queries for sensor networks
- Build alert systems with threshold detection
- Analyze hydrological patterns with aggregations

#### Collections

7 collections: `sites`, `sensors`, `measurements`, `ratingCurves`, `samplingPolicies`, `policyState`, `alerts`

#### Key Topics

- Time-series data
- GeoJSON
- Adaptive sampling
- Alert generation
- Sensor telemetry
- Hydrological modeling

#### Sensors/Metrics

`water_level`, `flow_rate`, `rainfall`, `battery_voltage`

#### Features

[✓] Time Series | [✓] Geospatial | [✓] Schema Validation | [✓] Aggregation Pipelines | [✓] Real Time Monitoring

#### Files

- **Setup:** `00_setup_mongodb.js`
- **Seed:** `01_seed_flood_project.py`
- **Simulate:** `02_simulate_flood_project.py`
- **Queries:** `03_queries_exam.js`
- **Validation:** `04_bad_inserts.js`

#### Prerequisites

- MongoDB 6.0+ (7.0+ recommended)
- Basic understanding of IoT concepts
- Familiarity with time-series data

#### Tags

`#iot` `#time-series` `#environmental` `#real-time` `#geospatial`

#### Quick Start

```bash
cd labs/iot_flood_demo
mongosh 00_setup_mongodb.js
python 01_seed_*.py
python 02_simulate_*.py --hours 1
mongosh 03_queries_exam.js
```

---

### Smart Parking Occupancy System {#smart-parking-occupancy}

**Slug:** `smart-parking-occupancy`
**Domain:** Smart City & IoT
**Difficulty:** Intermediate
**Database:** `smartparking_db`
**Estimated Time:** 2-3 hours

#### Learning Outcomes

- Design time-series collections for occupancy monitoring
- Implement parking violation detection logic
- Build zone-based occupancy analytics
- Create confidence-based sensor readings
- Analyze parking patterns and peak hours
- Generate revenue and utilization reports

#### Collections

6 collections: `zones`, `parking_spots`, `sensors`, `occupancy_readings`, `events`, `violations`

#### Key Topics

- Smart city infrastructure
- Parking management
- LoRa/magnetometer sensors
- Occupancy detection
- Violation tracking
- Time-series analysis
- Zone-based aggregation

#### Sensors/Metrics

`magnetometer`, `ultrasonic`, `infrared`, `camera`, `lora_gateway`

#### Features

[✓] Time Series | [✓] Geospatial | [✓] Schema Validation | [✓] Aggregation Pipelines | [✓] Real Time Monitoring | [✓] Violation Detection

#### Files

- **Setup:** `00_setup_mongodb.js`
- **Seed:** `01_seed_infrastructure.py`
- **Simulate:** `02_simulate_occupancy.py`
- **Queries:** `03_queries_exam.js`
- **Validation:** `04_bad_inserts.js`

#### Prerequisites

- MongoDB 6.0+ (7.0+ recommended for time-series)
- Basic understanding of IoT sensor networks
- Familiarity with smart city concepts

#### Tags

`#smart-city` `#parking` `#iot` `#lora` `#magnetometer` `#time-series` `#occupancy` `#violations`

#### Quick Start

```bash
cd labs/smart-parking-occupancy
mongosh 00_setup_mongodb.js
python 01_seed_*.py
python 02_simulate_*.py --hours 1
mongosh 03_queries_exam.js
```

---

### Soil Humidity LoRaWAN Monitoring {#soil_humidity_lorawan}

**Slug:** `soil_humidity_lorawan`
**Domain:** Agriculture IoT
**Difficulty:** Intermediate
**Database:** `lorawan_db`
**Estimated Time:** 2-3 hours

#### Learning Outcomes

- Model agricultural domain with MongoDB
- Handle LoRaWAN-specific IoT patterns
- Implement precision irrigation strategies
- Analyze soil conditions with time-series data
- Create farm management dashboards

#### Collections

7 collections: `farms`, `fields`, `sensors`, `measurements`, `irrigationSchedules`, `alerts`, `cropTypes`

#### Key Topics

- Agricultural IoT
- LoRaWAN protocol
- Soil moisture monitoring
- Precision farming
- Irrigation management
- Time-series analytics

#### Sensors/Metrics

`soil_moisture`, `soil_temperature`, `soil_pH`, `air_temperature`, `humidity`

#### Features

[✓] Time Series | [✓] Geospatial | [✓] Schema Validation | [✓] Lorawan Specific | [✓] Irrigation Automation

#### Files

- **Setup:** `00_setup_mongodb.js`
- **Seed:** `01_seed_flood_project.py`
- **Simulate:** `02_simulate_flood_project.py`
- **Queries:** `03_queries_exam.js`
- **Validation:** `04_bad_inserts.js`

#### Prerequisites

- MongoDB 6.0+ (7.0+ recommended)
- Basic understanding of agriculture
- Familiarity with IoT sensors

#### Tags

`#agriculture` `#iot` `#lorawan` `#time-series` `#precision-farming`

#### Quick Start

```bash
cd labs/soil_humidity_lorawan
mongosh 00_setup_mongodb.js
python 01_seed_*.py
python 02_simulate_*.py --hours 1
mongosh 03_queries_exam.js
```

---

## Statistics

### By Difficulty

- **Intermediate:** 5 lab(s)

### By Domain

- **Agriculture IoT:** 1 lab(s)
- **Energy & Utilities:** 1 lab(s)
- **Environmental Monitoring:** 1 lab(s)
- **Logistics & Supply Chain:** 1 lab(s)
- **Smart City & IoT:** 1 lab(s)

### Feature Coverage

- **Time Series:** 5/5 labs (100%)
- **Schema Validation:** 5/5 labs (100%)
- **Geospatial:** 4/5 labs (80%)
- **Aggregation Pipelines:** 4/5 labs (80%)
- **Real Time Monitoring:** 4/5 labs (80%)
- **Adaptive Sampling:** 1/5 labs (20%)
- **Peak Detection:** 1/5 labs (20%)
- **Cost Calculation:** 1/5 labs (20%)
- **Violation Detection:** 1/5 labs (20%)
- **Lorawan Specific:** 1/5 labs (20%)
- **Irrigation Automation:** 1/5 labs (20%)

### Total Metrics

- **Total Labs:** 5
- **Total Collections:** 32
- **Average Collections per Lab:** 6.4