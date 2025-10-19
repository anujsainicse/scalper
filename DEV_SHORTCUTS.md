# Development Shortcuts

Quick reference for running the Scalper Bot application.

## 🚀 Quick Start

### Start Everything (Frontend + Backend)
```bash
npm run dev
```

This single command:
- ✅ Automatically kills any processes on ports 3000 & 8000
- ✅ Starts Next.js frontend on http://localhost:3000
- ✅ Starts FastAPI backend on http://localhost:8000

Output will be color-coded:
- `[NEXT]` - Frontend (cyan)
- `[API]` - Backend (magenta)

**Note:** `npm run dev` will automatically clean up stuck processes, so you never have to worry about "port already in use" errors!

## 📋 Individual Commands

### Start Frontend Only
```bash
npm run dev:frontend
```

### Start Backend Only
```bash
npm run dev:backend
```

### Build for Production
```bash
npm run build
```

### Start Production Server
```bash
npm start
```

## 🛠️ Troubleshooting

### Kill Stuck Processes
If ports 3000 or 8000 are already in use:
```bash
npm run kill:ports
```

### Manual Port Cleanup
```bash
# Find process on port 3000 (frontend)
lsof -i:3000

# Find process on port 8000 (backend)
lsof -i:8000

# Kill specific process
kill -9 <PID>
```

### Backend Virtual Environment Issues
If you see Python import errors, ensure the virtual environment is set up:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔑 Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (backend/.env)
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/scalper_bot
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

## 💡 Tips

1. **Auto-reload**: Both servers support hot-reload during development
2. **Logs**: All logs appear in the same terminal with color-coded prefixes
3. **Stop servers**: Press `Ctrl+C` once to stop both servers gracefully
4. **Database**: Make sure PostgreSQL and Redis are running before starting the backend

## 🎯 First Time Setup

1. Install dependencies:
   ```bash
   npm install
   cd backend && pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env.local
   cp backend/.env.example backend/.env
   # Edit both files with your configuration
   ```

3. Start development servers:
   ```bash
   npm run dev
   ```

That's it! 🎉
