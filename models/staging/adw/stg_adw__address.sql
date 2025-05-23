with
    renamed_source_address as (
        select
            cast (addressid as int) as pk_address
            , cast (stateprovinceid as int) as fk_state_province
            , cast(addressline1 as string) as address_line1
            , cast(addressline2 as string) as address_line2
            , cast(postalcode as string) as postal_code
            , cast (city as string) as city
            , cast(modifieddate as datetime) as modified_date
        from {{ source('raw_adventure_works', 'address') }}
    )

select *
from renamed_source_address