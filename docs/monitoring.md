## Monitoring with New Relic

Basic New Relic configuration is done in [newrelic.ini](../newrelic.ini)

Additional settings are specified in each deployment environment's manifest file as environment variables.

    NEW_RELIC_CONFIG_FILE
    NEW_RELIC_ENV
    NEW_RELIC_LOG

You must to supply the `NEW_RELIC_LICENSE_KEY` as part of each deployment's
`VCAP_SERVICES` user-provided-service.

To set or update this value, for each cloud.gov space:

```bash
cf target -s {SPACE}
cf cups VCAP_SERVICES -p NEW_RELIC_LICENSE_KEY
<enter license key>
```
