# Contributing to MongoDB Teaching Labs

Thank you for your interest in contributing to the MongoDB Teaching Labs repository! This document provides guidelines and instructions for contributing new labs, improving existing ones, and maintaining consistency across the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Creating a New Lab](#creating-a-new-lab)
- [Lab Requirements](#lab-requirements)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project is intended for educational purposes. Contributors should:
- Be respectful and inclusive
- Focus on educational value
- Provide clear, well-documented examples
- Help others learn MongoDB concepts effectively

## How to Contribute

### Types of Contributions

1. **New Labs** - Add complete teaching labs with novel scenarios
2. **Lab Improvements** - Enhance existing labs with better examples or exercises
3. **Bug Fixes** - Fix errors in scripts or documentation
4. **Documentation** - Improve explanations, add diagrams, or clarify concepts
5. **Tools & Scripts** - Add helper utilities or improve existing ones

### Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a feature branch: `git checkout -b lab/your-lab-name`
4. Make your changes
5. Test thoroughly
6. Commit with clear messages
7. Push to your fork
8. Create a pull request

## Creating a New Lab

### Step 1: Use the Template

```bash
python scripts/new-lab.py your-lab-slug \
  --name "Your Lab Name" \
  --domain "Domain Area" \
  --author "Your Name"
```

### Step 2: Design Your Data Model

Before coding, document your data model:
- What collections will you use?
- What are the relationships?
- What indexes are needed?
- What query patterns will students practice?

### Step 3: Implement Lab Components

Follow the standard 4-stage structure:

1. **00_setup_mongodb.js** - Database initialization
   - Create collections with appropriate options
   - Define indexes for performance
   - Add schema validators (optional but recommended)
   - Make it idempotent (safe to re-run)

2. **01_seed_*.py** - Master data seeding
   - Insert reference/configuration data
   - Support `--clean` flag for reset
   - Support `--seed` for reproducibility
   - Include realistic sample data

3. **02_simulate_*.py** - Time-series generation (optional)
   - Generate realistic patterns
   - Support `--hours` parameter
   - Include random events if applicable
   - Batch inserts for performance

4. **03_queries_exam.js** - Query exercises
   - Start simple, increase complexity
   - Cover various MongoDB features
   - Include reference solutions
   - Add performance analysis queries

### Step 4: Document Everything

- **DATABASE.md** - Document EVERY field
- **README.md** - Clear learning objectives and instructions
- Use comments to explain "why" not just "what"

## Lab Requirements

### Mandatory Requirements

- [ ] All 4 core scripts (00-03) must be present and functional
- [ ] DATABASE.md must document every field with examples
- [ ] README.md must include learning objectives
- [ ] Scripts must handle errors gracefully
- [ ] Data model must be educationally valuable
- [ ] Query exercises must have solutions

### Quality Criteria

- [ ] **Educational Value**: Does it teach important MongoDB concepts?
- [ ] **Realism**: Is the scenario believable and practical?
- [ ] **Completeness**: Are all aspects properly documented?
- [ ] **Reproducibility**: Can results be reproduced with seeds?
- [ ] **Performance**: Does it work with reasonable data volumes?
- [ ] **Clarity**: Can students understand without instructor help?

### Recommended Features

- Docker Compose configuration for easy setup
- Multiple difficulty levels in queries
- Performance optimization examples
- Index strategy demonstrations
- Aggregation pipeline examples

## Code Standards

### JavaScript (MongoDB Shell)

```javascript
// Use descriptive function names
function createCollectionIfNotExists(name, options = {}) {
    // Implementation
}

// Always check for existing data
if (db.collection.countDocuments({}) > 0) {
    print("Collection already has data");
    return;
}

// Make operations idempotent
try {
    db.collection.createIndex({ field: 1 });
} catch (e) {
    if (e.codeName !== 'IndexOptionsConflict') throw e;
}
```

### Python

```python
# Use type hints
def seed_data(db: pymongo.database.Database, clean: bool = False) -> Dict[str, Any]:
    """
    Seed master data with clear documentation.

    Args:
        db: MongoDB database instance
        clean: Whether to clean existing data

    Returns:
        Dictionary of inserted document IDs
    """
    # Implementation
```

### Naming Conventions

- **Database names**: `snake_case` (e.g., `ecommerce_orders`)
- **Collection names**: `camelCase` (e.g., `orderItems`)
- **Field names**: `camelCase` (e.g., `createdAt`)
- **Script names**: Follow the numbered pattern (00-03)

### Data Conventions

- Store all timestamps as UTC `Date` objects
- Include units in metric names (e.g., `distanceKm`, `durationMs`)
- Use consistent status values across collections
- Implement soft deletes with `deletedAt` when appropriate

## Testing Guidelines

### Before Submitting

1. **Clean Test**
   ```bash
   python scripts/reset-db.py your-lab --drop-database
   python scripts/run-lab.py your-lab
   ```

2. **Idempotency Test**
   ```bash
   # Run setup twice - should not fail
   mongosh labs/your-lab/00_setup_mongodb.js
   mongosh labs/your-lab/00_setup_mongodb.js
   ```

3. **Seed Reproducibility**
   ```bash
   python labs/your-lab/01_seed_*.py --clean --seed 42
   # Document count should be consistent
   ```

4. **Query Validation**
   ```bash
   # All queries should return results
   mongosh labs/your-lab/03_queries_exam.js
   ```

5. **Docker Test** (if applicable)
   ```bash
   cd labs/your-lab
   docker compose up -d
   # Run full sequence
   docker compose down -v
   ```

### Performance Testing

For labs with large datasets:
- Test with 1 hour of simulated data
- Test with 24 hours of simulated data
- Test with 7 days if applicable
- Ensure queries complete in reasonable time

## Documentation Standards

### DATABASE.md Structure

```markdown
# Data Dictionary for [Lab Name]

## Database: `database_name`

## Collections Overview
[Table with all collections]

## Collection: `collectionName`

**Purpose**: [Clear description]

**Indexes**:
- List all indexes

**Schema**:
[Table with field details]

**Example Document**:
```json
{
  // Full example
}
```
```

### README.md Structure

```markdown
# [Lab Name]

[Brief description]

## Learning Objectives
- Objective 1
- Objective 2

## Prerequisites
- MongoDB version
- Other requirements

## Quick Start
[Step-by-step instructions]

## Exercises
[What students will practice]
```

### Code Comments

```javascript
// GOOD: Explains why
// Use compound index for query performance on common filter pattern
db.orders.createIndex({ userId: 1, createdAt: -1 });

// BAD: States the obvious
// Create an index
db.orders.createIndex({ userId: 1 });
```

## Pull Request Process

### PR Checklist

- [ ] Lab follows standard structure
- [ ] All scripts tested and working
- [ ] Documentation is complete
- [ ] Added lab to main README table
- [ ] No sensitive data included
- [ ] Passes CI checks (when available)

### PR Title Format

```
[Type] Brief description

Types:
- feat: New lab
- fix: Bug fix
- docs: Documentation only
- refactor: Code improvement
- test: Test additions
```

Examples:
- `feat: Add e-commerce orders lab`
- `fix: Correct index creation in IoT lab`
- `docs: Improve aggregation explanations`

### PR Description Template

```markdown
## Summary
Brief description of changes

## Lab Details (for new labs)
- **Name**: Human-readable name
- **Slug**: Directory name
- **Domain**: Problem domain
- **Difficulty**: Beginner/Intermediate/Advanced
- **Key Concepts**: What it teaches

## Testing
- [ ] Clean installation tested
- [ ] All scripts run without errors
- [ ] Queries produce expected results
- [ ] Documentation reviewed

## Screenshots (if applicable)
[Query results, schema diagrams, etc.]
```

## Issue Reporting

### Bug Reports

Include:
1. Lab name and script
2. Error message (full traceback)
3. MongoDB version
4. Operating system
5. Steps to reproduce

### Feature Requests

Include:
1. Problem you're trying to solve
2. Proposed solution
3. Educational value
4. Alternative approaches considered

### Good Issue Titles

- ✅ `Bug: Seed script fails with duplicate key error in ecommerce lab`
- ✅ `Feature: Add transaction examples to retail lab`
- ❌ `Script doesn't work`
- ❌ `Add more stuff`

## Review Process

Pull requests will be reviewed for:

1. **Technical Correctness** - Do scripts work as intended?
2. **Educational Value** - Does it teach MongoDB concepts well?
3. **Code Quality** - Is code clean and maintainable?
4. **Documentation** - Is everything clearly explained?
5. **Consistency** - Does it follow repository standards?

### Review Timeline

- Simple fixes: 1-3 days
- New labs: 1 week
- Major changes: 2 weeks

## Questions?

- Open an issue for clarification
- Check existing labs for examples
- Review the [Repository Structure Guide](STRUCTURE.md)

## Recognition

Contributors will be:
- Listed in lab documentation
- Credited in commit history
- Acknowledged in release notes

Thank you for helping make MongoDB education better!

---

**Last Updated**: January 2024
**Maintainer Contact**: [Add contact info]