## How to use:

1. Install dependencies:
    ```bash
    poetry install
    ```

2. Prepare .env and .env.test
    ```bash
    make prepare_envs
    ```

3. Fill .env and .env.test:

    Env file:
    ```ini
    # General application settings
    DEBUG = "True"  # Enables debug mode (set to "False" for production)
    LOG_LEVEL = "debug"  # Sets the logging level (debug, info, warning, error, critical)
    APP_PORT = 8000  # Port on which the application will run
    SERVICE_NAME = "balance-service" # Name of the service

    # Database connection settings
    DATABASE__DRIVERNAME = "postgresql+asyncpg"  # Database driver (PostgreSQL with asyncpg)
    DATABASE__HOST = "db"  # Hostname of the database server
    DATABASE__PORT = 5432  # Port of the database server
    DATABASE__POSTGRES_USERNAME = "postgres"  # Username for database connection
    DATABASE__POSTGRES_PASSWORD = ""  # Password for database connection (set a secure password for production)
    DATABASE__DB_NAME = ""  # Name of the database (e.g., balance_db)
    ```

    Env for tests:
    ```ini
    # Database connection settings for the test environment
    DATABASE__DRIVERNAME = "postgresql+asyncpg"  # Database driver (PostgreSQL with asyncpg)
    DATABASE__HOST = "db_test"  # Hostname of the test database server (likely a Docker container)
    DATABASE__PORT = 5433  # Port of the test database server
    DATABASE__POSTGRES_USERNAME = "postgres"  # Username for test database connection
    DATABASE__POSTGRES_PASSWORD = ""  # Password for test database connection (often left blank for test databases)
    DATABASE__DB_NAME = ""  # Name of the test database (e.g., balance_db_test) 
    ```

4. Start application and database:
    ```bash
    make start_app
    ```

5. Migrate database:
    ```bash
    make make_db_migrations
    ```

6. Make commands:
    ```makefile
    start_test_db:  # Start the test database in a Docker container.
      sudo docker compose --env-file .env.test -f docker-compose.test.yml up --build

    stop_test_db:  # Stop the test database container.
      sudo docker compose -f docker-compose.test.yml stop

    run_tests:  # Run the test suite against the test database.
      clear
      sudo docker compose --env-file .env.test -f docker-compose.test.yml up --build -d
      -poetry run pytest
      sudo docker compose -f docker-compose.test.yml stop

    start_app_detached:  # Start the application in detached mode (background).
      sudo docker compose up --build -d

    start_app:  # Start the application in the foreground.
      sudo docker compose up --build

    stop_app:  # Stop the application.
      sudo docker compose stop

    prepare_envs:  # Prepare envs.
      cp .env.dist .env
      cp .env.test.dist .env.test

    make_db_migrations:  # Make database migrations.
      poetry run alembic revision --autogenerate
      poetry run alembic upgrade head
    ```



## Based on fastapi-sqlalchemy-template

https://github.com/mdhishaamakhtar/fastapi-sqlalchemy-postgres-template/

This is for test purposes only.
