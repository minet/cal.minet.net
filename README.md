# Calend'INT

Calend'INT is an associative calendar platform designed for campus students to discover and subscribe to events from various student organizations (associations, clubs, BDE lists, etc.).

## Features

- **User Accounts**: Sign up and manage your subscriptions.
- **Organizations**: Browse and subscribe to different campus organizations.
- **Events**: View events in a calendar or list view.
- **ICS Export**: Export your personalized calendar to your favorite calendar app (Google Calendar, Outlook, etc.).
- **Permissions**: Granular role-based access control (Superadmin, Org Admin, Member, Viewer).

## Tech Stack

- **Backend**: Python (FastAPI), SQLModel, PostgreSQL
- **Frontend**: Vue.js 3, Vite, TailwindCSS
- **Infrastructure**: Docker, Docker Compose

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop/Engine).

## Getting Started

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd calendint
   ```

2. **Start the application**:
   Run the following command in the root directory of the project:
   ```bash
   docker compose up --build
   ```

3. **Access the services**:
   - **Frontend**: [http://localhost:5173](http://localhost:5173)
   - **Backend API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Usage

### User Registration
- Go to the Frontend URL.
- Click on "Register" to create a new account.
- Log in with your credentials.

### Managing Organizations & Events
- Navigate to the **Organizations** tab to view or create organizations.
- Navigate to the **Events** tab to view or create events.
- *Note: Currently, permission enforcement is basic. You may need to manually adjust database roles for advanced testing.*

### ICS Export
- Your personalized ICS link can be generated via the API (implementation in progress).
- Endpoint: `http://localhost/api/calendar/user/{user_id}.ics`

## Development

- **Backend Code**: Located in `backend/`
- **Frontend Code**: Located in `frontend/`
- **Database**: PostgreSQL data is persisted in the `postgres_data` volume. To reset the database, run:
  ```bash
  docker compose down -v
  docker compose up --build
  ```

### Make a superadmin

```sh
docker compose exec backend python make_superadmin.py <email>
```