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

