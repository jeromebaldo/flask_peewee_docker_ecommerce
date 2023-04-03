CREATE TABLE product (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    image VARCHAR(255) NOT NULL,
    weight INTEGER NOT NULL,
    price FLOAT NOT NULL,
    in_stock BOOLEAN NOT NULL
);
