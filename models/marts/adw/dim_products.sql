with
    stg_product as (
        select *
        from {{ ref('stg_adw__product') }}
    )

select
    pk_product
    , product_name
from stg_product