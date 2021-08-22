{{ config(schema="TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'ID' || '~' ||
        'CURRENCY' || '~' ||
        {{QUOTE('DATE')}} || '~' ||
        'TIMESTAMP_COL' || '~' ||
        'HKD_SPECIAL___CHARACTERS' || '~' ||
        'HKD_SPECIAL___CHARACTERS_1' || '~' ||
        'NZD' || '~' ||
        'USD'
    ) as {{ QUOTE('_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID') }},
    tmp.*
from {{ ref('DEDUP_EXCHANGE_RATE_AB2') }} tmp
-- DEDUP_EXCHANGE_RATE

