"""
Test lab setup scripts create expected collections and schemas.
"""
import pytest
from pymongo.errors import OperationFailure


class TestLabSetup:
    """Test database setup for labs."""

    @pytest.mark.integration
    def test_iot_flood_setup_creates_collections(self, mongo_client, lab_runner):
        """Test that IoT flood demo setup creates all required collections."""
        lab_name = "iot_flood_demo"
        db_name = "iot_flood_demo"

        # Skip if lab doesn't exist
        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # Drop database if exists
        mongo_client.drop_database(db_name)

        # Run setup script
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")

        # Check collections were created
        db = mongo_client[db_name]
        collections = db.list_collection_names()

        expected_collections = [
            "sites", "sensors", "measurements", "alerts",
            "ratingCurves", "samplingPolicies", "policyState"
        ]

        for coll_name in expected_collections:
            assert coll_name in collections, f"Collection {coll_name} not created"

    @pytest.mark.integration
    def test_iot_flood_timeseries_collection(self, mongo_client, lab_runner):
        """Test that measurements collection is configured as time-series."""
        lab_name = "iot_flood_demo"
        db_name = "iot_flood_demo"

        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # Drop and recreate
        mongo_client.drop_database(db_name)
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")

        # Check time-series configuration
        db = mongo_client[db_name]
        coll_info = db.command("listCollections", filter={"name": "measurements"})

        collections = list(coll_info["cursor"]["firstBatch"])
        assert len(collections) == 1, "measurements collection not found"

        coll_options = collections[0].get("options", {})
        assert "timeseries" in coll_options, "measurements is not a time-series collection"

        ts_config = coll_options["timeseries"]
        assert ts_config.get("timeField") == "ts", "Wrong timeField"
        assert ts_config.get("metaField") == "meta", "Wrong metaField"

    @pytest.mark.integration
    def test_schema_validation_enabled(self, mongo_client, lab_runner):
        """Test that schema validation is applied to collections."""
        lab_name = "iot_flood_demo"
        db_name = "iot_flood_demo"

        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # Setup database
        mongo_client.drop_database(db_name)
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")

        db = mongo_client[db_name]

        # Test validation on sites collection
        # Try to insert invalid document (missing required field)
        with pytest.raises(OperationFailure) as exc_info:
            db.sites.insert_one({
                "siteCode": "TEST001"
                # Missing required fields like siteType, name, etc.
            })

        assert "Document failed validation" in str(exc_info.value)

    @pytest.mark.integration
    def test_indexes_created(self, mongo_client, lab_runner):
        """Test that appropriate indexes are created."""
        lab_name = "iot_flood_demo"
        db_name = "iot_flood_demo"

        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # Setup database
        mongo_client.drop_database(db_name)
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")

        db = mongo_client[db_name]

        # Check sites indexes
        sites_indexes = db.sites.list_indexes()
        index_keys = [idx["key"] for idx in sites_indexes]

        # Should have index on siteCode
        assert any(
            "siteCode" in keys for keys in index_keys
        ), "Missing index on siteCode"

        # Check unique constraint
        site_code_index = next(
            (idx for idx in sites_indexes if "siteCode" in idx["key"]),
            None
        )
        assert site_code_index is not None, "siteCode index not found"
        assert site_code_index.get("unique") == True, "siteCode index should be unique"

    @pytest.mark.integration
    @pytest.mark.parametrize("lab_config", [
        {
            "name": "iot_flood_demo",
            "database": "iot_flood_demo",
            "collections": ["sites", "sensors", "measurements", "alerts"]
        },
        {
            "name": "soil_humidity_lorawan",
            "database": "lorawan_db",
            "collections": ["sites", "sensors", "measurements"]
        }
    ])
    def test_multiple_labs_setup(self, mongo_client, lab_runner, lab_config):
        """Test setup for multiple labs."""
        if not lab_runner.check_lab_exists(lab_config["name"]):
            pytest.skip(f"Lab {lab_config['name']} not found")

        # Drop and setup
        mongo_client.drop_database(lab_config["database"])
        lab_runner.run_mongosh_script(lab_config["name"], "00_setup_mongodb.js")

        # Verify collections
        db = mongo_client[lab_config["database"]]
        collections = db.list_collection_names()

        for coll in lab_config["collections"]:
            assert coll in collections, f"{coll} not in {lab_config['name']}"

    def test_setup_idempotent(self, mongo_client, lab_runner):
        """Test that setup scripts can be run multiple times safely."""
        lab_name = "iot_flood_demo"
        db_name = "iot_flood_demo"

        if not lab_runner.check_lab_exists(lab_name):
            pytest.skip(f"Lab {lab_name} not found")

        # Drop database
        mongo_client.drop_database(db_name)

        # Run setup twice
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")
        lab_runner.run_mongosh_script(lab_name, "00_setup_mongodb.js")

        # Should still have correct collections
        db = mongo_client[db_name]
        collections = db.list_collection_names()
        assert "sites" in collections
        assert "measurements" in collections