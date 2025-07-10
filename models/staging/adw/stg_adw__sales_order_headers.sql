with
    source_sales_order_header_renamed as (
        select
            cast(salesorderid as int) as pk_sales_order
            , cast(customerid as int) as fk_customer
            , cast(salespersonid as int) as fk_salesperson
            , cast(territoryid as int) as fk_territory
            , cast(billtoaddressid as int) as fk_bill_to_address
            , cast(shiptoaddressid as int) as fk_ship_to_address
            , cast(shipmethodid as int) as fk_ship_method
            , cast(creditcardid as int) as fk_credit_card
            , cast(currencyrateid as int) as fk_currency_rate
            , cast(orderdate as date) as order_date
            , cast(duedate as date) as due_date
            , cast(shipdate as date) as ship_date
            , cast(subtotal as numeric(18, 2)) as subtotal
            , cast(taxamt as numeric(18, 2)) as tax_amount
            , cast(freight as numeric(18, 2)) as freight
            , cast(totaldue as numeric(18, 2)) as total_due
            , cast(revisionnumber as int) as revision_number
            , case status
                when 1 then 'Em Processo'
                when 2 then 'Aprovado'
                when 3 then 'Em espera'
                when 4 then 'Rejeitado'
                when 5 then 'Entregue'
                when 6 then 'Cancelado'
                else 'Desconhecido'
            end as status
            , cast(modifieddate as date) as date_modified
        from {{ source('raw_adventure_works', 'salesorderheader') }}
    )

select *
from source_sales_order_header_renamed
