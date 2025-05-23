with
    source_store_renamed as (
        select
            cast (businessentityid as int) as pk_business_entity		
            , cast (name as string) as store_name
        from {{ source('raw_adventure_works','store')}}
    )

select *
from source_store_renamed