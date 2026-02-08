# Running the Curio Decision Record System

This guide explains how to set up and run the Curio Decision Record System locally.

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

## Database Setup

1. Start PostgreSQL (if not already running)

2. Create the database:
```bash
psql -U postgres -c "CREATE DATABASE curio_decision_record;"
```

Or connect to psql and run:
```sql
CREATE DATABASE curio_decision_record;
```

## Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Create a `.env` file for configuration:
```bash
# backend/.env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=curio_decision_record
DB_USER=postgres
DB_PASSWORD=postgres
```

5. Create and initialize the database:
```bash
python init_db.py create  # Create the database
python init_db.py init    # Create all tables
```

6. Run the backend server:
```bash
python app.py
```

The API will be available at `http://localhost:5001`

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The UI will be available at `http://localhost:3000`

## Running Both Together

You can run both servers in separate terminal windows, or use a process manager.

### Option 1: Separate Terminals

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
python app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### Option 2: Using a Script

Create a `start.sh` script in the project root:
```bash
#!/bin/bash
cd backend && source venv/bin/activate && python app.py &
cd frontend && npm run dev &
wait
```

## Verifying the Setup

1. Open `http://localhost:3000` in your browser
2. You should see the Curio homepage with an empty projects list
3. Create a new project by clicking "New Project"
4. Add decisions and records to verify everything works

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready`
- Check the database exists: `psql -U postgres -l`
- Verify the connection string in `.env` or `config.py`

### Port Already in Use

Backend (Flask):
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9
```

Frontend (Vite):
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Table Issues

If you have issues with tables:
```bash
# Recreate all tables (development only!)
python init_db.py init
```

## Production Deployment

For production deployment:

1. Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 "app:app"
```

2. Build the frontend for production:
```bash
cd frontend
npm run build
```

3. Serve the built frontend with a web server like Nginx

4. Use environment variables for sensitive configuration

5. Set up proper database backups
