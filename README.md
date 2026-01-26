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
   Run the following command in the root directory of the project. **The docker-compose.yml file is used for development, and the stack.yaml file is used for production** (on docker swarm).
   ```bash
   # Dev mode
   docker compose up --watch --build
   ```

3. **Access the services**:
   - **Frontend**: [http://localhost](http://localhost)
   - **Backend API Documentation**: [http://localhost/docs](http://localhost/docs)

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
- Each user can find a link to import the calendar of the events he is subscribed to in the **Mon profil** tab.

## Development

- **Backend Code**: Located in `backend/`
- **Frontend Code**: Located in `frontend/`
- **Database**: PostgreSQL data is persisted in the `postgres_data` volume. To reset the database, run and add :
  ```bash
  docker compose exec backend python load_fixtures.py <email> --reset
  ```

### Make a superadmin

docker compose exec backend python make_superadmin.py <email>
```

### Push Notifications

To enable push notifications, you need to generate VAPID keys.

1. Generate keys:
   ```bash
   # You can use the web-push library or an online generator
   # Example using npx:
   npx web-push generate-vapid-keys
   ```

2. Add them to your `.env` file (create if needed):
   ```env
   VAPID_PUBLIC_KEY=<your_public_key>
   VAPID_PRIVATE_KEY=<your_private_key>
   ADMIN_EMAIL=mailto:admin@example.com
   CRON_DELAY=900
   ```
