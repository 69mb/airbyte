

  create or replace table `dataline-integration-testing`.test_normalization.`unnest_alias_children_owner`
  
  
  OPTIONS()
  as (
    
with __dbt__CTE__unnest_alias_children_owner_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_children_hashid,
    json_extract_scalar(owner, "$['owner_id']") as owner_id,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization.`unnest_alias_children` as table_alias
where owner is not null
-- owner at unnest_alias/children/owner
),  __dbt__CTE__unnest_alias_children_owner_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_children_hashid,
    cast(owner_id as 
    int64
) as owner_id,
    _airbyte_emitted_at
from __dbt__CTE__unnest_alias_children_owner_ab1
-- owner at unnest_alias/children/owner
),  __dbt__CTE__unnest_alias_children_owner_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_children_hashid as 
    string
), ''), '-', coalesce(cast(owner_id as 
    string
), '')) as 
    string
))) as _airbyte_owner_hashid
from __dbt__CTE__unnest_alias_children_owner_ab2
-- owner at unnest_alias/children/owner
)-- Final base SQL model
select
    _airbyte_children_hashid,
    owner_id,
    _airbyte_emitted_at,
    _airbyte_owner_hashid
from __dbt__CTE__unnest_alias_children_owner_ab3
-- owner at unnest_alias/children/owner from `dataline-integration-testing`.test_normalization.`unnest_alias_children`
  );
    