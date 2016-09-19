DROP TABLE data;
DROP TABLE metrics;
CREATE TABLE metrics(
  id SERIAL,
  name TEXT PRIMARY KEY,
  key_hash BYTEA CHECK (length(key_hash) = 128), --the SHA512 hash of the API key for the service.
  privileged BOOLEAN --whether authenticaion is required to view
);
CREATE TABLE data(
  id SERIAL PRIMARY KEY,
  metric_name TEXT REFERENCES metrics(name),
  data JSONB,
  creation_time TIMESTAMP,
  insert_time TIMESTAMP
);
