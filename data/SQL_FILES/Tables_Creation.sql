-- CREATE SCHEMA bikestore2;

-- CREATE THIS FIRST

 -- Order of data insertion needs to be ->  order_items
CREATE TABLE customers
(
	customer_id		INT NOT NULL,
    first_name 		VARCHAR(30),
    last_name		VARCHAR(30),
    phone 			VARCHAR(15),
    email			VARCHAR(30),
	street			VARCHAR(30),
	city 			VARCHAR(40),
	state			ENUM ('AL', 'AK', 'AZ', 'AR', 'CA',
							'CO', 'CT', 'DE', 'FL', 'GA',
							'HI', 'ID', 'IL', 'IN', 'IA',
							'KS', 'KY', 'LA', 'ME', 'MD',
							'MA', 'MI', 'MN', 'MS', 'MO',
							'MT', 'NE', 'NV', 'NH', 'NJ',
							'NM', 'NY', 'NC', 'ND', 'OH',
							'OK', 'OR', 'PA', 'RI', 'SC',
							'SD', 'TN', 'TX', 'UT', 'VT',
							'VA', 'WA', 'WV', 'WI', 'WY'),
	zipcode			INT,
    PRIMARY KEY (customer_id)
);

CREATE TABLE stores(
	store_id	INT NOT NULL,
    store_name 	VARCHAR(50),
    phone		VARCHAR(30),
    email		VARCHAR(30),
    street		VARCHAR(30),
    city		VARCHAR(30),
	state		ENUM ('AL', 'AK', 'AZ', 'AR', 'CA',
						'CO', 'CT', 'DE', 'FL', 'GA',
						'HI', 'ID', 'IL', 'IN', 'IA',
						'KS', 'KY', 'LA', 'ME', 'MD',
						'MA', 'MI', 'MN', 'MS', 'MO',
						'MT', 'NE', 'NV', 'NH', 'NJ',
						'NM', 'NY', 'NC', 'ND', 'OH',
						'OK', 'OR', 'PA', 'RI', 'SC',
						'SD', 'TN', 'TX', 'UT', 'VT',
						'VA', 'WA', 'WV', 'WI', 'WY'),
	zip_code	INT,
    PRIMARY KEY (store_id)
);

CREATE TABLE staffs (
	staff_id 	INT NOT NULL,
    first_name 	VARCHAR(30),
    last_name 	VARCHAR(30),
    email		VARCHAR(30),
    phone		VARCHAR(15),
    active		TINYINT,
    store_id	INT NOT NULL,
    manager_id	INT NOT NULL,
	
    PRIMARY KEY(staff_id),
    FOREIGN KEY store_id(store_id)
		REFERENCES stores(store_id)
);

CREATE TABLE orders (
	order_id 		INT NOT NULL,
	customer_id		INT NOT NULL,
    order_status	TINYINT,
    order_date 		DATE,
    required_date 	DATE,
    shipped_date	DATE,
    store_id		INT NOT NULL,
	staff_id		INT NOT NULL,
    
     FOREIGN KEY customer_id(customer_id)
		REFERENCES customers(customer_id),
    FOREIGN KEY store_id(store_id)
		REFERENCES stores(store_id),
	FOREIGN KEY staff_id(staff_id)
		REFERENCES staffs(staff_id),
    PRIMARY KEY (order_id)
);


CREATE TABLE categories (
	category_id		INT NOT NULL,
	category_name	VARCHAR(50),
    PRIMARY KEY (category_id)
);

CREATE TABLE brands (
	brand_id	INT NOT NULL,
	brand_name	VARCHAR(50),
    
    PRIMARY KEY (brand_id)
);

CREATE TABLE products (
	product_id		INT NOT NULL,
    product_name	VARCHAR(50),
    brand_id		INT NOT NULL,
	category_id		INT NOT NULL,
    model_year 		YEAR,
    list_price		FLOAT,
    
    PRIMARY KEY (product_id),
    FOREIGN KEY brand_id(brand_id)
		REFERENCES brands(brand_id),
	FOREIGN KEY category_id(category_id)
		REFERENCES categories(category_id)
);

CREATE TABLE stocks (
	store_id	INT NOT NULL,
	product_id	INT NOT NULL,
    quantity	INT,
    
    PRIMARY KEY (store_id, product_id),
    FOREIGN KEY store_id(store_id)
		REFERENCES stores(store_id),
	FOREIGN KEY product_id(product_id)
		REFERENCES products(product_id)
);

CREATE TABLE order_items (
	order_id	INT NOT NULL,
    item_id		INT NOT NULL,
    product_id	INT NOT NULL,
    quantity	INT,
    list_price	FLOAT,
    discount	FLOAT,
    
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY order_id(order_id)
		REFERENCES orders(order_id),
	FOREIGN KEY product_id(product_id)
		REFERENCES products(product_id)
);