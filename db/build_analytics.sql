-- Don't drop the analytics schema, it might have valuable data
CREATE SCHEMA IF NOT EXISTS analytics;

-- Try to start fresh, but don't flip out if the user doesn't exist.
\set ON_ERROR_STOP 0
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics, public FROM analytics;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE SELECT ON TABLES FROM analytics;
DROP USER analytics;
\set ON_ERROR_STOP 1

-- User needs access to both existing and future tables
CREATE USER analytics;
GRANT CONNECT ON DATABASE postgres TO analytics;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics;
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.dashboard_embed TO analytics;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL PRIVILEGES ON TABLES TO analytics;

ALTER USER analytics PASSWORD '$POSTGRES_ANALYTICS_PASSWORD';
