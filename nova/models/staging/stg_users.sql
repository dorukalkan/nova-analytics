select *
from {{ source('raw', 'nova_users') }}
