# Quivr Local Run Configurations

I've created run configurations for JetBrains IDEs (PyCharm, IntelliJ IDEA, etc.) to run the Quivr services locally. These configurations allow you to start the FastAPI backend and Celery workers without using Docker.

## What's Included

The run configurations are located in the `.run` directory and include:

1. **backend-api**: Runs the FastAPI backend API server
2. **worker**: Runs the Celery worker for processing background tasks
3. **notifier**: Runs the notifier service that monitors Celery tasks and sends notifications
4. **beat**: Runs the Celery beat service for scheduling periodic tasks

## How to Use

1. Make sure you have the prerequisites installed:
   - Python 3.11
   - Redis (for Celery)
   - Supabase CLI (for local Supabase)

2. Set up your environment:
   - Create and activate a Python virtual environment
   - Install dependencies from `backend/requirements-dev.lock`
   - Start Supabase locally with `supabase start`
   - Start Redis
   - Set up your environment variables in the `.env` file

3. Open the project in your JetBrains IDE (PyCharm, IntelliJ IDEA, etc.)
   - The run configurations should be automatically loaded from the `.run` directory

4. Start the services in the following order:
   1. Make sure Redis is running
   2. Start the `backend-api` service
   3. Start the `worker` service
   4. Start the `notifier` service
   5. Start the `beat` service

## Detailed Documentation

For more detailed information about the run configurations, including troubleshooting tips, see the README.md file in the `.run` directory.

## Comparison with Docker

These run configurations provide the same functionality as the Docker services defined in `docker-compose.yml`:

| Docker Service | Run Configuration | Command |
|---------------|-------------------|---------|
| backend-api | backend-api | `python -m uvicorn quivr_api.main:app --host 0.0.0.0 --port 5050 --reload` |
| worker | worker | `python -m celery -A quivr_worker.celery_worker worker -l info` |
| notifier | notifier | `python quivr_worker/celery_monitor.py` |
| beat | beat | `python -m celery -A quivr_worker.celery_worker beat -l info` |

The advantage of using these run configurations is that you can run the services directly on your local machine without Docker, which can be more convenient for development and debugging.