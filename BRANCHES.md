# Branch Configuration Guide

This document describes the parallel development branches and their port configurations.

## Overview

Three separate branches have been created from the main branch to allow parallel development and testing without port conflicts. Each branch is configured to run on different ports.

## Branch Details

### Main Branch
- **Branch Name**: `main`
- **Frontend Port**: 3000
- **Backend Port**: 8000
- **Purpose**: Production-ready code
- **Startup**: `npm run dev` (default ports)

### SOL1 Branch
- **Branch Name**: `sol1`
- **Frontend Port**: 3001
- **Backend Port**: 8001
- **Frontend URL**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **WebSocket URL**: ws://localhost:8001/api/v1/ws/coindcx
- **Startup**: `./start-sol1.sh`

### SOL2 Branch
- **Branch Name**: `sol2`
- **Frontend Port**: 3002
- **Backend Port**: 8002
- **Frontend URL**: http://localhost:3002
- **Backend API**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs
- **WebSocket URL**: ws://localhost:8002/api/v1/ws/coindcx
- **Startup**: `./start-sol2.sh`

### SOL3 Branch
- **Branch Name**: `sol3`
- **Frontend Port**: 3003
- **Backend Port**: 8003
- **Frontend URL**: http://localhost:3003
- **Backend API**: http://localhost:8003
- **API Docs**: http://localhost:8003/docs
- **WebSocket URL**: ws://localhost:8003/api/v1/ws/coindcx
- **Startup**: `./start-sol3.sh`

## Quick Start

### Running a Specific Branch

```bash
# Switch to the branch
git checkout sol1  # or sol2, sol3

# Run the startup script
./start-sol1.sh    # or start-sol2.sh, start-sol3.sh
```

### Running Multiple Branches Simultaneously

You can run all three branches at the same time for parallel testing:

```bash
# Terminal 1
git checkout sol1
./start-sol1.sh

# Terminal 2
git checkout sol2
./start-sol2.sh

# Terminal 3
git checkout sol3
./start-sol3.sh
```

Now you can access:
- SOL1: http://localhost:3001
- SOL2: http://localhost:3002
- SOL3: http://localhost:3003

## Environment Configuration

Each branch has its own environment configuration files:

### Backend Environment Files
- `backend/.env.sol1` - SOL1 backend configuration (port 8001)
- `backend/.env.sol2` - SOL2 backend configuration (port 8002)
- `backend/.env.sol3` - SOL3 backend configuration (port 8003)

**Note**: These files are in `.gitignore` and must be created locally using the startup scripts.

### Frontend Environment Files
- `.env.local.sol1` - SOL1 frontend configuration (API URL: http://localhost:8001)
- `.env.local.sol2` - SOL2 frontend configuration (API URL: http://localhost:8002)
- `.env.local.sol3` - SOL3 frontend configuration (API URL: http://localhost:8003)

**Note**: These files are in `.gitignore` and must be created locally using the startup scripts.

## Startup Scripts

Each branch includes a startup script that:
1. Kills any processes on the branch's assigned ports
2. Copies the correct environment files
3. Starts the backend server on the assigned port
4. Starts the frontend server on the assigned port
5. Displays the running URLs

### Script Files
- `start-sol1.sh` - Starts SOL1 branch
- `start-sol2.sh` - Starts SOL2 branch
- `start-sol3.sh` - Starts SOL3 branch

### How Startup Scripts Work

```bash
#!/bin/bash
# Example from start-sol1.sh

# 1. Clean up ports
lsof -ti:3001,8001 | xargs kill -9 2>/dev/null || true

# 2. Copy environment files
cp .env.local.sol1 .env.local
cp backend/.env.sol1 backend/.env

# 3. Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
cd ..

# 4. Start frontend
PORT=3001 npm run dev:frontend &
```

## Manual Configuration (Without Scripts)

If you prefer to configure manually:

### Backend

1. Create `backend/.env` with the branch's port:
```env
PORT=8001  # or 8002, 8003
BACKEND_CORS_ORIGINS=["http://localhost:3001", "http://127.0.0.1:3001"]
```

2. Start backend:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend

1. Create `.env.local` with the backend URL:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

2. Start frontend:
```bash
PORT=3001 npm run dev:frontend
```

## Port Conflicts

If you encounter port conflicts:

```bash
# Check which process is using a port
lsof -i :3001

# Kill a specific port
lsof -ti:3001 | xargs kill -9

# Kill multiple ports
lsof -ti:3001,3002,3003,8001,8002,8003 | xargs kill -9
```

## Database and Redis

All branches share the same:
- **PostgreSQL Database**: `scalper_bot` on port 5432
- **Redis Instance**: localhost:6379/0

This means data changes in one branch will be visible in other branches.

## Workflow Tips

### Testing Different Solutions

1. Create your fix/feature in SOL1
2. If it doesn't work, switch to SOL2 and try a different approach
3. Compare results across branches
4. Merge the working solution back to main

### Parallel Development

1. Use SOL1 for backend changes
2. Use SOL2 for frontend changes
3. Use SOL3 for integration testing

### Quick Switching

```bash
# Save work on current branch
git add .
git commit -m "WIP: description"

# Switch to another branch
git checkout sol2

# Start the new branch
./start-sol2.sh
```

## Merging Changes Back to Main

When you've finished testing and want to merge:

```bash
# Switch to main
git checkout main

# Merge from solution branch
git merge sol1  # or sol2, sol3

# Resolve conflicts if any
git add .
git commit -m "Merge sol1 into main"

# Push to GitHub
git push origin main
```

## Troubleshooting

### Port Already in Use
```bash
# The startup script should handle this, but if it doesn't:
lsof -ti:3001,8001 | xargs kill -9
```

### Environment Files Missing
```bash
# Run the startup script - it will create them
./start-sol1.sh
```

### Frontend Can't Connect to Backend
```bash
# Check backend is running
curl http://localhost:8001/health

# Check .env.local has correct API URL
cat .env.local
```

### Database Connection Issues
```bash
# All branches use the same database
# Check PostgreSQL is running
pg_isready

# Check connection
psql scalper_bot
```

## Cleaning Up

### Stop All Servers
```bash
# Kill all ports
lsof -ti:3000,3001,3002,3003,8000,8001,8002,8003 | xargs kill -9
```

### Delete Branch (After Merging)
```bash
# Delete local branch
git branch -d sol1

# Delete remote branch
git push origin --delete sol1
```

## Summary

| Branch | Frontend | Backend | Startup Script | Purpose |
|--------|----------|---------|----------------|---------|
| main   | 3000     | 8000    | `npm run dev`  | Production |
| sol1   | 3001     | 8001    | `./start-sol1.sh` | Testing Solution 1 |
| sol2   | 3002     | 8002    | `./start-sol2.sh` | Testing Solution 2 |
| sol3   | 3003     | 8003    | `./start-sol3.sh` | Testing Solution 3 |

## Support

For issues or questions:
- Check this documentation first
- Review startup script output
- Check backend logs
- Verify port availability
- Ensure database and Redis are running
