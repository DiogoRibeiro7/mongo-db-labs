"""
Test lab seed scripts produce expected data.
"""
import pytest
import json


class TestLabSeed:
    """Test data seeding for labs."""

    @pytest.mark.integration
    def test_iot_flood_seed_creates_data(self, mongo_client, lab_runner):
        """Test that seed script creates required documents."""
        lab_name = "iot_flood_demo"
        db_name = "iot_flood_demo"

        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # Setup and seed
        mongo_client.drop_database(db_name)
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")
        lab_runner.run_python_script(lab_name, "01_seed_flood_project.py")

        db = mongo_client[db_name]

        # Check minimum document counts
        min_counts = {
            "sites": 3,
            "sensors": 5,
            "ratingCurves": 2,
            "samplingPolicies": 3,
            "policyState": 3
        }

        for collection, min_count in min_counts.items():
            count = db[collection].count_documents({})
            assert count >= min_count, \
                f"{collection} has {count} docs, expected >= {min_count}"

    @pytest.mark.integration
    def test_seed_data_relationships(self, mongo_client, lab_runner):
        """Test that seeded data has valid relationships."""
        lab_name = "iot_flood_demo"
        db_name = "iot_flood_demo"

        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # Setup and seed
        mongo_client.drop_database(db_name)
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")
        lab_runner.run_python_script(lab_name, "01_seed_flood_project.py")

        db = mongo_client[db_name]

        # Get all site IDs
        site_ids = [doc["_id"] for doc in db.sites.find({}, {"_id": 1})]
        assert len(site_ids) > 0, "No sites created"

        # Check sensors reference valid sites
        sensors = list(db.sensors.find({}))
        for sensor in sensors:
            assert "siteId" in sensor, "Sensor missing siteId"
            assert sensor["siteId"] in site_ids, \
                f"Sensor references invalid site: {sensor['siteId']}"

        # Check policies reference valid sites
        policies = list(db.samplingPolicies.find({}))
        for policy in policies:
            assert "siteId" in policy, "Policy missing siteId"
            assert policy["siteId"] in site_ids, \
                f"Policy references invalid site: {policy['siteId']}"

    @pytest.mark.integration
    def test_seed_data_validity(self, mongo_client, lab_runner):
        """Test that seeded data passes schema validation."""
        lab_name = "iot_flood_demo"
        db_name = "iot_flood_demo"

        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # Setup and seed
        mongo_client.drop_database(db_name)
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")
        lab_runner.run_python_script(lab_name, "01_seed_flood_project.py")

        db = mongo_client[db_name]

        # Check sites have required fields
        sites = list(db.sites.find({}))
        for site in sites:
            assert "siteCode" in site, "Site missing siteCode"
            assert "siteType" in site, "Site missing siteType"
            assert "name" in site, "Site missing name"
            assert "geo" in site, "Site missing geo"
            assert site["siteType"] in ["river", "stormwater", "rain_gauge"]

            # Check GeoJSON structure
            geo = site["geo"]
            assert geo.get("type") == "Point", "Invalid GeoJSON type"
            assert "coordinates" in geo, "Missing coordinates"
            coords = geo["coordinates"]
            assert len(coords) == 2, "Invalid coordinates"
            assert -180 <= coords[0] <= 180, "Invalid longitude"
            assert -90 <= coords[1] <= 90, "Invalid latitude"

    @pytest.mark.integration
    def test_seed_deterministic_with_seed(self, mongo_client, lab_runner):
        """Test that seed script produces deterministic data with --seed."""
        lab_name = "iot_flood_demo"
        db_name = "iot_flood_demo"

        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # First run with seed
        mongo_client.drop_database(db_name)
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")
        lab_runner.run_python_script(lab_name, "01_seed_flood_project.py", ["--seed", "42"])

        db = mongo_client[db_name]
        sites1 = list(db.sites.find({}, {"_id": 0}).sort("siteCode", 1))

        # Second run with same seed
        mongo_client.drop_database(db_name)
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")
        lab_runner.run_python_script(lab_name, "01_seed_flood_project.py", ["--seed", "42"])

        sites2 = list(db.sites.find({}, {"_id": 0}).sort("siteCode", 1))

        # Should produce same data (except timestamps)
        assert len(sites1) == len(sites2), "Different number of sites"

        for s1, s2 in zip(sites1, sites2):
            # Compare essential fields
            assert s1["siteCode"] == s2["siteCode"]
            assert s1["siteType"] == s2["siteType"]
            assert s1["geo"] == s2["geo"]

    @pytest.mark.integration
    @pytest.mark.parametrize("lab_name,db_name,min_sites", [
        ("iot_flood_demo", "iot_flood_demo", 3),
        ("soil_humidity_lorawan", "lorawan_db", 2),
    ])
    def test_multiple_labs_seed(self, mongo_client, lab_runner, lab_name, db_name, min_sites):
        """Test seeding for multiple labs."""
        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # Setup and seed
        mongo_client.drop_database(db_name)
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")

        # Find the seed script (might have different names)
        import os
        from pathlib import Path
        lab_dir = Path(lab_runner.labs_dir) / lab_name
        seed_scripts = list(lab_dir.glob("01_seed*.py"))

        if not seed_scripts:
            pytest.skip(f"No seed script found for {lab_name}")

        lab_runner.run_python_script(lab_name, seed_scripts[0].name)

        # Check data was created
        db = mongo_client[db_name]
        site_count = db.sites.count_documents({})
        assert site_count >= min_sites, \
            f"{lab_name} created {site_count} sites, expected >= {min_sites}"

    def test_seed_handles_clean_flag(self, mongo_client, lab_runner):
        """Test that --clean flag removes existing data."""
        lab_name = "iot_flood_demo"
        db_name = "iot_flood_demo"

        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # Setup and seed twice
        mongo_client.drop_database(db_name)
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")

        # First seed
        lab_runner.run_python_script(lab_name, "01_seed_flood_project.py")
        db = mongo_client[db_name]
        count1 = db.sites.count_documents({})

        # Second seed with --clean
        lab_runner.run_python_script(lab_name, "01_seed_flood_project.py", ["--clean"])
        count2 = db.sites.count_documents({})

        # Should have same count (not doubled)
        assert count2 == count1, "--clean flag didn't prevent duplication"