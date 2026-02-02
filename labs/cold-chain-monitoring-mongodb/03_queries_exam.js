// =====================================================
// Cold Chain Monitoring - Query Exercises
// Database: coldchain_db
// =====================================================

// Note: Database is already selected by the lab runner

print("\n" + "=".repeat(60));
print("COLD CHAIN MONITORING - QUERY EXERCISES");
print("=".repeat(60));

// =====================================================
// QUERY 1: Current Asset Status Overview
// =====================================================
print("\n1. CURRENT ASSET STATUS OVERVIEW");
print("-".repeat(40));

db.assets.aggregate([
    {
        $lookup: {
            from: "sensors",
            localField: "assetId",
            foreignField: "assetId",
            as: "sensors"
        }
    },
    {
        $lookup: {
            from: "measurements",
            let: { aid: "$assetId" },
            pipeline: [
                {
                    $match: {
                        $expr: { $eq: ["$meta.assetId", "$$aid"] }
                    }
                },
                { $sort: { timestamp: -1 } },
                { $limit: 1 }
            ],
            as: "lastMeasurement"
        }
    },
    {
        $project: {
            assetId: 1,
            name: 1,
            assetType: 1,
            status: 1,
            "temperatureRange": 1,
            sensorCount: { $size: "$sensors" },
            activeSensors: {
                $size: {
                    $filter: {
                        input: "$sensors",
                        cond: { $eq: ["$$this.status", "active"] }
                    }
                }
            },
            lastTemperature: { $arrayElemAt: ["$lastMeasurement.temperature", 0] },
            lastReading: { $arrayElemAt: ["$lastMeasurement.timestamp", 0] },
            isInRange: {
                $and: [
                    { $gte: [
                        { $arrayElemAt: ["$lastMeasurement.temperature", 0] },
                        "$temperatureRange.min"
                    ]},
                    { $lte: [
                        { $arrayElemAt: ["$lastMeasurement.temperature", 0] },
                        "$temperatureRange.max"
                    ]}
                ]
            }
        }
    },
    { $sort: { assetType: 1, assetId: 1 } }
]).forEach(printjson);

// =====================================================
// QUERY 2: Temperature Statistics by Asset (Last 24 Hours)
// =====================================================
print("\n2. TEMPERATURE STATISTICS (LAST 24 HOURS)");
print("-".repeat(40));

db.measurements.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) },
            temperature: { $exists: true }
        }
    },
    {
        $group: {
            _id: "$meta.assetId",
            avgTemp: { $avg: "$temperature" },
            minTemp: { $min: "$temperature" },
            maxTemp: { $max: "$temperature" },
            stdDev: { $stdDevPop: "$temperature" },
            sampleCount: { $sum: 1 },
            excursions: {
                $sum: {
                    $cond: [
                        { $or: [
                            { $gt: ["$temperature", 8] },  // Above typical max
                            { $lt: ["$temperature", -20] }  // Below typical min
                        ]},
                        1, 0
                    ]
                }
            }
        }
    },
    {
        $lookup: {
            from: "assets",
            localField: "_id",
            foreignField: "assetId",
            as: "asset"
        }
    },
    {
        $unwind: "$asset"
    },
    {
        $project: {
            assetName: "$asset.name",
            assetType: "$asset.assetType",
            stats: {
                avg: { $round: ["$avgTemp", 2] },
                min: { $round: ["$minTemp", 2] },
                max: { $round: ["$maxTemp", 2] },
                stdDev: { $round: ["$stdDev", 2] },
                samples: "$sampleCount",
                excursions: "$excursions"
            },
            targetRange: "$asset.temperatureRange",
            compliance: {
                $cond: [
                    { $and: [
                        { $gte: ["$minTemp", "$asset.temperatureRange.min"] },
                        { $lte: ["$maxTemp", "$asset.temperatureRange.max"] }
                    ]},
                    "COMPLIANT",
                    "NON-COMPLIANT"
                ]
            }
        }
    },
    { $sort: { compliance: -1, assetType: 1 } }
]).forEach(printjson);

// =====================================================
// QUERY 3: Active Alerts Summary
// =====================================================
print("\n3. ACTIVE ALERTS SUMMARY");
print("-".repeat(40));

db.alerts.aggregate([
    {
        $match: { status: "active" }
    },
    {
        $group: {
            _id: {
                alertType: "$alertType",
                severity: "$severity"
            },
            count: { $sum: 1 },
            assets: { $addToSet: "$assetId" },
            oldestAlert: { $min: "$triggeredAt" },
            examples: { $push: {
                alertId: "$alertId",
                assetId: "$assetId",
                message: "$message",
                triggeredAt: "$triggeredAt"
            }}
        }
    },
    {
        $project: {
            alertType: "$_id.alertType",
            severity: "$_id.severity",
            count: 1,
            affectedAssets: { $size: "$assets" },
            oldestAlert: 1,
            exampleAlert: { $arrayElemAt: ["$examples", 0] }
        }
    },
    {
        $sort: {
            severity: -1,
            count: -1
        }
    }
]).forEach(printjson);

// =====================================================
// QUERY 4: Door Open Events Analysis
// =====================================================
print("\n4. DOOR OPEN EVENTS ANALYSIS");
print("-".repeat(40));

db.events.aggregate([
    {
        $match: {
            eventType: "door_open",
            timestamp: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
        }
    },
    {
        $project: {
            assetId: 1,
            timestamp: 1,
            hour: { $hour: "$timestamp" },
            dayOfWeek: { $dayOfWeek: "$timestamp" },
            duration: "$details.duration_seconds",
            tempAtOpen: "$details.temperature_at_open"
        }
    },
    {
        $group: {
            _id: "$assetId",
            totalOpens: { $sum: 1 },
            avgDuration: { $avg: "$duration" },
            maxDuration: { $max: "$duration" },
            avgTempAtOpen: { $avg: "$tempAtOpen" },
            hourlyPattern: {
                $push: "$hour"
            },
            peakHour: { $max: "$hour" }
        }
    },
    {
        $lookup: {
            from: "assets",
            localField: "_id",
            foreignField: "assetId",
            as: "asset"
        }
    },
    {
        $unwind: "$asset"
    },
    {
        $project: {
            assetName: "$asset.name",
            assetType: "$asset.assetType",
            doorStats: {
                totalOpens: "$totalOpens",
                avgDurationSec: { $round: ["$avgDuration", 1] },
                maxDurationSec: { $round: ["$maxDuration", 1] },
                avgTempAtOpen: { $round: ["$avgTempAtOpen", 2] }
            },
            opensPerDay: {
                $round: [{ $divide: ["$totalOpens", 7] }, 1]
            }
        }
    },
    { $sort: { "doorStats.totalOpens": -1 } }
]).forEach(printjson);

// =====================================================
// QUERY 5: Adaptive Sampling Effectiveness
// =====================================================
print("\n5. ADAPTIVE SAMPLING ANALYSIS");
print("-".repeat(40));

db.measurements.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
        }
    },
    {
        $group: {
            _id: {
                assetId: "$meta.assetId",
                mode: "$samplingMode"
            },
            count: { $sum: 1 },
            avgTemp: { $avg: "$temperature" },
            minTemp: { $min: "$temperature" },
            maxTemp: { $max: "$temperature" }
        }
    },
    {
        $group: {
            _id: "$_id.assetId",
            samplingModes: {
                $push: {
                    mode: "$_id.mode",
                    count: "$count",
                    avgTemp: "$avgTemp",
                    tempRange: {
                        min: "$minTemp",
                        max: "$maxTemp"
                    }
                }
            },
            totalSamples: { $sum: "$count" }
        }
    },
    {
        $lookup: {
            from: "assets",
            localField: "_id",
            foreignField: "assetId",
            as: "asset"
        }
    },
    {
        $unwind: "$asset"
    },
    {
        $project: {
            assetName: "$asset.name",
            totalSamples: 1,
            samplingBreakdown: "$samplingModes",
            adaptiveRatio: {
                $round: [{
                    $multiply: [{
                        $divide: [{
                            $sum: {
                                $map: {
                                    input: {
                                        $filter: {
                                            input: "$samplingModes",
                                            cond: { $ne: ["$$this.mode", "normal"] }
                                        }
                                    },
                                    as: "mode",
                                    in: "$$mode.count"
                                }
                            }
                        }, "$totalSamples"]
                    }, 100]
                }, 1]
            }
        }
    },
    { $sort: { adaptiveRatio: -1 } }
]).forEach(printjson);

// =====================================================
// QUERY 6: Route Performance Analysis
// =====================================================
print("\n6. ROUTE PERFORMANCE ANALYSIS");
print("-".repeat(40));

db.routes.aggregate([
    {
        $match: {
            status: { $in: ["completed", "in_progress"] }
        }
    },
    {
        $lookup: {
            from: "measurements",
            let: {
                aid: "$assetId",
                start: "$startTime",
                end: { $ifNull: ["$actualEndTime", new Date()] }
            },
            pipeline: [
                {
                    $match: {
                        $expr: {
                            $and: [
                                { $eq: ["$meta.assetId", "$$aid"] },
                                { $gte: ["$timestamp", "$$start"] },
                                { $lte: ["$timestamp", "$$end"] }
                            ]
                        }
                    }
                },
                {
                    $group: {
                        _id: null,
                        avgTemp: { $avg: "$temperature" },
                        minTemp: { $min: "$temperature" },
                        maxTemp: { $max: "$temperature" },
                        outOfRange: {
                            $sum: {
                                $cond: [
                                    { $or: [
                                        { $lt: ["$temperature", -25] },
                                        { $gt: ["$temperature", 8] }
                                    ]},
                                    1, 0
                                ]
                            }
                        },
                        totalReadings: { $sum: 1 }
                    }
                }
            ],
            as: "temperatureData"
        }
    },
    {
        $project: {
            routeId: 1,
            assetId: 1,
            status: 1,
            cargo: "$cargo.description",
            origin: "$origin.name",
            destination: "$destination.name",
            duration: {
                $cond: [
                    { $eq: ["$status", "completed"] },
                    { $divide: [
                        { $subtract: ["$actualEndTime", "$startTime"] },
                        3600000
                    ]},
                    { $divide: [
                        { $subtract: [new Date(), "$startTime"] },
                        3600000
                    ]}
                ]
            },
            temperatureStats: { $arrayElemAt: ["$temperatureData", 0] },
            requiredTemp: "$cargo.temperatureRequirement"
        }
    },
    {
        $project: {
            routeId: 1,
            assetId: 1,
            status: 1,
            cargo: 1,
            route: { $concat: ["$origin", " → ", "$destination"] },
            durationHours: { $round: ["$duration", 1] },
            tempCompliance: {
                avgTemp: { $round: [{ $ifNull: ["$temperatureStats.avgTemp", 0] }, 2] },
                minTemp: { $round: [{ $ifNull: ["$temperatureStats.minTemp", 0] }, 2] },
                maxTemp: { $round: [{ $ifNull: ["$temperatureStats.maxTemp", 0] }, 2] },
                excursions: { $ifNull: ["$temperatureStats.outOfRange", 0] },
                totalReadings: { $ifNull: ["$temperatureStats.totalReadings", 0] }
            }
        }
    },
    { $sort: { status: 1, routeId: -1 } },
    { $limit: 10 }
]).forEach(printjson);

// =====================================================
// QUERY 7: Battery Status Report
// =====================================================
print("\n7. SENSOR BATTERY STATUS");
print("-".repeat(40));

db.sensors.aggregate([
    {
        $lookup: {
            from: "measurements",
            let: { sid: "$sensorId" },
            pipeline: [
                {
                    $match: {
                        $expr: { $eq: ["$meta.sensorId", "$$sid"] },
                        batteryLevel: { $exists: true }
                    }
                },
                { $sort: { timestamp: -1 } },
                { $limit: 1 },
                { $project: { batteryLevel: 1, timestamp: 1 } }
            ],
            as: "lastBattery"
        }
    },
    {
        $project: {
            sensorId: 1,
            assetId: 1,
            sensorType: 1,
            model: 1,
            status: 1,
            currentBattery: {
                $ifNull: [
                    { $arrayElemAt: ["$lastBattery.batteryLevel", 0] },
                    "$batteryLevel"
                ]
            },
            lastUpdate: { $arrayElemAt: ["$lastBattery.timestamp", 0] },
            daysSinceInstall: {
                $divide: [
                    { $subtract: [new Date(), "$installedAt"] },
                    86400000
                ]
            }
        }
    },
    {
        $match: {
            currentBattery: { $lt: 30 }  // Low battery threshold
        }
    },
    {
        $lookup: {
            from: "assets",
            localField: "assetId",
            foreignField: "assetId",
            as: "asset"
        }
    },
    {
        $unwind: "$asset"
    },
    {
        $project: {
            sensorId: 1,
            assetName: "$asset.name",
            sensorType: 1,
            model: 1,
            batteryLevel: "$currentBattery",
            daysInService: { $round: ["$daysSinceInstall", 0] },
            urgency: {
                $switch: {
                    branches: [
                        { case: { $lt: ["$currentBattery", 10] }, then: "CRITICAL" },
                        { case: { $lt: ["$currentBattery", 20] }, then: "HIGH" },
                        { case: { $lt: ["$currentBattery", 30] }, then: "MEDIUM" }
                    ],
                    default: "LOW"
                }
            }
        }
    },
    { $sort: { batteryLevel: 1 } }
]).forEach(printjson);

// =====================================================
// QUERY 8: Compliance Report Summary
// =====================================================
print("\n8. COMPLIANCE REPORT SUMMARY");
print("-".repeat(40));

db.measurements.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
        }
    },
    {
        $lookup: {
            from: "assets",
            localField: "meta.assetId",
            foreignField: "assetId",
            as: "asset"
        }
    },
    {
        $unwind: "$asset"
    },
    {
        $addFields: {
            inCompliance: {
                $and: [
                    { $gte: ["$temperature", "$asset.temperatureRange.min"] },
                    { $lte: ["$temperature", "$asset.temperatureRange.max"] }
                ]
            }
        }
    },
    {
        $group: {
            _id: {
                assetId: "$meta.assetId",
                assetType: "$asset.assetType",
                date: { $dateToString: { format: "%Y-%m-%d", date: "$timestamp" } }
            },
            totalReadings: { $sum: 1 },
            compliantReadings: {
                $sum: { $cond: ["$inCompliance", 1, 0] }
            },
            minTemp: { $min: "$temperature" },
            maxTemp: { $max: "$temperature" },
            avgTemp: { $avg: "$temperature" }
        }
    },
    {
        $project: {
            date: "$_id.date",
            assetId: "$_id.assetId",
            assetType: "$_id.assetType",
            complianceRate: {
                $round: [{
                    $multiply: [
                        { $divide: ["$compliantReadings", "$totalReadings"] },
                        100
                    ]
                }, 2]
            },
            stats: {
                readings: "$totalReadings",
                compliant: "$compliantReadings",
                avgTemp: { $round: ["$avgTemp", 2] },
                tempRange: {
                    min: { $round: ["$minTemp", 2] },
                    max: { $round: ["$maxTemp", 2] }
                }
            }
        }
    },
    {
        $group: {
            _id: "$assetType",
            avgComplianceRate: { $avg: "$complianceRate" },
            minComplianceRate: { $min: "$complianceRate" },
            days: { $addToSet: "$date" },
            totalReadings: { $sum: "$stats.readings" },
            worstDay: {
                $min: {
                    date: "$date",
                    rate: "$complianceRate"
                }
            }
        }
    },
    {
        $project: {
            assetType: "$_id",
            overallCompliance: { $round: ["$avgComplianceRate", 2] },
            worstCompliance: { $round: ["$minComplianceRate", 2] },
            daysMonitored: { $size: "$days" },
            totalReadings: 1,
            status: {
                $switch: {
                    branches: [
                        { case: { $gte: ["$avgComplianceRate", 99] }, then: "EXCELLENT" },
                        { case: { $gte: ["$avgComplianceRate", 95] }, then: "GOOD" },
                        { case: { $gte: ["$avgComplianceRate", 90] }, then: "ACCEPTABLE" },
                        { case: { $lt: ["$avgComplianceRate", 90] }, then: "NEEDS IMPROVEMENT" }
                    ]
                }
            }
        }
    },
    { $sort: { overallCompliance: -1 } }
]).forEach(printjson);

// =====================================================
// SUMMARY
// =====================================================
print("\n" + "=".repeat(60));
print("QUERY EXERCISES COMPLETE");
print("Total collections: " + db.getCollectionNames().length);
print("Measurements count: " + db.measurements.countDocuments({}));
print("Active alerts: " + db.alerts.countDocuments({status: "active"}));
print("Assets monitored: " + db.assets.countDocuments({}));
print("=".repeat(60) + "\n");