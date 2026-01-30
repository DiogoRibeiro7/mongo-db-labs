# Docker Setup for MongoDB Labs

## Overview

This repository uses a **standardized Docker setup** providing a single MongoDB instance shared across all labs.

## Quick Start

```bash
# 1. Start MongoDB
docker-compose up -d

# 2. Verify readiness
python scripts/wait_for_mongo.py --docker

# 3. Run labs
python scripts/lab.py all iot_flood_demo --docker

# 4. Stop when done
docker-compose down
```

## Architecture

```
Root docker-compose.yml
├── MongoDB 7.0 (port 27017)
├── Persistent named volumes
├── Health checks
├── Auto-initialization
└── Optional MongoDB Express (port 8081)
```

## Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Root MongoDB service definition |
| `scripts/wait_for_mongo.py` | Ensures MongoDB readiness |
| `scripts/mongo-init/*.js` | Database initialization scripts |
| `docker-compose.override.yml.example` | Template for local customization |

## Connection Details

### Default Credentials

| User | Password | Purpose |
|------|----------|---------|
| admin | adminpassword | Admin access |
| labuser | labpassword | Lab execution |

### Connection Strings

```bash
# For labs (with auth)
mongodb://labuser:labpassword@localhost:27017/

# For admin tasks
mongodb://admin:adminpassword@localhost:27017/admin

# MongoDB Compass
mongodb://admin:adminpassword@localhost:27017/
```

## Lab Runner Integration

The lab runner (`scripts/lab.py`) now supports Docker:

```bash
# Auto-start Docker if needed
python scripts/lab.py all <lab> --docker

# List labs (no MongoDB needed)
python scripts/lab.py list

# Validate lab structure
python scripts/lab.py validate <lab>
```

## MongoDB Express GUI

Optional web interface for MongoDB:

```bash
# Start with GUI
docker-compose --profile with-gui up -d

# Access at
http://localhost:8081
# Login: admin / admin123
```

## Customization

Create `docker-compose.override.yml` for local settings:

```yaml
version: '3.8'

services:
  mongodb:
    ports:
      - "27018:27017"  # Different port
    environment:
      CUSTOM_VAR: value
```

## Volumes

Data persists in named Docker volumes:

- `mongodb-labs-data` - Database files
- `mongodb-labs-config` - Configuration

```bash
# List volumes
docker volume ls | grep mongodb-labs

# Remove volumes (deletes all data!)
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

```bash
# Option 1: Stop local MongoDB
net stop MongoDB          # Windows
sudo systemctl stop mongod # Linux

# Option 2: Use different port
# Create docker-compose.override.yml with port 27018
```

### Container Not Starting

```bash
# Check logs
docker logs mongodb-labs

# Restart
docker-compose restart mongodb

# Full reset
docker-compose down -v
docker-compose up -d
```

### Authentication Issues

```bash
# Use correct credentials
export MONGO_URI=mongodb://labuser:labpassword@localhost:27017/
python scripts/lab.py all <lab>
```

## Testing Setup

Run the test script to verify everything works:

```bash
python test_docker_setup.py
```

## Benefits

✅ **No MongoDB installation required** - Docker handles everything
✅ **Consistent environment** - Same MongoDB 7.0 for all users
✅ **Shared instance** - Single MongoDB for all labs (no duplication)
✅ **Persistent data** - Named volumes preserve data between sessions
✅ **Health checks** - Automatic readiness detection
✅ **Easy cleanup** - Simple commands to reset everything

## Commands Reference

```bash
# Start MongoDB
docker-compose up -d

# Stop (preserve data)
docker-compose stop

# Stop and remove containers
docker-compose down

# Complete cleanup
docker-compose down -v

# View logs
docker logs mongodb-labs -f

# Check status
docker ps

# Execute mongosh in container
docker exec -it mongodb-labs mongosh -u admin -p adminpassword
```