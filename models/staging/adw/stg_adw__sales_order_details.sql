with
    source_sales_order_detail_renamed as (
        select
            cast(salesorderdetailid as int) as pk_sales_order_detail
            , cast(salesorderid as int) as fk_sales_order
            , cast(productid as int) as fk_product
            , cast(specialofferid as int) as fk_special_offer
            , cast(orderqty as int) as order_quantity
            , cast(unitprice as numeric(18, 4)) as unit_price
            , cast(unitpricediscount as numeric(18, 4)) as unit_price_discount
            , cast(modifieddate as datetime) as modified_date
        from {{ source('raw_adventure_works', 'salesorderdetail') }}
    )

select *
from source_sales_order_detail_renamed
