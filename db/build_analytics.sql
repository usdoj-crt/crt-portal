-- Don't drop the analytics schema, it might have valuable data
CREATE SCHEMA IF NOT EXISTS analytics;

-- Try to start fresh, but don't flip out if the user doesn't exist.
\set ON_ERROR_STOP 0
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics, public FROM analytics;
ALTER DEFAULT PRIVILEGES FOR USER analytics IN SCHEMA public REVOKE SELECT ON TABLES FROM analytics;
DROP USER analytics;
\set ON_ERROR_STOP 1

-- User needs access to both existing and future tables
CREATE USER analytics;

-- We'll need to SELECT from application tables and info:
GRANT CONNECT ON DATABASE postgres TO analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics;
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA public GRANT SELECT ON TABLES TO analytics;

-- Jupyter expects these to exist, but they might also be created by Django:
CREATE TABLE IF NOT EXISTS analytics.analyticsfile ();
-- We'll need to do anything in the analytics schema:
GRANT ALL PRIVILEGES ON SCHEMA analytics TO analytics;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO analytics;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO analytics;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA analytics TO analytics;
-- We'll need to do those things for things created after this script is run:
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA analytics GRANT ALL PRIVILEGES ON TABLES TO analytics;
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA analytics GRANT ALL PRIVILEGES ON SEQUENCES TO analytics;
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA analytics GRANT ALL PRIVILEGES ON FUNCTIONS TO analytics;

ALTER USER analytics PASSWORD '$POSTGRES_ANALYTICS_PASSWORD';
