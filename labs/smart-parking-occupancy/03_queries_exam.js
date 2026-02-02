// =====================================================
// Smart Parking Occupancy - Query Exercises
// Database: smartparking_db
// =====================================================

// Note: Database is already selected by the lab runner

print("\n" + "=".repeat(60));
print("SMART PARKING OCCUPANCY - QUERY EXERCISES");
print("=".repeat(60));

// =====================================================
// QUERY 1: Current Parking Occupancy Overview
// =====================================================
print("\n1. CURRENT PARKING OCCUPANCY BY ZONE");
print("-" + "-".repeat(40));

// Get current occupancy rate for each zone
db.zones.aggregate([
    {
        $lookup: {
            from: "parking_spots",
            localField: "zoneId",
            foreignField: "zoneId",
            as: "spots"
        }
    },
    {
        $project: {
            zoneId: 1,
            name: 1,
            type: 1,
            totalSpots: 1,
            occupied: {
                $size: {
                    $filter: {
                        input: "$spots",
                        cond: { $eq: ["$$this.status", "occupied"] }
                    }
                }
            },
            available: {
                $size: {
                    $filter: {
                        input: "$spots",
                        cond: { $eq: ["$$this.status", "available"] }
                    }
                }
            },
            reserved: {
                $size: {
                    $filter: {
                        input: "$spots",
                        cond: { $eq: ["$$this.status", "reserved"] }
                    }
                }
            },
            violations: {
                $size: {
                    $filter: {
                        input: "$spots",
                        cond: { $eq: ["$$this.status", "violation"] }
                    }
                }
            }
        }
    },
    {
        $addFields: {
            occupancyRate: {
                $round: [
                    { $multiply: [
                        { $divide: ["$occupied", "$totalSpots"] },
                        100
                    ]},
                    1
                ]
            }
        }
    },
    { $sort: { occupancyRate: -1 } }
]).forEach(zone => {
    print(`${zone.name} (${zone.type}):`);
    print(`  Occupancy: ${zone.occupancyRate}% (${zone.occupied}/${zone.totalSpots})`);
    print(`  Available: ${zone.available}, Reserved: ${zone.reserved}, Violations: ${zone.violations}`);
});

// =====================================================
// QUERY 2: Hourly Occupancy Patterns (Last 24 Hours)
// =====================================================
print("\n2. HOURLY OCCUPANCY RATE ANALYSIS");
print("-" + "-".repeat(40));

// Analyze occupancy patterns by hour
db.occupancy_readings.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
        }
    },
    {
        $group: {
            _id: {
                hour: { $hour: "$timestamp" },
                zoneId: "$meta.zoneId"
            },
            totalReadings: { $sum: 1 },
            occupiedReadings: {
                $sum: { $cond: ["$occupied", 1, 0] }
            },
            avgConfidence: { $avg: "$confidence" }
        }
    },
    {
        $group: {
            _id: "$_id.hour",
            avgOccupancyRate: {
                $avg: {
                    $multiply: [
                        { $divide: ["$occupiedReadings", "$totalReadings"] },
                        100
                    ]
                }
            },
            avgConfidence: { $avg: "$avgConfidence" },
            zonesReporting: { $sum: 1 }
        }
    },
    { $sort: { _id: 1 } },
    { $limit: 10 }
]).forEach(hour => {
    print(`Hour ${hour._id}:00 - Occupancy: ${hour.avgOccupancyRate.toFixed(1)}%, ` +
          `Confidence: ${(hour.avgConfidence * 100).toFixed(1)}%`);
});

// =====================================================
// QUERY 3: Busiest Parking Zones
// =====================================================
print("\n3. BUSIEST PARKING ZONES (BY TURNOVER)");
print("-" + "-".repeat(40));

// Find zones with highest turnover (occupancy changes)
db.events.aggregate([
    {
        $match: {
            eventType: "occupancy_change",
            timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
        }
    },
    {
        $group: {
            _id: "$zoneId",
            totalChanges: { $sum: 1 },
            arrivals: {
                $sum: {
                    $cond: [
                        { $eq: ["$details.newStatus", "occupied"] },
                        1, 0
                    ]
                }
            },
            departures: {
                $sum: {
                    $cond: [
                        { $eq: ["$details.newStatus", "available"] },
                        1, 0
                    ]
                }
            },
            avgStayDuration: {
                $avg: "$details.duration"
            }
        }
    },
    {
        $lookup: {
            from: "zones",
            localField: "_id",
            foreignField: "zoneId",
            as: "zone"
        }
    },
    { $unwind: "$zone" },
    {
        $project: {
            zoneName: "$zone.name",
            zoneType: "$zone.type",
            totalChanges: 1,
            arrivals: 1,
            departures: 1,
            avgStayMinutes: { $round: ["$avgStayDuration", 0] },
            turnoverRate: {
                $round: [
                    { $divide: ["$totalChanges", "$zone.totalSpots"] },
                    2
                ]
            }
        }
    },
    { $sort: { turnoverRate: -1 } },
    { $limit: 5 }
]).forEach(zone => {
    print(`${zone.zoneName} (${zone.zoneType}):`);
    print(`  Turnover Rate: ${zone.turnoverRate} changes/spot`);
    print(`  Arrivals: ${zone.arrivals}, Departures: ${zone.departures}`);
    print(`  Avg Stay: ${zone.avgStayMinutes || 'N/A'} minutes`);
});

// =====================================================
// QUERY 4: Overstay Violations Analysis
// =====================================================
print("\n4. OVERSTAY VIOLATIONS SUMMARY");
print("-" + "-".repeat(40));

// Analyze violations by type and zone
db.violations.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
        }
    },
    {
        $group: {
            _id: {
                type: "$type",
                zoneId: "$zoneId"
            },
            count: { $sum: 1 },
            totalFines: { $sum: "$fine.amount" },
            avgFine: { $avg: "$fine.amount" },
            paidCount: {
                $sum: { $cond: [{ $eq: ["$status", "paid"] }, 1, 0] }
            }
        }
    },
    {
        $group: {
            _id: "$_id.type",
            totalViolations: { $sum: "$count" },
            totalRevenue: { $sum: "$totalFines" },
            avgFine: { $avg: "$avgFine" },
            collectionRate: {
                $multiply: [
                    { $divide: [
                        { $sum: "$paidCount" },
                        { $sum: "$count" }
                    ]},
                    100
                ]
            }
        }
    },
    { $sort: { totalViolations: -1 } }
]).forEach(violation => {
    print(`${violation._id}:`);
    print(`  Count: ${violation.totalViolations}`);
    print(`  Total Revenue: $${violation.totalRevenue.toFixed(2)}`);
    print(`  Avg Fine: $${violation.avgFine.toFixed(2)}`);
    print(`  Collection Rate: ${violation.collectionRate.toFixed(1)}%`);
});

// =====================================================
// QUERY 5: Sensor Performance Analysis
// =====================================================
print("\n5. SENSOR PERFORMANCE METRICS");
print("-" + "-".repeat(40));

// Analyze sensor reliability and confidence
db.occupancy_readings.aggregate([
    {
        $match: {
            timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
        }
    },
    {
        $lookup: {
            from: "sensors",
            localField: "meta.sensorId",
            foreignField: "sensorId",
            as: "sensor"
        }
    },
    { $unwind: "$sensor" },
    {
        $group: {
            _id: "$sensor.type",
            totalReadings: { $sum: 1 },
            avgConfidence: { $avg: "$confidence" },
            minConfidence: { $min: "$confidence" },
            maxConfidence: { $max: "$confidence" },
            avgBatteryLevel: { $avg: "$batteryLevel" },
            avgSignalStrength: { $avg: "$signalStrength" },
            avgProcessingTime: { $avg: "$processingTime" }
        }
    },
    {
        $project: {
            sensorType: "$_id",
            totalReadings: 1,
            avgConfidence: { $round: [{ $multiply: ["$avgConfidence", 100] }, 1] },
            confidenceRange: {
                $concat: [
                    { $toString: { $round: [{ $multiply: ["$minConfidence", 100] }, 1] } },
                    "-",
                    { $toString: { $round: [{ $multiply: ["$maxConfidence", 100] }, 1] } },
                    "%"
                ]
            },
            avgBatteryLevel: { $round: ["$avgBatteryLevel", 0] },
            avgSignalStrength: { $round: ["$avgSignalStrength", 0] },
            avgProcessingTime: { $round: ["$avgProcessingTime", 1] }
        }
    },
    { $sort: { avgConfidence: -1 } }
]).forEach(sensor => {
    print(`${sensor.sensorType}:`);
    print(`  Readings: ${sensor.totalReadings}`);
    print(`  Avg Confidence: ${sensor.avgConfidence}% (Range: ${sensor.confidenceRange})`);
    print(`  Battery: ${sensor.avgBatteryLevel}%, Signal: ${sensor.avgSignalStrength} dBm`);
    print(`  Processing: ${sensor.avgProcessingTime}ms`);
});

// =====================================================
// QUERY 6: Peak Hours and Revenue Analysis
// =====================================================
print("\n6. PEAK HOURS AND REVENUE OPTIMIZATION");
print("-" + "-".repeat(40));

// Identify peak hours for revenue optimization
db.parking_spots.aggregate([
    {
        $match: {
            "currentOccupant": { $exists: true, $ne: null }
        }
    },
    {
        $lookup: {
            from: "zones",
            localField: "zoneId",
            foreignField: "zoneId",
            as: "zone"
        }
    },
    { $unwind: "$zone" },
    {
        $group: {
            _id: {
                hour: { $hour: "$currentOccupant.entryTime" },
                zoneType: "$zone.type"
            },
            spotCount: { $sum: 1 },
            potentialRevenue: {
                $sum: {
                    $multiply: [
                        "$zone.pricing.perHour",
                        {
                            $divide: [
                                { $subtract: [
                                    { $ifNull: ["$currentOccupant.paidUntil", new Date()] },
                                    "$currentOccupant.entryTime"
                                ]},
                                3600000  // Convert to hours
                            ]
                        }
                    ]
                }
            }
        }
    },
    {
        $group: {
            _id: "$_id.hour",
            totalSpots: { $sum: "$spotCount" },
            totalRevenue: { $sum: "$potentialRevenue" },
            zoneTypes: { $addToSet: "$_id.zoneType" }
        }
    },
    { $sort: { totalRevenue: -1 } },
    { $limit: 5 }
]).forEach(peak => {
    print(`Hour ${peak._id}:00:`);
    print(`  Active Spots: ${peak.totalSpots}`);
    print(`  Potential Revenue: $${peak.totalRevenue.toFixed(2)}`);
    print(`  Zone Types: ${peak.zoneTypes.join(", ")}`);
});

// =====================================================
// QUERY 7: Sensor Offline Events
// =====================================================
print("\n7. SENSOR RELIABILITY REPORT");
print("-" + "-".repeat(40));

// Find sensors with offline events
db.events.aggregate([
    {
        $match: {
            eventType: { $in: ["sensor_offline", "sensor_fault"] },
            timestamp: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
        }
    },
    {
        $group: {
            _id: "$sensorId",
            offlineEvents: { $sum: 1 },
            lastOffline: { $max: "$timestamp" },
            totalDowntime: {
                $sum: {
                    $cond: [
                        { $ne: ["$endTime", null] },
                        { $subtract: ["$endTime", "$timestamp"] },
                        0
                    ]
                }
            }
        }
    },
    {
        $lookup: {
            from: "sensors",
            localField: "_id",
            foreignField: "sensorId",
            as: "sensor"
        }
    },
    { $unwind: { path: "$sensor", preserveNullAndEmptyArrays: true } },
    {
        $project: {
            sensorId: "$_id",
            sensorType: "$sensor.type",
            spotId: "$sensor.spotId",
            offlineEvents: 1,
            lastOffline: 1,
            downtimeHours: {
                $round: [
                    { $divide: ["$totalDowntime", 3600000] },
                    1
                ]
            },
            currentStatus: "$sensor.status"
        }
    },
    { $sort: { offlineEvents: -1 } },
    { $limit: 10 }
]).forEach(sensor => {
    print(`Sensor ${sensor.sensorId} (${sensor.sensorType || 'Unknown'}):`);
    print(`  Offline Events: ${sensor.offlineEvents}`);
    print(`  Total Downtime: ${sensor.downtimeHours} hours`);
    print(`  Current Status: ${sensor.currentStatus || 'Unknown'}`);
});

// =====================================================
// QUERY 8: Zone Performance Dashboard
// =====================================================
print("\n8. ZONE PERFORMANCE DASHBOARD");
print("-" + "-".repeat(40));

// Comprehensive zone performance metrics
db.zones.aggregate([
    {
        $lookup: {
            from: "parking_spots",
            localField: "zoneId",
            foreignField: "zoneId",
            as: "spots"
        }
    },
    {
        $lookup: {
            from: "violations",
            let: { zoneId: "$zoneId" },
            pipeline: [
                {
                    $match: {
                        $expr: { $eq: ["$zoneId", "$$zoneId"] },
                        timestamp: { $gte: new Date(Date.now() - 30*24*60*60*1000) }
                    }
                }
            ],
            as: "violations"
        }
    },
    {
        $lookup: {
            from: "events",
            let: { zoneId: "$zoneId" },
            pipeline: [
                {
                    $match: {
                        $expr: { $eq: ["$zoneId", "$$zoneId"] },
                        eventType: "occupancy_change",
                        timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
                    }
                }
            ],
            as: "recentEvents"
        }
    },
    {
        $project: {
            zoneId: 1,
            name: 1,
            type: 1,
            totalSpots: 1,
            currentOccupancy: {
                $size: {
                    $filter: {
                        input: "$spots",
                        cond: { $eq: ["$$this.status", "occupied"] }
                    }
                }
            },
            sensorCoverage: {
                $multiply: [
                    {
                        $divide: [
                            {
                                $size: {
                                    $filter: {
                                        input: "$spots",
                                        cond: { $ne: ["$$this.sensorId", null] }
                                    }
                                }
                            },
                            "$totalSpots"
                        ]
                    },
                    100
                ]
            },
            monthlyViolations: { $size: "$violations" },
            violationRevenue: { $sum: "$violations.fine.amount" },
            dailyTurnover: { $size: "$recentEvents" },
            baseHourlyRate: "$pricing.perHour"
        }
    },
    {
        $addFields: {
            occupancyRate: {
                $round: [
                    { $multiply: [
                        { $divide: ["$currentOccupancy", "$totalSpots"] },
                        100
                    ]},
                    1
                ]
            },
            estimatedDailyRevenue: {
                $round: [
                    {
                        $multiply: [
                            "$currentOccupancy",
                            "$baseHourlyRate",
                            8  // Assume 8 hours average occupancy
                        ]
                    },
                    2
                ]
            }
        }
    },
    { $sort: { estimatedDailyRevenue: -1 } }
]).forEach(zone => {
    print(`\n${zone.name} (${zone.type}):`);
    print(`  Capacity: ${zone.totalSpots} spots`);
    print(`  Current Occupancy: ${zone.occupancyRate}% (${zone.currentOccupancy}/${zone.totalSpots})`);
    print(`  Sensor Coverage: ${zone.sensorCoverage.toFixed(1)}%`);
    print(`  Daily Turnover: ${zone.dailyTurnover} vehicles`);
    print(`  Monthly Violations: ${zone.monthlyViolations} ($${zone.violationRevenue.toFixed(2)})`);
    print(`  Est. Daily Revenue: $${zone.estimatedDailyRevenue}`);
});

// =====================================================
// Summary Statistics
// =====================================================
print("\n" + "=".repeat(60));
print("QUERY EXERCISES COMPLETE");

// Get collection counts
const stats = {
    zones: db.zones.countDocuments(),
    spots: db.parking_spots.countDocuments(),
    sensors: db.sensors.countDocuments(),
    readings: db.occupancy_readings.countDocuments(),
    events: db.events.countDocuments(),
    violations: db.violations.countDocuments()
};

print(`Total zones: ${stats.zones}`);
print(`Total parking spots: ${stats.spots}`);
print(`Total sensors: ${stats.sensors}`);
print(`Total readings: ${stats.readings}`);
print(`Total events: ${stats.events}`);
print(`Total violations: ${stats.violations}`);

// Calculate system-wide metrics
const systemMetrics = db.parking_spots.aggregate([
    {
        $group: {
            _id: null,
            totalSpots: { $sum: 1 },
            occupiedSpots: {
                $sum: { $cond: [{ $eq: ["$status", "occupied"] }, 1, 0] }
            },
            spotsWithSensors: {
                $sum: { $cond: [{ $ne: ["$sensorId", null] }, 1, 0] }
            }
        }
    }
]).next();

if (systemMetrics) {
    const occupancyRate = (systemMetrics.occupiedSpots / systemMetrics.totalSpots * 100).toFixed(1);
    const sensorCoverage = (systemMetrics.spotsWithSensors / systemMetrics.totalSpots * 100).toFixed(1);

    print(`\nSystem-wide Metrics:`);
    print(`  Overall Occupancy: ${occupancyRate}%`);
    print(`  Sensor Coverage: ${sensorCoverage}%`);
}

print("=" + "=".repeat(60) + "\n");