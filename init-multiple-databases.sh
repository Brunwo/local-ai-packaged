#!/bin/bash
set -e
set -u

function create_user_and_database() {
    local database=$1
    echo "Creating user and database '$database'"

    # First, export the password for psql
    export PGPASSWORD="$POSTGRES_PASSWORD"

    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --host "db" --dbname "postgres" --port "5432" <<-EOSQL
        \set ON_ERROR_STOP on

        -- Create user if it doesn't exist
        DO \$\$
        BEGIN
           IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$database') THEN
              EXECUTE 'CREATE USER $database WITH PASSWORD ''$database''';
              RAISE NOTICE 'Created user: $database';
           ELSE
              RAISE NOTICE 'User already exists: $database';
           END IF;
        END
        \$\$;
EOSQL

    # Create database using createdb command which handles duplicates gracefully
    # First check if it exists using retval
    if PGPASSWORD="$POSTGRES_PASSWORD" psql -h db -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$database"; then
        echo "Database '$database' already exists."
    else
        echo "Database '$database' does not exist, creating..."
        if createdb -h db -U "$POSTGRES_USER" -O "$database" "$database"; then
            echo "Database '$database' created successfully."
        else
            echo "ERROR: Failed to create database '$database'"
            exit 1
        fi
    fi

    # Grant ONLY database-specific privileges (no cross-database access)
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --host "db" --dbname "postgres" --port "5432" -c "GRANT ALL PRIVILEGES ON DATABASE \"$database\" TO \"$database\";"

    # For now, skip the cross-database revoke since users might not exist yet
    # We'll handle this in a second pass after all databases are created

    if [ "$database" = "litellmdb" ]; then
        # Grant additional permissions needed by LiteLLM
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --host "db" --dbname "postgres" --port "5432" -c "ALTER USER \"$database\" CREATEDB;"
    fi

    unset PGPASSWORD
}

# Main execution logic
if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
    echo "Creating databases: $POSTGRES_MULTIPLE_DATABASES"

    # Wait for main database to be ready
    echo "Waiting for main PostgreSQL database to be ready..."
    timeout=60
    counter=0
    while ! pg_isready -h db -U "$POSTGRES_USER" -t 10 >/dev/null 2>&1; do
        if [ $counter -gt $timeout ]; then
            echo "ERROR: PostgreSQL main database did not become ready in time"
            exit 1
        fi
        echo "Waiting for PostgreSQL main database... ($counter/$timeout)"
        sleep 2
        counter=$((counter + 2))
    done

    echo "PostgreSQL main database is ready. Proceeding with database creation..."

    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        echo "Processing database: $db"
        create_user_and_database "$db"
    done

    echo "Database initialization completed successfully"

    # Second pass: Apply cross-database access restrictions now that all users exist
    echo "Applying cross-database access restrictions..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --host "db" --dbname "postgres" --port "5432" <<-EOSQL
        -- Revoke connect privilege from databases this user shouldn't access
        REVOKE CONNECT ON DATABASE litellmdb FROM n8ndb;
        REVOKE CONNECT ON DATABASE n8ndb FROM litellmdb;
        -- Ensure users can only connect to their own databases
        -- Note: PostgreSQL enforces this at connection time
EOSQL
    echo "Security restrictions applied successfully"

else
    echo "No multiple databases configured"
fi
