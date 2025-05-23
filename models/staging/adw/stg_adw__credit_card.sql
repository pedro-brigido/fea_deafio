with
    source_credit_card_renamed as (
        select
            cast(creditcardid as int) pk_credit_card
            , cast(cardtype as string) card_type
            , cast(cardnumber as int) card_number
            , cast(expmonth as int) expiration_month
            , cast(expyear as int) expiration_year
            , cast(modifieddate as string) modified_date
        from {{ source('raw_adventure_works', 'creditcard') }}
    )

select *
from source_credit_card_renamed