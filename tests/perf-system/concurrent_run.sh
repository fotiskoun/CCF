#!/binbash
PERF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# shellcheck disable=SC2046
CCF_DIR=$(dirname $( dirname "$PERF_DIR" ))

BUILD_DIR="$CCF_DIR"/build
cd "$BUILD_DIR"
./submit -c ./workspace/sandbox_common/user0_cert.pem -k ./workspace/sandbox_common/user0_privk.pem --cacert ./workspace/sandbox_common/service_cert.pem --generator-filepath ../tests/perf-system/generator/new_100k_raw.parquet --response-filepath "../tests/perf-system/submitter/cpp_respond.parquet" --send-filepath "../tests/perf-system/submitter/cpp_send.parquet" -m 1000 &
P1=$!
./submit -c ./workspace/sandbox_common/user0_cert.pem -k ./workspace/sandbox_common/user0_privk.pem --cacert ./workspace/sandbox_common/service_cert.pem --generator-filepath ../tests/perf-system/generator/new_100k_raw.parquet --response-filepath "../tests/perf-system/submitter/cpp_respond2.parquet" --send-filepath "../tests/perf-system/submitter/cpp_send2.parquet" -m 1000 &
P2=$!
wait $P1 $P2
