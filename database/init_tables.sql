DROP TABLE data;
DROP TABLE services;
CREATE TABLE services(
  id SERIAL,
  name TEXT PRIMARY KEY,
  key_hash BYTEA CHECK (length(key_hash) = 128), --the SHA512 hash of the API key for the service.
  privileged BOOLEAN --whether authenticaion is required to view
);
CREATE TABLE data(
  id SERIAL PRIMARY KEY,
  service_name TEXT REFERENCES services(name),
  data JSONB,
  creation_time TIMESTAMP,
  insert_time TIMESTAMP
);
