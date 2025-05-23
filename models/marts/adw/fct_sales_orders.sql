with
    stg_sales_order_header as (
        select *
        from {{ ref('stg_adw__sales_order_header') }}
    )

    , stg_sales_order_detail as (
        select *
        from {{ ref('stg_adw__sales_order_detail') }}
    )

    , enriched_sales_order as (
        select
            stg_sales_order_header.pk_sales_order
            , stg_sales_order_header.fk_customer
            , stg_sales_order_detail.fk_product
            , stg_sales_order_header.fk_salesperson
            , stg_sales_order_header.fk_territory
            , stg_sales_order_header.fk_bill_to_address
            , stg_sales_order_header.fk_ship_to_address
            , stg_sales_order_header.fk_ship_method
            , stg_sales_order_header.fk_credit_card
            , stg_sales_order_header.fk_currency_rate
            , stg_sales_order_header.order_date
            , stg_sales_order_header.due_date
            , stg_sales_order_header.ship_date
            , stg_sales_order_header.subtotal
            , stg_sales_order_header.tax_amount
            , stg_sales_order_header.freight
            , stg_sales_order_header.total_due
            , stg_sales_order_header.revision_number
            , stg_sales_order_header.status
            , stg_sales_order_detail.order_quantity
            , stg_sales_order_detail.unit_price
            , stg_sales_order_detail.unit_price_discount
        from stg_sales_order_header
        left join stg_sales_order_detail
            on stg_sales_order_header.pk_sales_order = stg_sales_order_detail.fk_sales_order
    )

select * 
from enriched_sales_order
