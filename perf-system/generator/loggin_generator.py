# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.
from generator import create_parquet, create_verb

MYHOST = "127.0.0.1:8000"
REQUEST_CONTENT_TYPE = "content-type: application/json"


for i in range(25):
    req_type = "HTTP/1.1"
    req_path = "/app/log/private"
    req_data = '{"id": ' + str(1000) + ', "msg": "Logged to private table"}'

    create_verb(
        "post",
        MYHOST,
        req_path,
        req_type,
        req_message=req_data,
        headers=[REQUEST_CONTENT_TYPE],
    )

for i in range(300):

    req_type = "HTTP/1.1"
    req_path = "/app/log/private?id=" + str(i % 1000)

    create_verb("GET", MYHOST, req_path, req_type, headers=[REQUEST_CONTENT_TYPE])

for i in range(25):

    req_type = "HTTP/1.1"
    req_path = "/app/log/private?id=" + str(i % 1000)

    create_verb("delete", MYHOST, req_path, req_type, headers=[REQUEST_CONTENT_TYPE])


create_parquet("new_mid_raw.parquet")
