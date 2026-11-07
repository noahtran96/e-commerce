import duckdb

conn = duckdb.connect("ecommerce.duckdb")

version = conn.execute("SELECT version()").fetchone()[0]
print(f"Successfully created DuckDB! Version: {version}")

conn.close()
