CREATE DATABASE restaurant;
CREATE ROLE restaurant with LOGIN PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE restaurant TO restaurant;
