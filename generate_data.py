import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2

# Connect to the PostgreSQL database created via Docker
conn = psycopg2.connect(
    host="localhost",
    database="ecommerce_source",
    user="postgres",
    password="password123",
    port=5432,
)
cursor = conn.cursor()

# Create source tables
cursor.execute("""
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (user_id SERIAL PRIMARY KEY, name VARCHAR(100), email VARCHAR(150), country VARCHAR(100), created_at TIMESTAMP);

CREATE TABLE products (product_id SERIAL PRIMARY KEY, product_name VARCHAR(100), category VARCHAR(50), price NUMERIC(10, 2));

CREATE TABLE orders (order_id SERIAL PRIMARY KEY, user_id INT REFERENCES users(user_id), order_date TIMESTAMP, status VARCHAR(20));

CREATE TABLE order_items (order_item_id SERIAL PRIMARY KEY, order_id INT REFERENCES orders(order_id), product_id INT REFERENCES products(product_id), quantity INT, unit_price NUMERIC(10, 2));
""")
conn.commit()
print("Successfully created tables in PostgreSQL!")

fake = Faker()

# 1. Generate User data (500 users)
users = []
for _ in range(500):
    users.append(
        (
            fake.name(),
            fake.email(),
            fake.country(),
            fake.date_time_between(start_date="-1y", end_date="now"),
        )
    )
cursor.executemany(
    "INSERT INTO users (name, email, country, created_at) VALUES (%s, %s, %s, %s)",
    users,
)
conn.commit()

# 2. Generate Product data (50 products)
categories = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Sports"]
products = []
for _ in range(50):
    products.append(
        (
            fake.word().capitalize() + " " + random.choice(["Pro", "Max", "Basic", ""]),
            random.choice(categories),
            round(random.uniform(10.0, 500.0), 2),
        )
    )
cursor.executemany(
    "INSERT INTO products (product_name, category, price) VALUES (%s, %s, %s)",
    products,
)
conn.commit()

# Fetch ID lists to generate orders
cursor.execute("SELECT user_id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT product_id, price FROM products")
products_info = cursor.fetchall()

# 3. Generate Orders & Order Items data (2000 orders)
statuses = ["Completed", "Cancelled", "Pending", "Shipped"]
for _ in range(2000):
    u_id = random.choice(user_ids)
    o_date = fake.date_time_between(start_date="-6m", end_date="now")
    status = random.choices(statuses, weights=[70, 10, 5, 15], k=1)[0]

    cursor.execute(
        "INSERT INTO orders (user_id, order_date, status) VALUES (%s, %s, %s) RETURNING order_id",
        (u_id, o_date, status),
    )
    order_id = cursor.fetchone()[0]

    num_items = random.randint(1, 4)
    chosen_products = random.sample(products_info, num_items)

    for prod in chosen_products:
        p_id, p_price = prod[0], prod[1]
        qty = random.randint(1, 3)
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
            (order_id, p_id, qty, p_price),
        )

conn.commit()
cursor.close()
conn.close()
print("Successfully generated mock data into the source database!")
