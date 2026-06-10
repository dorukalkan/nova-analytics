select *
from {{ source('raw', 'nova_services') }}
