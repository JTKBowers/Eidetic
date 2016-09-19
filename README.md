# Eidetic
A lifelogging application. Consists of a thin database wrapper backend, a web based frontend, and an API for a diverse range of services to inject metrics into the database.

## Components:
### Backend
A thin wrapper around a Postgres database. It provides an API for:

- Inserting new readings.
- Getting a list of available metrics.
- Getting the data for a metric.

### Frontend
**[TODO]**

### Services
Services are small daemons that interact with the outside world and insert data into the database using the API.
