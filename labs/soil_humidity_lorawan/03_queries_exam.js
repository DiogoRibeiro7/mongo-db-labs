// 03_queries_exam.js
// Usage:
//   mongosh 03_queries_exam.js
//
// Exam-style queries for the IoT flood demo dataset.
// Database: iot_flood_demo
//
// Collections:
// - sites
// - sensors
// - ratingCurves
// - samplingPolicies
// - policyState
// - measurements (time series): { ts, meta:{siteId,sensorId,metric}, value, batteryPct, signalQuality, qcFlags }
// - alerts: { ts, siteId, alertType, status(OPEN|RESOLVED), severity, context }
//
// Notes:
// - Metrics are stored as separate measurement documents per metric.
// - Many queries use $dateTrunc (MongoDB 5.0+) and $setWindowFields (MongoDB 5.0+).

const dbName = "iot_flood_demo";
const dbRef = db.getSiblingDB(dbName);

function printTitle(title) {
  print("\n============================================================");
  print(title);
  print("============================================================\n");
}

// ------------------------------------------------------------
// Q1) Average flow rate (m3/s) per hour and per site
// ------------------------------------------------------------
printTitle("Q1) Average flow rate (flowRateM3s) per hour and per site");

dbRef.measurements.aggregate([
  { $match: { "meta.metric": "flowRateM3s" } },
  {
    $group: {
      _id: {
        siteId: "$meta.siteId",
        hour: { $dateTrunc: { date: "$ts", unit: "hour" } }
      },
      avgFlowM3s: { $avg: "$value" },
      maxFlowM3s: { $max: "$value" },
      minFlowM3s: { $min: "$value" },
      n: { $sum: 1 }
    }
  },
  {
    $lookup: {
      from: "sites",
      localField: "_id.siteId",
      foreignField: "_id",
      as: "site"
    }
  },
  { $unwind: "$site" },
  {
    $project: {
      _id: 0,
      siteCode: "$site.siteCode",
      siteType: "$site.siteType",
      hour: "$_id.hour",
      avgFlowM3s: { $round: ["$avgFlowM3s", 3] },
      maxFlowM3s: { $round: ["$maxFlowM3s", 3] },
      minFlowM3s: { $round: ["$minFlowM3s", 3] },
      n: 1
    }
  },
  { $sort: { hour: 1, siteCode: 1 } },
  { $limit: 50 }
]);

// ------------------------------------------------------------
// Q2) Top 5 highest water levels in the last 2 hours (all sites)
// ------------------------------------------------------------
printTitle("Q2) Top 5 highest water levels (waterLevelM) in the last 2 hours");

const now = new Date();
const twoHoursAgo = new Date(now.getTime() - 2 * 3600 * 1000);

dbRef.measurements.aggregate([
  { $match: { "meta.metric": "waterLevelM", ts: { $gte: twoHoursAgo } } },
  { $sort: { value: -1 } },
  { $limit: 5 },
  {
    $lookup: {
      from: "sites",
      localField: "meta.siteId",
      foreignField: "_id",
      as: "site"
    }
  },
  { $unwind: "$site" },
  {
    $project: {
      _id: 0,
      ts: 1,
      siteCode: "$site.siteCode",
      siteType: "$site.siteType",
      catchmentId: "$site.catchmentId",
      waterLevelM: "$value",
      batteryPct: 1,
      signalQuality: 1
    }
  }
]);

// ------------------------------------------------------------
// Q3) Latest measurement per site and metric (last known value)
// ------------------------------------------------------------
printTitle("Q3) Latest measurement per site and metric");

dbRef.measurements.aggregate([
  { $sort: { ts: -1 } },
  {
    $group: {
      _id: { siteId: "$meta.siteId", metric: "$meta.metric" },
      ts: { $first: "$ts" },
      value: { $first: "$value" },
      batteryPct: { $first: "$batteryPct" },
      signalQuality: { $first: "$signalQuality" },
      qcFlags: { $first: "$qcFlags" }
    }
  },
  {
    $lookup: {
      from: "sites",
      localField: "_id.siteId",
      foreignField: "_id",
      as: "site"
    }
  },
  { $unwind: "$site" },
  {
    $project: {
      _id: 0,
      siteCode: "$site.siteCode",
      metric: "$_id.metric",
      ts: 1,
      value: 1,
      batteryPct: 1,
      signalQuality: 1,
      qcFlags: 1
    }
  },
  { $sort: { siteCode: 1, metric: 1 } },
  { $limit: 80 }
]);

// ------------------------------------------------------------
// Q4) Rainfall total per catchment by hour
// (Using rainfallAccumMm; max(accum) - min(accum) per hour)
// ------------------------------------------------------------
printTitle("Q4) Rainfall (mm) per catchment by hour (using rainfallAccumMm)");

dbRef.measurements.aggregate([
  { $match: { "meta.metric": "rainfallAccumMm" } },
  {
    $lookup: {
      from: "sites",
      localField: "meta.siteId",
      foreignField: "_id",
      as: "site"
    }
  },
  { $unwind: "$site" },
  {
    $group: {
      _id: {
        catchmentId: "$site.catchmentId",
        hour: { $dateTrunc: { date: "$ts", unit: "hour" } }
      },
      minAccum: { $min: "$value" },
      maxAccum: { $max: "$value" }
    }
  },
  {
    $project: {
      _id: 0,
      catchmentId: "$_id.catchmentId",
      hour: "$_id.hour",
      rainfallMm: { $round: [{ $subtract: ["$maxAccum", "$minAccum"] }, 3] }
    }
  },
  { $sort: { hour: 1, catchmentId: 1 } },
  { $limit: 80 }
]);

// ------------------------------------------------------------
// Q5) Potential high risk moments: waterLevel above local thresholds
// ------------------------------------------------------------
printTitle("Q5) Potential high risk moments (water level above local thresholds)");

dbRef.measurements.aggregate([
  { $match: { "meta.metric": "waterLevelM" } },
  {
    $lookup: {
      from: "sites",
      localField: "meta.siteId",
      foreignField: "_id",
      as: "site"
    }
  },
  { $unwind: "$site" },
  {
    $addFields: {
      isRiver: { $eq: ["$site.siteType", "river"] },
      isStorm: { $eq: ["$site.siteType", "stormwater"] }
    }
  },
  {
    $addFields: {
      thresholdM: {
        $cond: [
          "$isRiver",
          "$site.thresholds.warningLevelM",
          "$site.thresholds.surchargeLevelM"
        ]
      }
    }
  },
  {
    $match: {
      $expr: { $and: [{ $ne: ["$thresholdM", null] }, { $gte: ["$value", "$thresholdM"] }] }
    }
  },
  { $sort: { ts: -1, value: -1 } },
  { $limit: 20 },
  {
    $project: {
      _id: 0,
      ts: 1,
      siteCode: "$site.siteCode",
      siteType: "$site.siteType",
      waterLevelM: "$value",
      thresholdM: 1,
      batteryPct: 1,
      signalQuality: 1
    }
  }
]);

// ------------------------------------------------------------
// Q6) Lagged join: rainfallRate vs river waterLevel (5-min buckets)
// ------------------------------------------------------------
printTitle("Q6) Lagged join: rainfallRate vs river waterLevel (5-min buckets, configurable lag)");

const bucketMinutes = 5;
const lagMinutes = 30; // try 10/20/30/45

dbRef.measurements.aggregate([
  { $match: { "meta.metric": "rainfallRateMmh" } },
  {
    $lookup: {
      from: "sites",
      localField: "meta.siteId",
      foreignField: "_id",
      as: "site"
    }
  },
  { $unwind: "$site" },
  {
    $project: {
      catchmentId: "$site.catchmentId",
      tBucket: { $dateTrunc: { date: "$ts", unit: "minute", binSize: bucketMinutes } },
      rainRate: "$value"
    }
  },
  {
    $group: {
      _id: { catchmentId: "$catchmentId", tBucket: "$tBucket" },
      rainRateAvg: { $avg: "$rainRate" }
    }
  },
  {
    $project: {
      _id: 0,
      catchmentId: "$_id.catchmentId",
      tBucket: "$_id.tBucket",
      rainRateAvg: { $round: ["$rainRateAvg", 3] },
      tBucketLagged: { $dateSubtract: { startDate: "$_id.tBucket", unit: "minute", amount: lagMinutes } }
    }
  },
  {
    $lookup: {
      from: "measurements",
      let: { catchmentId: "$catchmentId", tBucketLagged: "$tBucketLagged" },
      pipeline: [
        { $match: { "meta.metric": "waterLevelM" } },
        {
          $lookup: {
            from: "sites",
            localField: "meta.siteId",
            foreignField: "_id",
            as: "site"
          }
        },
        { $unwind: "$site" },
        { $match: { "site.siteType": "river" } },
        {
          $project: {
            catchmentId: "$site.catchmentId",
            siteCode: "$site.siteCode",
            tBucket: { $dateTrunc: { date: "$ts", unit: "minute", binSize: bucketMinutes } },
            level: "$value"
          }
        },
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$catchmentId", "$$catchmentId"] },
                { $eq: ["$tBucket", "$$tBucketLagged"] }
              ]
            }
          }
        },
        {
          $group: {
            _id: { siteCode: "$siteCode", tBucket: "$tBucket" },
            waterLevelAvg: { $avg: "$level" }
          }
        },
        { $project: { _id: 0, siteCode: "$_id.siteCode", tBucket: "$_id.tBucket", waterLevelAvg: { $round: ["$waterLevelAvg", 3] } } }
      ],
      as: "riverLevel"
    }
  },
  { $unwind: "$riverLevel" },
  {
    $project: {
      catchmentId: 1,
      rainBucket: "$tBucket",
      rainRateAvg: 1,
      riverSiteCode: "$riverLevel.siteCode",
      riverBucketLagged: "$riverLevel.tBucket",
      waterLevelAvg: "$riverLevel.waterLevelAvg"
    }
  },
  { $sort: { rainBucket: 1, riverSiteCode: 1 } },
  { $limit: 60 }
]);

// ------------------------------------------------------------
// Q7) Alert counts by site and type (OPEN/RESOLVED)
// ------------------------------------------------------------
printTitle("Q7) Alert counts by site and alertType");

dbRef.alerts.aggregate([
  {
    $group: {
      _id: { siteId: "$siteId", alertType: "$alertType", status: "$status" },
      n: { $sum: 1 },
      firstTs: { $min: "$ts" },
      lastTs: { $max: "$ts" }
    }
  },
  {
    $lookup: {
      from: "sites",
      localField: "_id.siteId",
      foreignField: "_id",
      as: "site"
    }
  },
  { $unwind: "$site" },
  {
    $project: {
      _id: 0,
      siteCode: "$site.siteCode",
      alertType: "$_id.alertType",
      status: "$_id.status",
      n: 1,
      firstTs: 1,
      lastTs: 1
    }
  },
  { $sort: { siteCode: 1, alertType: 1, status: 1 } }
]);

// ------------------------------------------------------------
// Q8) Alert durations (OPEN -> next RESOLVED) using window functions
// ------------------------------------------------------------
printTitle("Q8) Alert durations (OPEN to next RESOLVED) per site and type");

dbRef.alerts.aggregate([
  { $sort: { siteId: 1, alertType: 1, ts: 1 } },
  {
    $setWindowFields: {
      partitionBy: { siteId: "$siteId", alertType: "$alertType" },
      sortBy: { ts: 1 },
      output: {
        nextTs: { $shift: { output: "$ts", by: 1 } },
        nextStatus: { $shift: { output: "$status", by: 1 } }
      }
    }
  },
  { $match: { status: "OPEN", nextStatus: "RESOLVED" } },
  {
    $addFields: {
      durationSec: { $dateDiff: { startDate: "$ts", endDate: "$nextTs", unit: "second" } }
    }
  },
  {
    $lookup: { from: "sites", localField: "siteId", foreignField: "_id", as: "site" }
  },
  { $unwind: "$site" },
  {
    $project: {
      _id: 0,
      siteCode: "$site.siteCode",
      alertType: 1,
      openTs: "$ts",
      resolveTs: "$nextTs",
      durationSec: 1
    }
  },
  { $sort: { durationSec: -1 } },
  { $limit: 30 }
]);

// ------------------------------------------------------------
// Q9) Non-OK QC flags
// ------------------------------------------------------------
printTitle("Q9) Measurements with non-OK qcFlags");

dbRef.measurements.aggregate([
  { $match: { qcFlags: { $ne: ["OK"] } } },
  { $sort: { ts: -1 } },
  { $limit: 30 },
  {
    $lookup: { from: "sites", localField: "meta.siteId", foreignField: "_id", as: "site" }
  },
  { $unwind: "$site" },
  {
    $project: {
      _id: 0,
      ts: 1,
      siteCode: "$site.siteCode",
      metric: "$meta.metric",
      value: 1,
      qcFlags: 1,
      batteryPct: 1
    }
  }
]);

// ------------------------------------------------------------
// Q10) Sampling frequency proxy: waterLevelM points per hour
// ------------------------------------------------------------
printTitle("Q10) Sampling frequency proxy: waterLevelM points per hour (per site)");

dbRef.measurements.aggregate([
  { $match: { "meta.metric": "waterLevelM" } },
  {
    $group: {
      _id: { siteId: "$meta.siteId", hour: { $dateTrunc: { date: "$ts", unit: "hour" } } },
      points: { $sum: 1 },
      avgBattery: { $avg: "$batteryPct" }
    }
  },
  {
    $lookup: { from: "sites", localField: "_id.siteId", foreignField: "_id", as: "site" }
  },
  { $unwind: "$site" },
  {
    $project: {
      _id: 0,
      siteCode: "$site.siteCode",
      siteType: "$site.siteType",
      hour: "$_id.hour",
      points: 1,
      avgBattery: { $round: ["$avgBattery", 1] },
      inferredMode: {
        $switch: {
          branches: [
            { case: { $gte: ["$points", 300] }, then: "CRITICAL_like" },
            { case: { $gte: ["$points", 40] }, then: "HIGH_like" },
            { case: { $gte: ["$points", 10] }, then: "NORMAL_like" }
          ],
          default: "LOW_like"
        }
      }
    }
  },
  { $sort: { hour: 1, siteCode: 1 } },
  { $limit: 80 }
]);

// ------------------------------------------------------------
// Q11) Battery trend per site (avg per hour, using waterLevelM docs)
// ------------------------------------------------------------
printTitle("Q11) Battery trend per site (avg battery per hour)");

dbRef.measurements.aggregate([
  { $match: { "meta.metric": "waterLevelM" } },
  {
    $group: {
      _id: { siteId: "$meta.siteId", hour: { $dateTrunc: { date: "$ts", unit: "hour" } } },
      avgBattery: { $avg: "$batteryPct" },
      minBattery: { $min: "$batteryPct" }
    }
  },
  {
    $lookup: { from: "sites", localField: "_id.siteId", foreignField: "_id", as: "site" }
  },
  { $unwind: "$site" },
  {
    $project: {
      _id: 0,
      siteCode: "$site.siteCode",
      siteType: "$site.siteType",
      hour: "$_id.hour",
      avgBattery: { $round: ["$avgBattery", 1] },
      minBattery: 1
    }
  },
  { $sort: { siteCode: 1, hour: 1 } },
  { $limit: 80 }
]);

// ------------------------------------------------------------
// Q12) Severe alerts per catchment (OPEN only)
// ------------------------------------------------------------
printTitle("Q12) Severe alerts per catchment (OPEN events only)");

dbRef.alerts.aggregate([
  { $match: { status: "OPEN", alertType: { $in: ["FLOOD_SEVERE", "STORMWATER_OVERFLOW"] } } },
  {
    $lookup: { from: "sites", localField: "siteId", foreignField: "_id", as: "site" }
  },
  { $unwind: "$site" },
  {
    $group: {
      _id: { catchmentId: "$site.catchmentId", alertType: "$alertType" },
      n: { $sum: 1 },
      firstTs: { $min: "$ts" },
      lastTs: { $max: "$ts" }
    }
  },
  {
    $project: {
      _id: 0,
      catchmentId: "$_id.catchmentId",
      alertType: "$_id.alertType",
      opens: "$n",
      firstTs: 1,
      lastTs: 1
    }
  },
  { $sort: { opens: -1, catchmentId: 1 } }
]);

print("\n✅ Done. Tip: adjust lagMinutes and bucketMinutes in Q6 to explore different response times.\n");
