FROM postgres:11.14-alpine
RUN apk update
RUN apk add gettext  # For envsubst

ARG analytics_password
ENV POSTGRES_ANALYTICS_PASSWORD $analytics_password

COPY db/build_analytics.sql /
RUN envsubst < build_analytics.sql > docker-entrypoint-initdb.d/build_analytics.sql
