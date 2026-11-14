-- Bronze staging model for raw products from PostgreSQL OLTP
{{
  config(
    pre_hook="INSTALL postgres; LOAD postgres; ATTACH IF NOT EXISTS 'host=localhost port=5432 dbname=ecommerce_source user=postgres password=password123' AS pg_oltp (TYPE postgres, READ_ONLY);"
  )
}}
with source_products as (
  select *
  from pg_oltp.public.products
)

select
  *,
  current_timestamp as _ingested_at
from source_products