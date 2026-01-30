/**
 * MongoDB Setup Script for {{LAB_NAME}}
 *
 * This script:
 * 1. Creates the database and collections
 * 2. Sets up indexes for query performance
 * 3. Applies schema validators (optional)
 *
 * Usage: mongosh 00_setup_mongodb.js
 */

// ============================================
// REPLACE THESE PLACEHOLDERS
// ============================================
const DATABASE_NAME = "{{DATABASE_NAME}}";  // e.g., "iot_flood_demo"

// Connect to MongoDB
conn = new Mongo();
db = conn.getDB(DATABASE_NAME);

print(`\n=== Setting up database: ${DATABASE_NAME} ===\n`);

// ============================================
// Helper Functions
// ============================================

function createCollectionIfNotExists(name, options = {}) {
    const collections = db.getCollectionNames();
    if (!collections.includes(name)) {
        db.createCollection(name, options);
        print(`✓ Created collection: ${name}`);
    } else {
        print(`○ Collection exists: ${name}`);
    }
}

function createIndexSafely(collection, index, options = {}) {
    try {
        db[collection].createIndex(index, options);
        print(`✓ Created index on ${collection}: ${JSON.stringify(index)}`);
    } catch (e) {
        if (e.codeName === 'IndexOptionsConflict' || e.code === 85) {
            print(`○ Index exists on ${collection}: ${JSON.stringify(index)}`);
        } else {
            throw e;
        }
    }
}

// ============================================
// Create Collections
// ============================================

print("\n--- Creating Collections ---");

// Example: Regular collection
createCollectionIfNotExists("sites");

// Example: Time-series collection (if needed)
/*
createCollectionIfNotExists("measurements", {
    timeseries: {
        timeField: "ts",
        metaField: "meta",
        granularity: "seconds"  // seconds, minutes, hours
    }
});
*/

// Example: Capped collection for events/logs (if needed)
/*
createCollectionIfNotExists("events", {
    capped: true,
    size: 100000000,  // 100MB
    max: 100000       // max documents
});
*/

// ADD YOUR COLLECTIONS HERE
// createCollectionIfNotExists("your_collection");

// ============================================
// Create Indexes
// ============================================

print("\n--- Creating Indexes ---");

// Example: Unique index
createIndexSafely("sites", { siteCode: 1 }, { unique: true });

// Example: Compound index
createIndexSafely("sites", { siteType: 1, createdAt: -1 });

// Example: Text index for search
// createIndexSafely("products", { name: "text", description: "text" });

// Example: 2dsphere index for geospatial queries
// createIndexSafely("sites", { location: "2dsphere" });

// ADD YOUR INDEXES HERE
// createIndexSafely("collection", { field: 1 }, { options });

// ============================================
// Schema Validation (Optional)
// ============================================

print("\n--- Applying Schema Validators ---");

// Example: JSON Schema validator
/*
db.runCommand({
    collMod: "sites",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["siteCode", "siteType", "name"],
            properties: {
                siteCode: {
                    bsonType: "string",
                    description: "Unique site identifier",
                    pattern: "^[A-Z0-9_]+$"
                },
                siteType: {
                    enum: ["type1", "type2", "type3"],
                    description: "Site category"
                },
                name: {
                    bsonType: "string",
                    minLength: 1,
                    maxLength: 100
                },
                createdAt: {
                    bsonType: "date"
                },
                location: {
                    bsonType: "object",
                    required: ["type", "coordinates"],
                    properties: {
                        type: { enum: ["Point"] },
                        coordinates: {
                            bsonType: "array",
                            minItems: 2,
                            maxItems: 2,
                            items: { bsonType: "number" }
                        }
                    }
                }
            }
        }
    },
    validationLevel: "moderate",  // strict, moderate, off
    validationAction: "error"     // error, warn
});
print("✓ Applied validator to sites collection");
*/

// ADD YOUR VALIDATORS HERE (if needed)

// ============================================
// Summary
// ============================================

print("\n--- Setup Summary ---");
print(`Database: ${DATABASE_NAME}`);
print(`Collections: ${db.getCollectionNames().join(", ")}`);

// Show collection stats
db.getCollectionNames().forEach(collName => {
    const stats = db[collName].stats();
    const indexCount = db[collName].getIndexes().length;
    print(`  ${collName}: ${stats.count} documents, ${indexCount} indexes`);
});

print("\n✓ Setup complete!");
print("\nNext steps:");
print("1. Run: python 01_seed_project.py");
print("2. Run: python 02_simulate_project.py (if applicable)");
print("3. Run: mongosh 03_queries_exam.js");