-- Sample SQL file for the test fixture
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE
);

CREATE INDEX idx_customers_email ON customers(email);
