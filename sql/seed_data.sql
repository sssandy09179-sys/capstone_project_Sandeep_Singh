SET GLOBAL local_infile = 1;
SHOW VARIABLES LIKE 'local_infile';

    -- orders.csv
LOAD DATA LOCAL INFILE 'D:/Capstone Project/Raw Data/orders.csv'
INTO TABLE orders
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    order_id,
    customer_id,
    product_id,
    order_date,
    quantity,
    @discount,
    payment_method,
    @rating,
    returned
)
SET
    discount_pct = NULLIF(TRIM(@discount), ''),
    rating = NULLIF(TRIM(@rating), '');
    
-- customers.csv
LOAD DATA LOCAL INFILE 'D:/Capstone Project/Raw Data/customers.csv'
INTO TABLE customers
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    customer_id,
    name,
    city,
    city_tier,
    signup_date,
    acquisition_source
);

-- products.csv
LOAD DATA LOCAL INFILE 'D:/Capstone Project/Raw Data/products.csv'
INTO TABLE products
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    product_id,
    product_name,
    category,
    price
);
