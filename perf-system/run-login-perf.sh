#!/bin/bash
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.

set -e

PERF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

CCF_DIR=$( dirname "$PERF_DIR" )

BUILD_DIR="$CCF_DIR"/build

CHECK_DELIMITER="---------------------------"

echo -e "\n$CHECK_DELIMITER"
echo -e "-- Generating requests\n"
cd "$PERF_DIR"/generator
python3 loggin_generator.py

echo -e "\n$CHECK_DELIMITER"
echo -e "-Run Submitter\n"
cd "$BUILD_DIR"
./submit -c ./workspace/sandbox_common/user0_cert.pem -k ./workspace/sandbox_common/user0_privk.pem -ca ./workspace/sandbox_common/service_cert.pem -gf ../perf-system/generator/new_raw.parquet

echo -e "\n$CHECK_DELIMITER"
echo -e "--Run analyzer\n"
cd "$PERF_DIR"/analyzer
python3 analyze_packages.py

echo -e "\n$CHECK_DELIMITER"
echo "Finished sample performance tool successfully"