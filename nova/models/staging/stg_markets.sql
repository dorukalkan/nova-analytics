select *
from {{ source('raw', 'nova_markets') }}
