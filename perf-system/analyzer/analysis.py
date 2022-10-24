# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.
"""
Provide metrics based on the requests sent
"""

import argparse
import pandas as pd  # type: ignore

# pylint: disable=import-error
from prettytable import PrettyTable  # type: ignore
import numpy as np
import matplotlib.pyplot as plt  # type: ignore
from typing import List

latency_list = []
ms_latency_list = []
SEC_MS = 1000


def get_latency_list() -> list:
    return latency_list


def get_ms_latency_list() -> list:
    return ms_latency_list


def get_req_type(df_responses: pd.DataFrame) -> str:
    return df_responses.iloc[0]["rawResponse"].split(" ")[0]


def get_latency_at_i(df_sends, df_responses, req_id):
    # will need to handle the re-submission response from submitter when decided
    return df_responses.iloc[req_id]["receiveTime"] - df_sends.iloc[req_id]["sendTime"]


def check_success(df_responses, req_id) -> int:
    req_resp = df_responses.iloc[req_id]["rawResponse"].split("\n")
    status_list = req_resp[0].split(" ")
    # if we get a full statues and says ok increase the successful
    if len(status_list) > 1 and status_list[1][:3] == "200":
        return 1
    return 0


def iter_for_success_and_latency(df_sends, df_responses) -> float:
    successful_reqs = 0

    for i in range(len(df_sends.index)):
        successful_reqs += check_success(df_responses, i)

        latency_i = get_latency_at_i(df_sends, df_responses, i)
        latency_list.append(latency_i)
        ms_latency_list.append(latency_i * SEC_MS)

    return successful_reqs / len(df_sends.index) * 100


def total_time_in_sec(df_sends, df_responses):
    # time_spent is: last timestamp of responses - first timestamp of sends
    return df_responses.iloc[-1]["receiveTime"] - df_sends.iloc[0]["sendTime"]


def sec_to_ms(time_in_sec):
    return time_in_sec / SEC_MS


def time_success_thoughput_table(df_sends, df_responses, successful_percent):
    generic_output_table = PrettyTable()

    generic_output_table.field_names = [
        "Total Requests",
        "Total Time (s)",
        "Pass (%)",
        "Fail (%)",
        "Throughput (req/s)",
    ]

    time_spent = total_time_in_sec(df_sends, df_responses)
    ms_time_spent_sum = sec_to_ms(time_spent)

    generic_output_table.add_row(
        [
            len(df_sends.index),
            round(ms_time_spent_sum / 1000, 3),
            round(successful_percent, 1),
            round(100 - successful_percent, 1),
            round(len(df_sends.index) / time_spent, 1),
        ]
    )
    return generic_output_table


def latencies_table(df_sends, df_responses):
    ms_time_spent_sum = total_time_in_sec(df_sends, df_responses) * SEC_MS
    latency_output_table = PrettyTable()
    latency_output_table.field_names = [
        "Latency (ms)",
        "Average Latency (ms)",
        "Latency 80th (ms)",
        "Latency 90th (ms)",
        "Latency 95th (ms)",
        "Latency 99th (ms)",
        "Latency 99.9th (ms)",
    ]
    latency_output_table.add_row(
        [
            round(np.percentile(ms_latency_list, 50), 3),
            round(ms_time_spent_sum / len(df_sends.index), 3),
            round(np.percentile(ms_latency_list, 80), 3),
            round(np.percentile(ms_latency_list, 90), 3),
            round(np.percentile(ms_latency_list, 95), 3),
            round(np.percentile(ms_latency_list, 99), 3),
            round(np.percentile(ms_latency_list, 99.9), 3),
        ]
    )
    return latency_output_table


def customize_table(fields_list, values_list: List[List]):
    custom_table = PrettyTable()
    custom_table.field_names = fields_list
    for val_row in values_list:
        custom_table.add_row(val_row)
    return custom_table


def make_analysis(send_file, response_file):
    """
    Produce the analysis results
    """
    df_sends = pd.read_parquet(send_file, engine="fastparquet")
    df_responses = pd.read_parquet(response_file, engine="fastparquet")

    successful_percent = iter_for_success_and_latency(df_sends, df_responses)

    print("The request type sent is ", get_req_type(df_responses))

    print(time_success_thoughput_table(df_sends, df_responses, successful_percent))
    print(latencies_table(df_sends, df_responses))

    x = ["-"] * 20
    print("\n", "".join(x), " Start plotting  ", "".join(x))
    time_unit = [
        x - df_responses["receiveTime"][0] + 1 for x in df_responses["receiveTime"]
    ]

    id_unit = [x for x in range(0, len(df_sends.index))]
    lat_unit = ms_latency_list

    # sort the latencies as it make sense to get the throughput
    # by time unit ignoring the ids
    sorted_latencies = sorted(df_responses["receiveTime"].tolist())
    idxes_100ms = [0]
    for i, lat in enumerate(sorted_latencies):
        if lat > sorted_latencies[idxes_100ms[-1]] + 0.1:
            idxes_100ms.append(i)

    req_per_100ms = []
    time_in_100ms_parts = []
    if len(idxes_100ms) > 1:
        for i in range(len(idxes_100ms) - 1):
            req_per_100ms.append(idxes_100ms[i + 1] - idxes_100ms[i])
            time_in_100ms_parts.append(100 * (i + 1))
        req_per_100ms.append(len(sorted_latencies) - 1 - idxes_100ms[-1])
        time_in_100ms_parts.append(
            time_in_100ms_parts[-1]
            + int((sorted_latencies[-1] - sorted_latencies[idxes_100ms[-1]]) * 1000)
        )
    throughput_per_100ms = [
        x * 10 for x in req_per_100ms
    ]  # x*10 because is 0.1s per input

    # plot latency with ids
    plt.figure(1)
    plt.scatter(id_unit, lat_unit, s=1)
    plt.ylabel("Latency_ms")
    plt.xlabel("ids")
    plt.savefig("latency_per_id.png")
    plt.figure(figsize=(15, 15), dpi=80)
    # plot latency with time
    plt.figure(2)
    plt.scatter(time_unit, ms_latency_list, s=1)
    plt.ylabel("Latency(ms)")
    plt.xlabel("time(s)")
    plt.savefig("latency_across_time.png")
    plt.figure(figsize=(15, 15), dpi=80)

    # plot throughput with time
    plt.figure(3)
    plt.plot(time_in_100ms_parts, throughput_per_100ms)
    plt.ylabel("Throughput(req/s)")
    plt.xlabel("time(ms)")
    plt.savefig("throughput_across_time.png")

    print("\n", "".join(x), "Finished plotting", "".join(x))


def main():
    """
    The function to receive the arguments
    from the command line
    """
    arg_send_file = "../submitter/cpp_send.parquet"
    arg_response_file = "../submitter/cpp_respond.parquet"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-sf",
        "--send_file",
        help="Path to the parquet file that contains the submitted\
            requests. Default location `../submitter/sends.parquet`",
        type=str,
    )
    parser.add_argument(
        "-rf",
        "--response_file",
        help="Path to the parquet file that contains the responses\
            from the submitted requests. Default `../submitter/receives.parquet`",
        type=str,
    )

    args = parser.parse_args()
    make_analysis(
        args.send_file or arg_send_file, args.response_file or arg_response_file
    )


if __name__ == "__main__":
    main()
