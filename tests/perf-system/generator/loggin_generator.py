# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.
from generator import Messages

HOST = "127.0.0.1:8000"
REQUEST_CONTENT_TYPE = "content-type: application/json"


msgs = Messages()

for i in range(100):
    msgs.append(
        HOST,
        "/app/log/private",
        "POST",
        data='{"id": ' + str(i) + ', "msg": "Logged ' + str(i) + ' to private table"}',
    )

msgs.append(HOST, "/app/log/private?id=1", "GET", iterations=1000)


msgs.to_parquet_file("demo.parquet")
