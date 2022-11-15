# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.
from generator import Messages

HOST = "127.0.0.1:8000"
REQUEST_CONTENT_TYPE = "content-type: application/json"


msgs = Messages()

# inputs = msgs.append(HOST, "/app/log/private/count", "GET")
for i in range(20):
    for i in range(500):
        msgs.append(
            HOST,
            "/app/log/private",
            "POST",
            data='{"id": '
            + str(i)
            + ', "msg": "Logged '
            + str(i)
            + ' to private table"}',
        )
    inputs = msgs.append(HOST, "/app/commit", "GET")


# for i in range(300000):
#     msgs.append(HOST, "/app/log/private?id=42", "GET")
# inputs = msgs.append(HOST, "/app/log/private/count", "GET")

# for i in range(1000):
#     msgs.append(HOST, "/app/log/private?id=" + str(i), "DELETE")
# inputs = msgs.append(HOST, "/app/log/private/count", "GET")


msgs.to_parquet_file("medium_commit.parquet")
