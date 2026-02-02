# MongoDB Labs Test Suite

Lightweight tests to ensure lab functionality and catch regressions.

## Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Start MongoDB
docker-compose up -d

# Run fast tests
pytest tests/ -m "not slow"

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=labs --cov=scripts
```

## Test Structure

```
tests/
├── __init__.py              # Test package marker
├── conftest.py              # Pytest fixtures and configuration
├── test_infrastructure.py   # Basic sanity tests
├── test_lab_setup.py        # Test database setup scripts
├── test_lab_seed.py         # Test data seeding
└── test_lab_simulation.py   # Test time-series generation
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Fast, no external dependencies
- Test pure functions and logic
- Run in < 1 second each

### Integration Tests (`@pytest.mark.integration`)
- Require MongoDB connection
- Test database operations
- Test script execution

### Slow Tests (`@pytest.mark.slow`)
- Full simulations
- Extended time ranges
- Excluded by default

## Running Tests

### Command Line

```bash
# Run specific test file
pytest tests/test_lab_setup.py

# Run specific test
pytest tests/test_lab_setup.py::TestLabSetup::test_iot_flood_setup_creates_collections

# Run tests matching pattern
pytest tests/ -k "flood"

# Run specific marker
pytest tests/ -m "unit"
pytest tests/ -m "integration and not slow"
```

### Using Make

```bash
make test           # Fast tests only
make test-all       # All tests
make test-coverage  # With coverage report
make test-lab LAB=iot_flood_demo  # Test specific lab
```

### Using Test Runner

```bash
python scripts/test_runner.py              # Fast tests
python scripts/test_runner.py --slow       # All tests
python scripts/test_runner.py --lab iot    # Specific lab
python scripts/test_runner.py --coverage   # With coverage
```

## Writing Tests

### Basic Test

```python
def test_something():
    """Test description."""
    assert 1 + 1 == 2
```

### Using Fixtures

```python
def test_with_mongodb(mongo_client):
    """Test that needs MongoDB."""
    db = mongo_client.test_db
    result = db.test.insert_one({"test": True})
    assert result.inserted_id is not None
```

### Testing Lab Scripts

```python
def test_lab_setup(lab_runner):
    """Test lab setup script."""
    lab_runner.run_mongosh_script("iot_flood_demo", "00_setup_mongodb.js")
    # Verify results...
```

## CI/CD Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Manual workflow dispatch

GitHub Actions workflow:
- Starts MongoDB service container
- Installs dependencies
- Runs tests with timeout
- Reports results

## Test Coverage Goals

- **Setup scripts**: Collections created, indexes applied
- **Seed scripts**: Minimum document counts, valid relationships
- **Simulations**: Time-series data, value ranges
- **Schema validation**: Validation rules enforced

## Troubleshooting

### MongoDB Not Available

```bash
# Start MongoDB
docker-compose up -d

# Or use different URI
MONGO_URI=mongodb://myserver:27017 pytest tests/
```

### Tests Timing Out

```bash
# Increase timeout
pytest tests/ --timeout=120

# Or run without timeout
pytest tests/ --timeout=0
```

### Slow Tests

```bash
# Skip slow tests
pytest tests/ -m "not slow"

# Run only slow tests
pytest tests/ -m "slow"
```

## Best Practices

1. **Keep tests fast** - Most tests should run in < 1 second
2. **Use markers** - Categorize tests appropriately
3. **Clean up** - Drop test databases after tests
4. **Deterministic** - Use seeds for reproducible results
5. **Independent** - Tests shouldn't depend on each other
6. **Descriptive** - Clear test names and assertions

## Continuous Improvement

When adding new labs:
1. Add test cases to verify setup/seed/simulation
2. Update `sample_labs` fixture if needed
3. Ensure CI passes before merging
4. Keep test runtime under 5 minutes