// =====================================================
// Smart Grid Energy Monitoring - Query Exercises
// Database: energygrid_db
// =====================================================

// Note: Database is already selected by the lab runner

print("\n" + "=".repeat(60));
print("SMART GRID ENERGY MONITORING - QUERY EXERCISES");
print("=".repeat(60));

// =====================================================
// QUERY 1: Current Grid Status Overview
// =====================================================
print("\n1. CURRENT GRID STATUS AND DEMAND");
print("-" + "-".repeat(40));

// Get current demand by building type
db.readings.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 60*60*1000) }  // Last hour
        }
    },
    {
        $sort: { timestamp: -1 }
    },
    {
        $group: {
            _id: "$meta.buildingId",
            lastReading: { $first: "$$ROOT" }
        }
    },
    {
        $lookup: {
            from: "buildings",
            localField: "_id",
            foreignField: "buildingId",
            as: "building"
        }
    },
    { $unwind: "$building" },
    {
        $group: {
            _id: "$building.type",
            totalDemandKW: { $sum: "$lastReading.kWDemand" },
            avgPowerFactor: { $avg: "$lastReading.powerFactor" },
            buildingCount: { $sum: 1 },
            avgVoltage: { $avg: "$lastReading.voltage" }
        }
    },
    {
        $project: {
            buildingType: "$_id",
            totalDemandKW: { $round: ["$totalDemandKW", 2] },
            totalDemandMW: { $round: [{ $divide: ["$totalDemandKW", 1000] }, 3] },
            avgPowerFactor: { $round: ["$avgPowerFactor", 3] },
            buildingCount: 1,
            avgVoltage: { $round: ["$avgVoltage", 1] }
        }
    },
    { $sort: { totalDemandKW: -1 } }
]).forEach(type => {
    print(`${type.buildingType}:`);
    print(`  Demand: ${type.totalDemandKW} kW (${type.totalDemandMW} MW)`);
    print(`  Buildings: ${type.buildingCount}`);
    print(`  Avg Power Factor: ${type.avgPowerFactor}`);
    print(`  Avg Voltage: ${type.avgVoltage}V`);
});

// =====================================================
// QUERY 2: Daily Energy Consumption Totals
// =====================================================
print("\n2. DAILY ENERGY CONSUMPTION ANALYSIS");
print("-" + "-".repeat(40));

// Calculate daily totals and costs
db.readings.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }  // Last 24 hours
        }
    },
    {
        $group: {
            _id: {
                buildingId: "$meta.buildingId",
                hour: { $hour: "$timestamp" }
            },
            hourlyKWh: { $sum: "$kWhConsumed" },
            peakDemand: { $max: "$kWDemand" },
            avgPowerFactor: { $avg: "$powerFactor" }
        }
    },
    {
        $group: {
            _id: "$_id.buildingId",
            totalKWh: { $sum: "$hourlyKWh" },
            peakDemandKW: { $max: "$peakDemand" },
            avgPowerFactor: { $avg: "$avgPowerFactor" },
            peakHour: {
                $max: {
                    demand: "$peakDemand",
                    hour: "$_id.hour"
                }
            }
        }
    },
    {
        $lookup: {
            from: "buildings",
            localField: "_id",
            foreignField: "buildingId",
            as: "building"
        }
    },
    { $unwind: "$building" },
    {
        $lookup: {
            from: "tariffs",
            localField: "building.contractInfo.tariffPlanId",
            foreignField: "tariffId",
            as: "tariff"
        }
    },
    { $unwind: "$tariff" },
    {
        $project: {
            buildingName: "$building.name",
            buildingType: "$building.type",
            totalKWh: { $round: ["$totalKWh", 2] },
            peakDemandKW: { $round: ["$peakDemandKW", 2] },
            avgPowerFactor: { $round: ["$avgPowerFactor", 3] },
            estimatedCost: {
                $round: [
                    {
                        $multiply: [
                            "$totalKWh",
                            { $ifNull: ["$tariff.rates.flatRate.pricePerKWh", 0.12] }
                        ]
                    },
                    2
                ]
            },
            tariffType: "$tariff.type",
            peakHour: "$peakHour.hour"
        }
    },
    { $sort: { totalKWh: -1 } },
    { $limit: 10 }
]).forEach(building => {
    print(`${building.buildingName} (${building.buildingType}):`);
    print(`  Consumption: ${building.totalKWh} kWh`);
    print(`  Peak Demand: ${building.peakDemandKW} kW at hour ${building.peakHour}`);
    print(`  Power Factor: ${building.avgPowerFactor}`);
    print(`  Est. Cost: $${building.estimatedCost} (${building.tariffType} tariff)`);
});

// =====================================================
// QUERY 3: Peak Demand Intervals
// =====================================================
print("\n3. PEAK DEMAND INTERVALS (TOP 5 PEAKS)");
print("-" + "-".repeat(40));

// Find peak demand periods across all buildings
db.readings.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 7*24*60*60*1000) }  // Last 7 days
        }
    },
    {
        $group: {
            _id: {
                interval: {
                    $dateToString: {
                        format: "%Y-%m-%d %H:%M",
                        date: "$timestamp"
                    }
                }
            },
            totalDemandKW: { $sum: "$kWDemand" },
            avgVoltage: { $avg: "$voltage" },
            avgFrequency: { $avg: "$frequency" },
            readingCount: { $sum: 1 }
        }
    },
    { $sort: { totalDemandKW: -1 } },
    { $limit: 5 },
    {
        $project: {
            interval: "$_id.interval",
            totalDemandKW: { $round: ["$totalDemandKW", 2] },
            totalDemandMW: { $round: [{ $divide: ["$totalDemandKW", 1000] }, 3] },
            avgVoltage: { $round: ["$avgVoltage", 1] },
            avgFrequency: { $round: ["$avgFrequency", 2] },
            readingCount: 1
        }
    }
]).forEach(peak => {
    print(`${peak.interval}:`);
    print(`  Peak Demand: ${peak.totalDemandKW} kW (${peak.totalDemandMW} MW)`);
    print(`  Grid Conditions: ${peak.avgVoltage}V, ${peak.avgFrequency}Hz`);
    print(`  Active Meters: ${peak.readingCount}`);
});

// =====================================================
// QUERY 4: Time-of-Use Cost Analysis
// =====================================================
print("\n4. TIME-OF-USE COST BREAKDOWN");
print("-" + "-".repeat(40));

// Analyze consumption by time-of-use periods
db.readings.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
        }
    },
    {
        $lookup: {
            from: "buildings",
            localField: "meta.buildingId",
            foreignField: "buildingId",
            as: "building"
        }
    },
    { $unwind: "$building" },
    {
        $match: {
            "building.contractInfo.tariffPlanId": { $in: ["TAR0002", "TAR1001", "TAR2001"] }  // TOU tariffs
        }
    },
    {
        $addFields: {
            hour: { $hour: "$timestamp" },
            period: {
                $switch: {
                    branches: [
                        { case: { $and: [{ $gte: [{ $hour: "$timestamp" }, 16] },
                                       { $lte: [{ $hour: "$timestamp" }, 21] }] },
                          then: "peak" },
                        { case: { $or: [{ $lt: [{ $hour: "$timestamp" }, 7] },
                                      { $gt: [{ $hour: "$timestamp" }, 23] }] },
                          then: "offPeak" }
                    ],
                    default: "shoulder"
                }
            }
        }
    },
    {
        $group: {
            _id: {
                buildingType: "$building.type",
                period: "$period"
            },
            totalKWh: { $sum: "$kWhConsumed" },
            avgDemand: { $avg: "$kWDemand" },
            count: { $sum: 1 }
        }
    },
    {
        $group: {
            _id: "$_id.buildingType",
            periods: {
                $push: {
                    period: "$_id.period",
                    totalKWh: "$totalKWh",
                    avgDemand: "$avgDemand"
                }
            },
            totalKWh: { $sum: "$totalKWh" }
        }
    },
    {
        $project: {
            buildingType: "$_id",
            totalKWh: { $round: ["$totalKWh", 2] },
            breakdown: "$periods"
        }
    }
]).forEach(analysis => {
    print(`\n${analysis.buildingType} buildings (${analysis.totalKWh} kWh total):`);
    analysis.breakdown.forEach(period => {
        const percentage = (period.totalKWh / analysis.totalKWh * 100).toFixed(1);
        print(`  ${period.period}: ${period.totalKWh.toFixed(2)} kWh (${percentage}%), ` +
              `Avg ${period.avgDemand.toFixed(2)} kW`);
    });
});

// =====================================================
// QUERY 5: Power Quality Analysis
// =====================================================
print("\n5. POWER QUALITY METRICS");
print("-" + "-".repeat(40));

// Analyze power quality issues
db.events.aggregate([
    {
        $match: {
            eventType: { $in: ["voltage_sag", "voltage_spike", "frequency_deviation", "phase_imbalance"] },
            timestamp: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
        }
    },
    {
        $group: {
            _id: "$eventType",
            count: { $sum: 1 },
            avgDuration: { $avg: "$details.duration" },
            affectedBuildings: { $addToSet: "$buildingId" },
            severityBreakdown: {
                $push: "$severity"
            }
        }
    },
    {
        $project: {
            eventType: "$_id",
            count: 1,
            avgDurationSec: { $round: ["$avgDuration", 0] },
            affectedBuildingCount: { $size: "$affectedBuildings" },
            criticalCount: {
                $size: {
                    $filter: {
                        input: "$severityBreakdown",
                        cond: { $eq: ["$$this", "critical"] }
                    }
                }
            }
        }
    },
    { $sort: { count: -1 } }
]).forEach(quality => {
    print(`${quality.eventType}:`);
    print(`  Occurrences: ${quality.count}`);
    print(`  Avg Duration: ${quality.avgDurationSec}s`);
    print(`  Affected Buildings: ${quality.affectedBuildingCount}`);
    print(`  Critical Events: ${quality.criticalCount}`);
});

// =====================================================
// QUERY 6: Building Energy Efficiency
// =====================================================
print("\n6. ENERGY EFFICIENCY BY BUILDING CLASS");
print("-" + "-".repeat(40));

// Calculate efficiency metrics by energy class
db.buildings.aggregate([
    {
        $lookup: {
            from: "readings",
            let: { buildingId: "$buildingId" },
            pipeline: [
                {
                    $match: {
                        $expr: { $eq: ["$meta.buildingId", "$$buildingId"] },
                        timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
                    }
                },
                {
                    $group: {
                        _id: null,
                        totalKWh: { $sum: "$kWhConsumed" },
                        avgPowerFactor: { $avg: "$powerFactor" }
                    }
                }
            ],
            as: "consumption"
        }
    },
    { $unwind: { path: "$consumption", preserveNullAndEmptyArrays: true } },
    {
        $group: {
            _id: {
                energyClass: "$characteristics.energyClass",
                type: "$type"
            },
            buildingCount: { $sum: 1 },
            avgConsumptionPerSqM: {
                $avg: {
                    $divide: [
                        { $ifNull: ["$consumption.totalKWh", 0] },
                        "$characteristics.squareMeters"
                    ]
                }
            },
            avgPowerFactor: { $avg: "$consumption.avgPowerFactor" },
            solarCount: {
                $sum: { $cond: ["$characteristics.hasSolar", 1, 0] }
            }
        }
    },
    {
        $project: {
            energyClass: "$_id.energyClass",
            buildingType: "$_id.type",
            buildingCount: 1,
            kWhPerSqM: { $round: ["$avgConsumptionPerSqM", 4] },
            avgPowerFactor: { $round: ["$avgPowerFactor", 3] },
            solarPercentage: {
                $round: [
                    { $multiply: [{ $divide: ["$solarCount", "$buildingCount"] }, 100] },
                    1
                ]
            }
        }
    },
    { $sort: { energyClass: 1, kWhPerSqM: 1 } }
]).forEach(efficiency => {
    print(`Class ${efficiency.energyClass || 'N/A'} - ${efficiency.buildingType}:`);
    print(`  Buildings: ${efficiency.buildingCount}`);
    print(`  Consumption: ${efficiency.kWhPerSqM} kWh/m²/day`);
    print(`  Power Factor: ${efficiency.avgPowerFactor}`);
    print(`  Solar Adoption: ${efficiency.solarPercentage}%`);
});

// =====================================================
// QUERY 7: Outage and Event Impact
// =====================================================
print("\n7. GRID EVENTS AND OUTAGE ANALYSIS");
print("-" + "-".repeat(40));

// Analyze power outages and their impact
db.events.aggregate([
    {
        $match: {
            eventType: { $in: ["power_outage", "peak_demand"] },
            timestamp: { $gte: new Date(Date.now() - 30*24*60*60*1000) }
        }
    },
    {
        $group: {
            _id: "$eventType",
            totalEvents: { $sum: 1 },
            avgDuration: {
                $avg: {
                    $divide: [
                        { $subtract: [
                            { $ifNull: ["$endTime", "$timestamp"] },
                            "$timestamp"
                        ]},
                        60000  // Convert to minutes
                    ]
                }
            },
            totalCost: { $sum: "$details.estimatedCost" },
            affectedUnits: { $sum: "$details.affectedUnits" },
            severityBreakdown: {
                $push: "$severity"
            }
        }
    },
    {
        $project: {
            eventType: "$_id",
            totalEvents: 1,
            avgDurationMin: { $round: ["$avgDuration", 1] },
            totalCost: { $round: ["$totalCost", 2] },
            affectedUnits: 1,
            emergencyCount: {
                $size: {
                    $filter: {
                        input: "$severityBreakdown",
                        cond: { $eq: ["$$this", "emergency"] }
                    }
                }
            }
        }
    }
]).forEach(event => {
    print(`${event.eventType}:`);
    print(`  Total Events: ${event.totalEvents}`);
    print(`  Avg Duration: ${event.avgDurationMin} minutes`);
    print(`  Est. Impact Cost: $${event.totalCost}`);
    print(`  Affected Units: ${event.affectedUnits}`);
    print(`  Emergency Events: ${event.emergencyCount}`);
});

// =====================================================
// QUERY 8: Monthly Billing Summary
// =====================================================
print("\n8. MONTHLY BILLING AND REVENUE ANALYSIS");
print("-" + "-".repeat(40));

// Analyze billing data
db.bills.aggregate([
    {
        $match: {
            "billingPeriod.start": { $gte: new Date(Date.now() - 60*24*60*60*1000) }
        }
    },
    {
        $lookup: {
            from: "buildings",
            localField: "buildingId",
            foreignField: "buildingId",
            as: "building"
        }
    },
    { $unwind: "$building" },
    {
        $group: {
            _id: "$building.type",
            billCount: { $sum: 1 },
            totalRevenue: { $sum: "$totalAmount" },
            totalConsumption: { $sum: "$consumption.totalKWh" },
            avgBill: { $avg: "$totalAmount" },
            paidBills: {
                $sum: { $cond: [{ $eq: ["$status", "paid"] }, 1, 0] }
            },
            overdueBills: {
                $sum: { $cond: [{ $eq: ["$status", "overdue"] }, 1, 0] }
            },
            avgPowerFactor: { $avg: "$consumption.powerFactor" }
        }
    },
    {
        $project: {
            buildingType: "$_id",
            billCount: 1,
            totalRevenue: { $round: ["$totalRevenue", 2] },
            totalConsumptionMWh: { $round: [{ $divide: ["$totalConsumption", 1000] }, 2] },
            avgBill: { $round: ["$avgBill", 2] },
            avgRatePerKWh: {
                $round: [
                    { $divide: ["$totalRevenue", "$totalConsumption"] },
                    4
                ]
            },
            collectionRate: {
                $round: [
                    { $multiply: [
                        { $divide: ["$paidBills", "$billCount"] },
                        100
                    ]},
                    1
                ]
            },
            overdueCount: "$overdueBills",
            avgPowerFactor: { $round: ["$avgPowerFactor", 3] }
        }
    },
    { $sort: { totalRevenue: -1 } }
]).forEach(billing => {
    print(`\n${billing.buildingType}:`);
    print(`  Bills Issued: ${billing.billCount}`);
    print(`  Total Revenue: $${billing.totalRevenue}`);
    print(`  Total Consumption: ${billing.totalConsumptionMWh} MWh`);
    print(`  Avg Bill: $${billing.avgBill}`);
    print(`  Avg Rate: $${billing.avgRatePerKWh}/kWh`);
    print(`  Collection Rate: ${billing.collectionRate}%`);
    print(`  Overdue: ${billing.overdueCount}`);
});

// =====================================================
// Summary Statistics
// =====================================================
print("\n" + "=".repeat(60));
print("QUERY EXERCISES COMPLETE");

// Get collection counts
const stats = {
    buildings: db.buildings.countDocuments(),
    meters: db.meters.countDocuments(),
    tariffs: db.tariffs.countDocuments(),
    readings: db.readings.countDocuments(),
    events: db.events.countDocuments(),
    bills: db.bills.countDocuments()
};

print(`Total buildings: ${stats.buildings}`);
print(`Total meters: ${stats.meters}`);
print(`Total tariff plans: ${stats.tariffs}`);
print(`Total readings: ${stats.readings}`);
print(`Total events: ${stats.events}`);
print(`Total bills: ${stats.bills}`);

// Calculate system-wide metrics
const systemMetrics = db.readings.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 60*60*1000) }  // Last hour
        }
    },
    {
        $group: {
            _id: null,
            totalDemandKW: { $sum: "$kWDemand" },
            avgVoltage: { $avg: "$voltage" },
            avgFrequency: { $avg: "$frequency" },
            avgPowerFactor: { $avg: "$powerFactor" }
        }
    }
]).next();

if (systemMetrics) {
    print(`\nCurrent Grid Status:`);
    print(`  Total Demand: ${systemMetrics.totalDemandKW.toFixed(2)} kW (${(systemMetrics.totalDemandKW/1000).toFixed(3)} MW)`);
    print(`  Avg Voltage: ${systemMetrics.avgVoltage.toFixed(1)}V`);
    print(`  Avg Frequency: ${systemMetrics.avgFrequency.toFixed(2)}Hz`);
    print(`  Avg Power Factor: ${systemMetrics.avgPowerFactor.toFixed(3)}`);
}

print("=" + "=".repeat(60) + "\n");