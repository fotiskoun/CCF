# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.
from generator import Messages

HOST = "127.0.0.1:8000"


msgs = Messages()

inputs = msgs.append(HOST, "/app/log/private?id=42", "GET", iterations=5000)


msgs.to_parquet_file("demo.parquet")
