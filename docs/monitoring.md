## Monitoring with New Relic

Basic New Relic configuration is done in [newrelic.ini](../newrelic.ini)

Additional settings are specified in each deployment environment's manifest file as environment variables.

    NEW_RELIC_CONFIG_FILE
    NEW_RELIC_ENV
    NEW_RELIC_LOG

You must to supply the `NEW_RELIC_LICENSE_KEY` as part of each deployment's
`VCAP_SERVICES` user-provided-service.

To set or update this value, for each cloud.gov space:

**Note Running these commands will over-write any existing variables
stored in `VCAP_SERVICES`**

We need to preserve any other existing user provided variables such as SSO configuration if
enabled.

You can view what is currently stored in `VCAP_SERVICES` with:

    cf env crt-portal-django

### For development:
```bash
cf target -s dev
cf uups VCAP_SERVICES -p '{"SECRET_KEY":"<value>", "NEW_RELIC_LICENSE_KEY":"<value>"}'
```

### For Staging:
```bash
cf target -s staging
cf uups VCAP_SERVICES -p '{"SECRET_KEY":"<value>", "AUTH_GROUP_CLAIM":"<value>", "AUTH_SERVER":"<value>", "AUTH_USERNAME_CLAIM":"<value>", "NEW_RELIC_LICENSE_KEY":"<value>"}'
```

### For Production:
```bash
cf target -s production
cf uups VCAP_SERVICES -p '{"SECRET_KEY":"<value>", "AUTH_GROUP_CLAIM":"<value>", "AUTH_SERVER":"<value>", "AUTH_USERNAME_CLAIM":"<value>", "NEW_RELIC_LICENSE_KEY":"<value>"}'
```
