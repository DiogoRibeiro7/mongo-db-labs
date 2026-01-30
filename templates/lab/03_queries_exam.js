/**
 * Query Exercises for {{LAB_NAME}}
 *
 * This file contains query exercises for students to practice
 * MongoDB aggregation pipelines and query techniques.
 *
 * Each query includes:
 * - Description of the problem
 * - Expected output format
 * - Reference solution
 *
 * Usage: mongosh 03_queries_exam.js
 */

// ============================================
// CONFIGURATION - REPLACE PLACEHOLDER
// ============================================
const DATABASE_NAME = "{{DATABASE_NAME}}";  // e.g., "iot_flood_demo"

// Connect to database
conn = new Mongo();
db = conn.getDB(DATABASE_NAME);

print(`\n${"=".repeat(50)}`);
print(`Query Exercises for ${DATABASE_NAME}`);
print(`${"=".repeat(50)}\n`);

// ============================================
// Helper Functions
// ============================================

function runQuery(queryNumber, description, pipeline, collection) {
    print(`\n--- Query ${queryNumber}: ${description} ---`);
    try {
        const startTime = Date.now();
        const result = db[collection].aggregate(pipeline).toArray();
        const duration = Date.now() - startTime;

        print(`Results (${result.length} documents, ${duration}ms):`);

        // Print first 5 results
        result.slice(0, 5).forEach(doc => {
            printjson(doc);
        });

        if (result.length > 5) {
            print(`... and ${result.length - 5} more`);
        }

        return result;
    } catch (error) {
        print(`ERROR: ${error.message}`);
        return null;
    }
}

function runFindQuery(queryNumber, description, filter, collection, options = {}) {
    print(`\n--- Query ${queryNumber}: ${description} ---`);
    try {
        const startTime = Date.now();
        let query = db[collection].find(filter);

        if (options.sort) query = query.sort(options.sort);
        if (options.limit) query = query.limit(options.limit);
        if (options.projection) query = query.projection(options.projection);

        const result = query.toArray();
        const duration = Date.now() - startTime;

        print(`Results (${result.length} documents, ${duration}ms):`);

        result.forEach(doc => {
            printjson(doc);
        });

        return result;
    } catch (error) {
        print(`ERROR: ${error.message}`);
        return null;
    }
}

// ============================================
// QUERY EXERCISES
// ============================================

// ------------------
// Basic Queries
// ------------------

print("\n" + "=".repeat(50));
print("SECTION 1: Basic Queries");
print("=".repeat(50));

// Query 1: Find documents with specific criteria
runFindQuery(
    "1.1",
    "Find all active items (EXAMPLE - REPLACE)",
    { status: "active" },  // Filter
    "example",  // Collection
    {
        projection: { name: 1, status: 1, createdAt: 1 },
        sort: { createdAt: -1 },
        limit: 10
    }
);

// Query 1.2: Count documents
print("\n--- Query 1.2: Count documents by category ---");
const count = db.example.countDocuments({ category: "category_a" });
print(`Count: ${count}`);

// ------------------
// Aggregation Queries
// ------------------

print("\n" + "=".repeat(50));
print("SECTION 2: Aggregation Pipelines");
print("=".repeat(50));

// Query 2.1: Group and count
runQuery(
    "2.1",
    "Count items by category (EXAMPLE - REPLACE)",
    [
        { $group: {
            _id: "$category",
            count: { $sum: 1 },
            items: { $push: "$name" }
        }},
        { $sort: { count: -1 }}
    ],
    "example"
);

// Query 2.2: Date aggregation
runQuery(
    "2.2",
    "Group by date (EXAMPLE - REPLACE)",
    [
        { $group: {
            _id: {
                year: { $year: "$createdAt" },
                month: { $month: "$createdAt" },
                day: { $dayOfMonth: "$createdAt" }
            },
            count: { $sum: 1 }
        }},
        { $sort: { "_id.year": 1, "_id.month": 1, "_id.day": 1 }}
    ],
    "example"
);

// ------------------
// Time-Series Queries (if applicable)
// ------------------

print("\n" + "=".repeat(50));
print("SECTION 3: Time-Series Analysis");
print("=".repeat(50));

// Query 3.1: Time-series aggregation
runQuery(
    "3.1",
    "Average values per hour (EXAMPLE - REPLACE)",
    [
        { $match: {
            ts: {
                $gte: new Date(Date.now() - 24*60*60*1000),  // Last 24 hours
                $lte: new Date()
            }
        }},
        { $group: {
            _id: {
                sensor: "$sensorId",
                hour: { $dateTrunc: { date: "$ts", unit: "hour" }}
            },
            avgValue: { $avg: "$value" },
            maxValue: { $max: "$value" },
            minValue: { $min: "$value" },
            count: { $sum: 1 }
        }},
        { $sort: { "_id.hour": 1, "_id.sensor": 1 }}
    ],
    "measurements"
);

// ------------------
// Complex Queries
// ------------------

print("\n" + "=".repeat(50));
print("SECTION 4: Complex Queries");
print("=".repeat(50));

// Query 4.1: Joins (lookups)
runQuery(
    "4.1",
    "Join collections (EXAMPLE - REPLACE)",
    [
        { $lookup: {
            from: "relatedCollection",
            localField: "referenceId",
            foreignField: "_id",
            as: "relatedData"
        }},
        { $unwind: "$relatedData" },
        { $project: {
            name: 1,
            relatedName: "$relatedData.name",
            combinedInfo: { $concat: ["$name", " - ", "$relatedData.name"] }
        }},
        { $limit: 5 }
    ],
    "example"
);

// Query 4.2: Window functions (MongoDB 5.0+)
runQuery(
    "4.2",
    "Moving average (EXAMPLE - REPLACE)",
    [
        { $setWindowFields: {
            partitionBy: "$sensorId",
            sortBy: { ts: 1 },
            output: {
                movingAvg: {
                    $avg: "$value",
                    window: {
                        documents: [-5, 5]  // 11-point moving average
                    }
                },
                rank: { $rank: {} }
            }
        }},
        { $limit: 10 }
    ],
    "measurements"
);

// ------------------
// Performance Analysis
// ------------------

print("\n" + "=".repeat(50));
print("SECTION 5: Performance Analysis");
print("=".repeat(50));

// Query 5.1: Explain plan
print("\n--- Query 5.1: Explain Plan Example ---");
const explainResult = db.example.find({ category: "category_a" }).explain("executionStats");
print("Execution stats:");
print(`  Documents examined: ${explainResult.executionStats.totalDocsExamined}`);
print(`  Documents returned: ${explainResult.executionStats.nReturned}`);
print(`  Execution time: ${explainResult.executionStats.executionTimeMillis}ms`);
print(`  Index used: ${explainResult.executionStats.executionStages.indexName || "NONE (collection scan)"}`);

// ------------------
// Student Exercises
// ------------------

print("\n" + "=".repeat(50));
print("SECTION 6: Student Exercises");
print("=".repeat(50));

print("\nTO DO: Complete these exercises");
print("Replace the null with your query solution\n");

// Exercise 1
print("Exercise 1: [Description of what student should query]");
print("Hint: [Helpful hint]");
const exercise1 = null;  // Student solution here
// Solution (comment out for students):
// const exercise1 = db.collection.find({...});

// Exercise 2
print("\nExercise 2: [Description of aggregation exercise]");
print("Hint: Use $group and $match stages");
const exercise2 = null;  // Student solution here
// Solution (comment out for students):
// const exercise2 = db.collection.aggregate([...]);

// Add more exercises as needed...

// ============================================
// Summary Statistics
// ============================================

print("\n" + "=".repeat(50));
print("Database Statistics");
print("=".repeat(50));

db.getCollectionNames().forEach(collName => {
    const stats = db[collName].stats();
    const indexes = db[collName].getIndexes();

    print(`\nCollection: ${collName}`);
    print(`  Document count: ${stats.count}`);
    print(`  Average document size: ${stats.avgObjSize} bytes`);
    print(`  Total size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
    print(`  Indexes: ${indexes.map(idx => idx.name).join(", ")}`);
});

print("\n✓ Query exercises complete!");
print("\nNote: Review the solutions and experiment with your own queries.");