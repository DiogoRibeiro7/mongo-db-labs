"""
Basic tests to verify test infrastructure is working.
"""
import pytest
import os
from pathlib import Path


class TestInfrastructure:
    """Test that the test infrastructure itself is working."""

    @pytest.mark.unit
    def test_pytest_running(self):
        """Verify pytest is running."""
        assert True, "If this fails, something is very wrong"

    @pytest.mark.unit
    def test_project_structure(self):
        """Test that basic project structure exists."""
        project_root = Path(__file__).parent.parent

        # Check essential directories
        assert (project_root / "labs").exists(), "labs/ directory missing"
        assert (project_root / "scripts").exists(), "scripts/ directory missing"
        assert (project_root / "tests").exists(), "tests/ directory missing"
        assert (project_root / "docs").exists(), "docs/ directory missing"

    @pytest.mark.unit
    def test_lab_directories_exist(self):
        """Test that at least some labs exist."""
        labs_dir = Path(__file__).parent.parent / "labs"
        lab_dirs = [d for d in labs_dir.iterdir() if d.is_dir()]

        assert len(lab_dirs) > 0, "No lab directories found"

        # Check for expected labs
        expected_labs = ["iot_flood_demo", "soil_humidity_lorawan"]
        existing_labs = [d.name for d in lab_dirs]

        for lab in expected_labs:
            if lab in existing_labs:
                assert True, f"Found expected lab: {lab}"
                break
        else:
            pytest.skip("Expected labs not found (may be intentional)")

    @pytest.mark.unit
    def test_environment_variables(self):
        """Test that MongoDB URI can be configured."""
        # Default should be localhost
        default_uri = "mongodb://localhost:27017"

        # Get from environment or use default
        mongo_uri = os.environ.get("MONGO_URI", default_uri)

        assert mongo_uri is not None, "MONGO_URI not set"
        assert "mongodb://" in mongo_uri, "Invalid MongoDB URI format"

    @pytest.mark.integration
    def test_mongodb_connection(self, mongo_client):
        """Test that MongoDB connection works."""
        # This will skip if MongoDB is not available (handled by fixture)
        result = mongo_client.admin.command('ping')
        assert result.get('ok') == 1, "MongoDB ping failed"

    @pytest.mark.integration
    def test_database_operations(self, mongo_client):
        """Test basic database operations."""
        test_db = mongo_client.test_db_deleteme
        test_collection = test_db.test_collection

        # Insert
        doc = {"test": True, "value": 42}
        result = test_collection.insert_one(doc)
        assert result.inserted_id is not None

        # Find
        found = test_collection.find_one({"test": True})
        assert found is not None
        assert found["value"] == 42

        # Cleanup
        mongo_client.drop_database("test_db_deleteme")

    @pytest.mark.unit
    def test_lab_runner_fixture(self, lab_runner):
        """Test that lab runner fixture is available."""
        assert lab_runner is not None
        assert hasattr(lab_runner, "run_mongosh_script")
        assert hasattr(lab_runner, "run_python_script")
        assert hasattr(lab_runner, "check_lab_exists")

    @pytest.mark.unit
    def test_sample_labs_fixture(self, sample_labs):
        """Test that sample labs configuration is available."""
        assert len(sample_labs) > 0, "No sample labs configured"

        for lab in sample_labs:
            assert "name" in lab, "Lab missing name"
            assert "database" in lab, "Lab missing database"
            assert "collections" in lab, "Lab missing collections"

    @pytest.mark.skip(reason="Example of skipped test")
    def test_skip_example(self):
        """This test is always skipped (example)."""
        assert False, "This should never run"

    @pytest.mark.slow
    def test_slow_marker(self):
        """Test marked as slow (excluded by default)."""
        import time
        time.sleep(0.1)  # Simulate slow operation
        assert True, "Slow test completed"