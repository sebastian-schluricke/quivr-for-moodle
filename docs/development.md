# Quivr Local Development Guide

This guide provides instructions on how to set up and develop the Quivr project locally. It covers the prerequisites, installation, project structure, and development workflow.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Contribution Guidelines](#contribution-guidelines)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Git**: For version control
- **Docker**: For containerization (version 20.10.0 or higher)
- **Docker Compose**: For multi-container Docker applications (version 2.0.0 or higher)
- **Supabase CLI**: For local Supabase development
- **Node.js**: For frontend development (version 18 or higher)
- **Python**: For backend development (version 3.11)
- **npm** or **yarn**: For JavaScript package management

### Installing Supabase CLI

Follow the instructions [here](https://supabase.com/docs/guides/cli/getting-started) to install the Supabase CLI.

```bash
supabase -v # Check that the installation worked
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/quivrhq/quivr.git
cd quivr
```

### 2. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit the `.env` file to add your API keys and configuration:

```bash
# Use your preferred text editor
vim .env  # or nano .env, code .env, etc.
```

At minimum, you need to update the `OPENAI_API_KEY` variable. You can get your API key [here](https://platform.openai.com/api-keys).

### 3. Start Supabase Locally

```bash
cd backend
supabase start
cd ..
```

### 4. Development Options

#### Option A: Run Everything with Docker (Recommended for Full Stack Testing)

This option runs both frontend and backend in Docker containers:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Access the application at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5050/docs
- Supabase: http://localhost:54323

#### Option B: Run Frontend and Backend Separately (Recommended for Development)

This option gives you more flexibility for development:

1. **Start the Backend Services**:

```bash
docker compose -f docker-compose.dev.yml up backend-api redis worker notifier beat flower
```

2. **Start the Frontend Development Server** (in a new terminal):

```bash
cd frontend
npm install  # or yarn install
npm run dev  # or yarn dev
```

Access the application at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5050/docs
- Supabase: http://localhost:54323

#### Option C: Run Everything Without Docker (Real-time Development)

This option allows you to run all components directly on your local machine without Docker, giving you the most flexibility for real-time development:

1. **Install Dependencies**:

First, set up your Python virtual environment and install the required dependencies:

```bash
# Create and activate a virtual environment
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements-dev.lock
```

2. **Start Supabase Locally**:

Supabase requires Docker, but you can run just the Supabase services:

```bash
cd backend
supabase start
```

3. **Install and Start Redis**:

Redis is required for Celery. Install it locally:

- **Windows**: Download and install [Redis for Windows](https://github.com/tporadowski/redis/releases)
- **macOS**: `brew install redis && brew services start redis`
- **Linux**: `sudo apt install redis-server && sudo systemctl start redis-server`

4. **Start the Backend API**:

```bash
# Make sure you're in the project root
cd backend/api
# Set PYTHONPATH to include all backend modules
set PYTHONPATH=C:\path\to\quivr\backend  # Windows
# OR
export PYTHONPATH=/path/to/quivr/backend  # macOS/Linux

# Start the FastAPI application
python -m uvicorn quivr_api.main:app --host 0.0.0.0 --port 5050 --reload
```

5. **Start the Celery Workers** (in a new terminal):

```bash
# Activate your virtual environment
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux

cd backend/worker
# Set PYTHONPATH to include all backend modules
set PYTHONPATH=C:\path\to\quivr\backend  # Windows
# OR
export PYTHONPATH=/path/to/quivr/backend  # macOS/Linux

# Start the Celery worker
python -m celery -A quivr_worker.celery_worker worker -l info
```

6. **Start the Celery Beat** (in a new terminal):

```bash
# Activate your virtual environment
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux

cd backend/worker
# Set PYTHONPATH to include all backend modules
set PYTHONPATH=C:\path\to\quivr\backend  # Windows
# OR
export PYTHONPATH=/path/to/quivr/backend  # macOS/Linux

# Start the Celery beat
python -m celery -A quivr_worker.celery_worker beat -l info
```

7. **Start the Celery Flower** (optional, for monitoring):

```bash
# Activate your virtual environment
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux

cd backend/worker
# Set PYTHONPATH to include all backend modules
set PYTHONPATH=C:\path\to\quivr\backend  # Windows
# OR
export PYTHONPATH=/path/to/quivr/backend  # macOS/Linux

# Start Flower
python -m celery -A quivr_worker.celery_worker flower -l info --port=5555
```

8. **Start the Frontend Development Server** (in a new terminal):

```bash
cd frontend
npm install  # or yarn install
npm run dev  # or yarn dev
```

Access the application at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5050/docs
- Supabase: http://localhost:54323
- Celery Flower (monitoring): http://localhost:5555

### 5. Login to the Application

You can sign in to the app with the default credentials:
- Email: `admin@quivr.app`
- Password: `admin`

## Project Structure

Quivr is organized into several main components:

### Frontend (`/frontend`)

A Next.js application with TypeScript and React:

- `/app`: Next.js app directory with route components
- `/lib`: Shared utilities, hooks, and components
- `/public`: Static assets and localization files
- `/styles`: Global CSS and styling

Key technologies:
- Next.js for the framework
- React for UI components
- Tailwind CSS for styling
- Supabase for authentication
- TypeScript for type safety

### Backend (`/backend`)

A Python-based backend with multiple components:

- `/api`: FastAPI application that serves the REST API
- `/core`: Core business logic and utilities
- `/worker`: Celery workers for background tasks
- `/supabase`: Supabase configuration and migrations

Key technologies:
- FastAPI for the API framework
- Celery for background tasks
- Redis for message queuing
- Supabase for database and authentication

### Docker Configuration

- `docker-compose.yml`: Production configuration
- `docker-compose.dev.yml`: Development configuration
- `Dockerfile` and `Dockerfile.dev`: Container definitions

## Development Workflow

### Frontend Development

1. Make changes to the frontend code in the `/frontend` directory
2. The development server will automatically reload with your changes
3. Use the following commands for frontend development:

```bash
# In the frontend directory
npm run lint        # Run ESLint to check code quality
npm run format-fix  # Format code with Prettier
npm run test-unit   # Run unit tests
npm run test-e2e    # Run end-to-end tests
```

### Backend Development

1. Make changes to the backend code in the `/backend` directory
2. The development server will automatically reload with your changes
3. Use the following commands for backend development:

```bash
# For running tests (inside the backend container)
python -m pytest

# For applying database migrations
cd backend
supabase migration up
```

### Working with Supabase

Supabase provides the database, authentication, and storage for Quivr:

1. Access the Supabase dashboard at http://localhost:54323
2. Use the SQL editor to run custom queries
3. Manage database tables, functions, and policies

## Testing

### Frontend Tests

```bash
# In the frontend directory
npm run test-unit   # Run unit tests with Vitest
npm run test-e2e    # Run end-to-end tests with Playwright
```

### Backend Tests

```bash
# Inside the backend container
python -m pytest
```

## Contribution Guidelines

1. **Fork the Repository**: Create your own fork of the repository
2. **Create a Branch**: Make your changes in a new branch
3. **Follow Coding Standards**:
   - Use ESLint and Prettier for frontend code
   - Follow PEP 8 for Python code
4. **Write Tests**: Add tests for new features or bug fixes
5. **Submit a Pull Request**: Open a PR with a clear description of your changes

For more details on contributing, check out the [Contribution Guidelines](https://docs.quivr.app/docs/Developers/contribution/guidelines).

## Troubleshooting

### Common Issues

1. **Docker Errors**:
   - Ensure Docker is running
   - Try stopping and removing all containers with `docker compose down`
   - Check if ports 3000, 5050, or 54321 are already in use

2. **Supabase Issues**:
   - Ensure Supabase CLI is installed correctly
   - Try restarting Supabase with `supabase stop` and `supabase start`

3. **Frontend Build Errors**:
   - Clear the Next.js cache with `rm -rf .next`
   - Ensure all dependencies are installed with `npm install`

4. **Backend Errors**:
   - Check the logs with `docker compose logs backend-api` (for Docker setup)
   - Ensure environment variables are set correctly

5. **Docker-free Development Issues**:
   - **PYTHONPATH Issues**: Make sure the PYTHONPATH is set correctly to include all backend modules
   - **Redis Connection Errors**: Verify Redis is running with `redis-cli ping` (should return "PONG")
   - **Celery Worker Errors**: Check that the Celery worker can connect to Redis
   - **Module Import Errors**: Ensure all dependencies are installed in your virtual environment
   - **Port Conflicts**: Make sure no other services are using ports 3000, 5050, 5555, or 6379
   - **Environment Variables**: Verify that all required environment variables are set correctly in your .env file

## Additional Resources

- [Quivr Documentation](https://docs.quivr.app/)
- [Supabase Documentation](https://supabase.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
