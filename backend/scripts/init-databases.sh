#!/bin/bash
set -e
echo "Initializing databases..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE IF NOT EXISTS auth_db;
    CREATE DATABASE IF NOT EXISTS catalog_db;
    CREATE DATABASE IF NOT EXISTS order_db;
    GRANT ALL PRIVILEGES ON DATABASE auth_db TO postgres;
    GRANT ALL PRIVILEGES ON DATABASE catalog_db TO postgres;
    GRANT ALL PRIVILEGES ON DATABASE order_db TO postgres;
EOSQL
echo "Databases initialized!"
