# API specification
This document outlines the API implemented by the backend.

## Inserting new readings

URI:
```
POST /metrics/[metric name]/?api_key=[API key]
```

Inserts the data provided (as JSON) with the POST request as a new reading for the metric.

Data format:
```
{
  "creation_time": "YYYY-MM-DD HH:MM:SS",
  "data": {...}
}
```

## Getting a list of available metrics.
URI:
```
GET /metrics/
```

Gets a list of metrics that can be fetched. If this was done properly, it would not expose the existence of authentication-required metrics.

Data format:
```
{
  "metrics": [
    {
      "name": "..."
    },
    ...
  ]
}
```

## Getting the data for a metric.
URI:
```
GET /metrics/[metric name]
```

Gets all the data for this metric.

Data format:
```
{
  "metric_name": "..."
  "readings": [
    {
      "creation_time": "YYYY-MM-DD HH:MM:SS",
      "data": {...}
    },
    ...
  ]
}
```
**[TODO]** Add time/date limits for this.

**[TODO]** Add authentication handling.
