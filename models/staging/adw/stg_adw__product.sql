with
    source_product_renamed as (
        select
            cast(productid as int) as pk_product
            , cast(productsubcategoryid as int) as fk_product_subcategory
            , cast(productmodelid as int) as fk_product_model
            , cast(standardcost as numeric(18, 2)) as standard_cost
            , cast(listprice as numeric(18, 2)) as list_price
            , cast(name as string) as product_name
            , cast(productnumber as string) as product_number
            , cast(sellstartdate as datetime) as sell_start_date
            , cast(sellenddate as datetime) as sell_end_date
            , cast(modifieddate as datetime) as modified_date
        from {{ source('raw_adventure_works', 'product') }}
    )

select *
from source_product_renamed