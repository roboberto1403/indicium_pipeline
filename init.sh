#!/bin/bash
set -e

# Wait for PostgreSQL to be ready (optional but recommended)
until pg_isready -h localhost -p 5432 -U roboberto; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

echo "PostgreSQL is ready. Populating database..."

# Copy the SQL file into the container
docker cp northwind.sql db_source:/tmp/northwind.sql

# Execute the SQL file
docker exec -i db_source psql -U roboberto -d northwind -f /tmp/northwind.sql

echo "Database population complete."

# Keep the container running (if your original entrypoint was just starting postgres)
# If your original image already has an entrypoint that keeps postgres running, you might not need this.
exec "$@"