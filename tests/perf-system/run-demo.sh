#!/bin/bash
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.

set -e

PERF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# shellcheck disable=SC2046
CCF_DIR=$(dirname $( dirname "$PERF_DIR" ))

BUILD_DIR="$CCF_DIR"/build

CHECK_DELIMITER="---------------------------"

echo -e "\n$CHECK_DELIMITER"
echo -e "-- Generating requests\n"
cd "$PERF_DIR"/generator
python3 demo_generator.py

echo -e "\n$CHECK_DELIMITER"
echo -e "-Run Submitter\n"
cd "$BUILD_DIR"
./submit \
--cert ./workspace/sandbox_common/user0_cert.pem \
--key ./workspace/sandbox_common/user0_privk.pem \
--cacert ./workspace/sandbox_common/service_cert.pem \
--generator-filepath ../tests/perf-system/generator/demo.parquet \
-s ../tests/perf-system/submitter/demo_send.parquet \
-r ../tests/perf-system/submitter/demo_response.parquet \
-m 1000

echo -e "\n$CHECK_DELIMITER"
echo -e "--Run analyzer\n"
cd "$PERF_DIR"/analyzer
python3 demo_analysis.py

echo -e "\n$CHECK_DELIMITER"
echo "Finished sample performance tool successfully"
