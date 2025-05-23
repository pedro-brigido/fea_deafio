with
    source_customer_renamed as (
        select
            cast(customerid as int) as pk_customer
            , cast(personid as int) as fk_person
            , cast(storeid as int) as fk_store
            , cast(territoryid as int) as fk_territory
            , cast(modifieddate as date) as modified_date
        from {{ source('raw_adventure_works', 'customer') }}
    )

select *
from source_customer_renamed
