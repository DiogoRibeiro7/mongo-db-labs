"""
Quick fix script to ensure all numeric values are floats in the database.
This is a temporary workaround for type validation issues.
"""

from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['agrimonitor_db']

print("Fixing numeric types in database...")

# Fix sensors collection - convert range min/max to floats
sensors = db.sensors.find({})
for sensor in sensors:
    if 'specifications' in sensor and 'range' in sensor['specifications']:
        updates = {}
        if 'min' in sensor['specifications']['range']:
            updates['specifications.range.min'] = float(sensor['specifications']['range']['min'])
        if 'max' in sensor['specifications']['range']:
            updates['specifications.range.max'] = float(sensor['specifications']['range']['max'])

        if updates:
            db.sensors.update_one(
                {'_id': sensor['_id']},
                {'$set': updates}
            )

print("✓ Fixed sensors collection")

# Fix risk_assessments collection - convert scores and contributions to floats
assessments = db.risk_assessments.find({})
for assessment in assessments:
    updates = {}

    # Fix main risk score
    if 'riskScore' in assessment:
        updates['riskScore'] = float(assessment['riskScore'])

    # Fix factor contributions
    if 'factors' in assessment:
        for factor_name in ['leafWetness', 'temperature', 'humidity', 'rainfall', 'trapCount']:
            if factor_name in assessment['factors']:
                factor = assessment['factors'][factor_name]
                if 'contribution' in factor:
                    updates[f'factors.{factor_name}.contribution'] = float(factor['contribution'])
                if 'value' in factor:
                    updates[f'factors.{factor_name}.value'] = float(factor['value'])

    if updates:
        db.risk_assessments.update_one(
            {'_id': assessment['_id']},
            {'$set': updates}
        )

print("✓ Fixed risk_assessments collection")

print("\nType fixing complete!")
print("You can now run: python 02_simulate_conditions.py")