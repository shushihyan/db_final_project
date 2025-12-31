# Library API — Quickstart

This repository contains a small FastAPI-based Library Management API and helper scripts to initialize and populate a local PostgreSQL database for manual testing.

The steps below show how to clone the repo, bring up a local Postgres with Docker Compose, configure environment variables, start the API, populate the database with test data, and run the provided test queries to see results.

## Prerequisites

- Git
- Docker and Docker Compose (or the `docker compose` plugin)
- Python 3.10+ and pip (recommended to use a virtualenv)

## Quickstart (recommended)

1. Clone the repository and cd into it:

   git clone <your-repo-url>
   cd library_api

2. Start Postgres using Docker Compose:

   docker compose up -d

   The included `docker-compose.yml` launches a Postgres 15 container bound to host port `5407` by default.

3. Create a `.env` file in the repository root with the database connection values used by the app and scripts.

   Example `.env` (adjust if you change docker-compose credentials):

   DATABASE_URL=postgresql+psycopg2://user5407:12345678@localhost:5407/library_db
   DB_HOST=localhost
   DB_PORT=5407
   DB_ADMIN_USER=user5407
   DB_ADMIN_PASSWORD=12345678
   DB_NAME=library_db
   DB_USER=library_user
   DB_PASSWORD=library_password

   Notes:
   - `DATABASE_URL` is used by the application (SQLAlchemy) to connect. Make sure it follows the format:
     `postgresql+psycopg2://<user>:<password>@<host>:<port>/<db>`
   - `init_db.py` reads `DB_ADMIN_*` variables to perform database/user creation. The defaults in the script are safe to override via `.env`.

4. (Optional) Install Python dependencies in a virtual environment:

   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

5. Initialize the database user/database (optional):

   The repository includes `scripts/init_db.py` which can create the `DB_USER` and `DB_NAME` using the admin credentials provided above. Run this once after Postgres is ready:

   python3 scripts/init_db.py

   If your Postgres container was started from the included `docker-compose.yml`, the container creates `library_db` already, but running `init_db.py` is harmless and will create the application user (`library_user` in the example) and grant privileges if needed.

6. Start the API server (in a separate terminal):

   uvicorn main:app --reload --port 8000

   - The API will be available at: `http://localhost:8000`
   - Swagger UI: `http://localhost:8000/docs`

7. Populate the API with test data and run sample queries:

   - Fill the database with generated sample books/orders (the script uses the running API at http://localhost:8000):

     python3 scripts/fill_db.py

   - Run quick API test queries (uses the same base URL):

     python3 scripts/test_queries.py

   Both scripts assume the API is reachable at `http://localhost:8000` (this is the default inside the scripts). If you run the API on a different host/port, update the `BASE_URL` value at the top of the script files.

## Quick manual checks

- Visit `http://localhost:8000/docs` to explore endpoints and make requests interactively.
- To list all books with curl:

  curl -s http://localhost:8000/books/ | jq '.'

## Troubleshooting

- If the API raises database connection errors, verify:
  - The Postgres container is running: `docker ps`
  - Port mapping (host port `5407` by default) is correct
  - `DATABASE_URL` in your `.env` is correct and available to the Python process
- If `init_db.py` fails because it cannot connect as the admin user, check `DB_ADMIN_USER` / `DB_ADMIN_PASSWORD` in `.env` and the docker-compose credentials.
- If the `fill_db.py` or `test_queries.py` scripts cannot reach the API, ensure the API server (uvicorn) is running and accessible at `http://localhost:8000`.

## Security note

The credentials and configuration in this repository are for local testing only. Do not use them in production.

## Summary

1. Clone
2. docker compose up -d
3. Create `.env` (set `DATABASE_URL` and `DB_*` vars) (optional)
4. (Optional) pip install -r requirements.txt
5. python3 scripts/init_db.py
6. uvicorn main:app --reload --port 8000
7. python3 scripts/fill_db.py
8. python3 scripts/test_queries.py

Enjoy exploring the API!
