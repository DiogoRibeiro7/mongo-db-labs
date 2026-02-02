"""
Pytest configuration and fixtures for MongoDB Labs testing.
"""
import os
import sys
import pytest
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import subprocess
import time

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# MongoDB connection settings
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
TEST_TIMEOUT = 30  # seconds


@pytest.fixture(scope="session")
def mongo_client():
    """
    Create a MongoDB client for the test session.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        yield client
    except ConnectionFailure as e:
        pytest.skip(f"MongoDB not available at {MONGO_URI}: {e}")
    finally:
        if 'client' in locals():
            client.close()


@pytest.fixture(scope="function")
def clean_database(mongo_client):
    """
    Provide a clean database for each test.
    Drops the database after the test.
    """
    def _get_clean_db(db_name):
        # Drop if exists
        mongo_client.drop_database(db_name)
        return mongo_client[db_name]

    databases_created = []

    def factory(db_name):
        databases_created.append(db_name)
        return _get_clean_db(db_name)

    yield factory

    # Cleanup
    for db_name in databases_created:
        try:
            mongo_client.drop_database(db_name)
        except:
            pass


@pytest.fixture(scope="session")
def lab_runner():
    """
    Helper to run lab scripts.
    """
    class LabRunner:
        def __init__(self):
            self.project_root = PROJECT_ROOT
            self.labs_dir = self.project_root / "labs"

        def run_mongosh_script(self, lab_name, script_name):
            """Run a mongosh script for a lab."""
            script_path = self.labs_dir / lab_name / script_name
            if not script_path.exists():
                pytest.skip(f"Script not found: {script_path}")

            cmd = ["mongosh", MONGO_URI, "--quiet", str(script_path)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TEST_TIMEOUT
            )

            if result.returncode != 0:
                raise RuntimeError(f"mongosh script failed: {result.stderr}")

            return result.stdout

        def run_python_script(self, lab_name, script_name, args=None):
            """Run a Python script for a lab."""
            script_path = self.labs_dir / lab_name / script_name
            if not script_path.exists():
                pytest.skip(f"Script not found: {script_path}")

            cmd = [sys.executable, str(script_path)]
            if args:
                cmd.extend(args)

            # Set environment
            env = os.environ.copy()
            env["MONGO_URI"] = MONGO_URI

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TEST_TIMEOUT,
                cwd=str(self.labs_dir / lab_name),
                env=env
            )

            if result.returncode != 0:
                raise RuntimeError(f"Python script failed: {result.stderr}")

            return result.stdout

        def check_lab_exists(self, lab_name):
            """Check if a lab directory exists."""
            lab_path = self.labs_dir / lab_name
            return lab_path.exists() and lab_path.is_dir()

    return LabRunner()


@pytest.fixture
def sample_labs():
    """
    List of labs to test.
    """
    return [
        {
            "name": "iot_flood_demo",
            "database": "iot_flood_demo",
            "collections": ["sites", "sensors", "measurements", "alerts",
                          "ratingCurves", "samplingPolicies", "policyState"],
            "min_counts": {
                "sites": 3,
                "sensors": 5,
                "ratingCurves": 2,
                "samplingPolicies": 3,
                "policyState": 3
            },
            "time_series": ["measurements"],
            "measurement_fields": ["ts", "meta", "value"],
            "value_ranges": {
                "value": (-100, 1000),
                "batteryPct": (0, 100),
                "signalQuality": (0.0, 1.0)
            }
        },
        {
            "name": "soil_humidity_lorawan",
            "database": "lorawan_db",
            "collections": ["sites", "sensors", "measurements", "alerts",
                          "ratingCurves", "samplingPolicies", "policyState"],
            "min_counts": {
                "sites": 3,
                "sensors": 5,
                "ratingCurves": 2,
                "samplingPolicies": 3
            },
            "time_series": ["measurements"],
            "measurement_fields": ["ts", "meta", "value"],
            "value_ranges": {
                "value": (0, 100),  # Soil moisture percentage
                "batteryPct": (0, 100)
            }
        }
    ]


@pytest.fixture
def quick_simulation_args():
    """
    Arguments for quick simulation runs (1 minute of simulated data).
    """
    return [
        "--hours", "0.017",  # ~1 minute
        "--seed", "42",       # Deterministic
        "--base-step-sec", "60"  # 1-minute intervals
    ]


def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically mark test types based on their names/location.
    """
    for item in items:
        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Mark slow tests
        if "slow" in item.name or "simulate" in item.name:
            item.add_marker(pytest.mark.slow)