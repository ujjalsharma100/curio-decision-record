# Curio Decision Record Backend

A simplified Flask backend for managing decision records.

## Architecture

The application follows a clean layered architecture:

- **app.py** - Flask application with API endpoints (only interacts with decision_service)
- **decision_service.py** - Business logic layer (interacts with database_service)
- **database_service.py** - Database operations layer (PostgreSQL CRUD operations)
- **models.py** - Data models/classes
- **sql/** - SQL files for table creation

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   Create a `.env` file in the backend directory with the following variables:
   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=curio_decision_record
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_SCHEMA=public

   # Flask Configuration
   FLASK_ENV=development
   PORT=5000
   ```

3. **Initialize the database:**
   ```bash
   # Create the database (if it doesn't exist)
   python init_db.py create

   # Initialize tables (uses SQL files from sql/ directory)
   python init_db.py init
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000` (or the port specified in your `.env` file).

## Project Structure

```
backend/
├── app.py                      # Flask application with all routes
├── decision_service.py          # Business logic layer
├── database_service.py          # Database operations layer
├── models.py                    # Data models/classes
├── init_db.py                   # Database initialization script
├── requirements.txt             # Python dependencies
├── sql/                         # SQL files for table creation
│   ├── projects.sql
│   ├── decisions.sql
│   ├── decision_records.sql
│   ├── decision_record_status_history.sql
│   └── decision_record_relationships.sql
└── README.md                    # This file
```

## API Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create a new project
- `GET /api/projects/<project_id>` - Get a project by ID
- `PUT /api/projects/<project_id>` - Update a project
- `DELETE /api/projects/<project_id>` - Delete a project

### Decisions
- `GET /api/projects/<project_id>/decisions` - List all decisions for a project
- `POST /api/projects/<project_id>/decisions` - Create a new decision
- `GET /api/decisions/<decision_id>` - Get a decision by ID
- `PUT /api/decisions/<decision_id>` - Update a decision
- `DELETE /api/decisions/<decision_id>` - Delete a decision

### Decision Records
- `GET /api/decisions/<decision_id>/records` - List all records for a decision
- `POST /api/decisions/<decision_id>/records` - Create a new decision record
- `GET /api/records/<record_id>` - Get a record by ID
- `PUT /api/records/<record_id>` - Update a record
- `DELETE /api/records/<record_id>` - Delete a record
- `PATCH /api/records/<record_id>/status` - Change record status
- `GET /api/records/<record_id>/history` - Get status history

### Relationships
- `GET /api/records/<record_id>/relationships` - List relationships for a record
- `POST /api/records/<record_id>/relationships` - Create a relationship
- `DELETE /api/relationships/<relationship_id>` - Delete a relationship

### Health Check
- `GET /health` - Health check endpoint

## Database

The application uses PostgreSQL for persistence. The database service handles:
- Connection pooling
- Schema management
- Table creation from SQL files
- All database CRUD operations

## Status Transitions

Decision records can have the following statuses:
- `proposed` - Initial status for new records
- `accepted` - Record has been accepted
- `implemented` - Record has been implemented
- `implemented_inferred` - Implementation was inferred
- `rejected` - Record was rejected
- `deprecated` - Record is deprecated

Valid status transitions are enforced by the decision service.

## Data Flow

1. **API Request** → `app.py` (endpoints)
2. **Business Logic** → `decision_service.py` (validation, status transitions, etc.)
3. **Database Operations** → `database_service.py` (CRUD operations)
4. **PostgreSQL** → Database
