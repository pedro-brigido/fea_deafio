with
    stg_credit_card as (
        select *
        from {{ ref('stg_adw__credit_card') }}
    )

select
    pk_credit_card
    , card_type
from stg_credit_card