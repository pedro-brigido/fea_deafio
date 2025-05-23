with
    stg_customer as (
        select *
        from {{ ref('stg_adw__customer') }}
    )

    , stg_person as (
        select *
        from {{ ref('stg_adw__person') }}
    )

    , stg_employee as (
        select *
        from {{ ref('stg_adw__employee') }}
    )

    , stg_sales_person as (
        select *
        from {{ ref('stg_adw__sales_person') }}
    )

    , stg_store as (
        select *
        from {{ ref('stg_adw__store') }}
    )

    , joined_customer as (
        select
            stg_customer.pk_customer
            , stg_customer.fk_person
            , stg_customer.fk_store
            , stg_person.full_name as customer_full_name
            , stg_store.store_name
        from stg_customer
        left join stg_person
            on stg_customer.fk_person = stg_person.pk_business_entity
        left join stg_store
            on stg_customer.fk_store = stg_store.pk_business_entity
    )

select *
from joined_customer