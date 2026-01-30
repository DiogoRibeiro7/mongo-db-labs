// MongoDB initialization script
// Creates standard databases and users for all labs

// Switch to admin database
db = db.getSiblingDB('admin');

// Create lab user with appropriate permissions
db.createUser({
    user: 'labuser',
    pwd: 'labpassword',
    roles: [
        { role: 'readWrite', db: 'sensor_data' },
        { role: 'readWrite', db: 'timeseries_db' },
        { role: 'readWrite', db: 'iot_flood_db' },
        { role: 'readWrite', db: 'lorawan_db' },
        { role: 'readWrite', db: 'mls_flood_db' },
        { role: 'readWrite', db: 'smart_farming_db' },
        { role: 'readWrite', db: 'test_db' },
        { role: 'dbAdmin', db: 'sensor_data' },
        { role: 'dbAdmin', db: 'timeseries_db' },
        { role: 'dbAdmin', db: 'iot_flood_db' },
        { role: 'dbAdmin', db: 'lorawan_db' },
        { role: 'dbAdmin', db: 'mls_flood_db' },
        { role: 'dbAdmin', db: 'smart_farming_db' },
        { role: 'dbAdmin', db: 'test_db' }
    ]
});

print('Lab user created successfully');

// Create databases with initial collections
const databases = [
    { name: 'sensor_data', collections: ['metadata'] },
    { name: 'timeseries_db', collections: ['metadata'] },
    { name: 'iot_flood_db', collections: ['metadata'] },
    { name: 'lorawan_db', collections: ['metadata'] },
    { name: 'mls_flood_db', collections: ['metadata'] },
    { name: 'smart_farming_db', collections: ['metadata'] },
    { name: 'test_db', collections: ['test_collection'] }
];

databases.forEach(dbConfig => {
    db = db.getSiblingDB(dbConfig.name);

    // Create initial collections
    dbConfig.collections.forEach(collName => {
        db.createCollection(collName);
        print(`Created collection ${dbConfig.name}.${collName}`);
    });

    // Add metadata document
    db.metadata.insertOne({
        database: dbConfig.name,
        created: new Date(),
        version: '1.0.0',
        purpose: 'MongoDB Labs - Teaching Database',
        initialized_by: 'docker-compose'
    });
});

print('All databases initialized successfully');