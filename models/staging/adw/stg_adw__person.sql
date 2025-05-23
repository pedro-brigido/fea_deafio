with
    source_person_renamed as (
        select
            cast(businessentityid as int) as pk_business_entity
            , cast(persontype as string) as person_type
            , cast(firstname as string) as first_name
            , cast(middlename as string) as middle_name
            , cast(lastname as string) as last_name
            , cast(
                (coalesce(firstname, '_') || ' ' || coalesce(middlename, '_') || ' ' || coalesce(lastname, '_'))
                as string
                ) as full_name
        from {{ source('raw_adventure_works', 'person') }}
    )

select *
from source_person_renamed
