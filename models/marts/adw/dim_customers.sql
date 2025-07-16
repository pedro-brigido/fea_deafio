with
    stg_customers as (
        select *
        from {{ ref('stg_adw__customers') }}
    )

    , stg_people as (
        select *
        from {{ ref('stg_adw__people') }}
    )

    , stg_stores as (
        select *
        from {{ ref('stg_adw__stores') }}
    )

    , joined_customer as (
        select
            stg_customers.pk_customer
            , stg_customers.fk_person
            , stg_customers.fk_store
            , stg_people.full_name as customer_full_name
            , stg_stores.store_name
        from stg_customers
        left join stg_people
            on stg_customers.fk_person = stg_people.pk_business_entity
        left join stg_stores
            on stg_customers.fk_store = stg_stores.pk_business_entity
    )

select *
from joined_customer
