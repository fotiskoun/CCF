# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.

import pandas as pd  # type: ignore

# pylint: disable=import-error
from prettytable import PrettyTable  # type: ignore
import numpy as np
import matplotlib.pyplot as plt  # type: ignore
from typing import List
import sys
from loguru import logger as LOG

SEC_MS = 1000

request_objects = []  # type: List[Requests]

# Change default log format
LOG.remove()
LOG.add(
    sys.stdout,
    format="<green>[{time:HH:mm:ss.SSS}]</green> {message}",
)


def indexOf(list_to_check: List, value) -> int:
    """
    If the value is in the list return index
    else return -1
    """
    if value in list_to_check:
        return list_to_check.index(value)
    else:
        return -1


def split_dfs_per_verb(
    df_sends: pd.DataFrame, df_responses: pd.DataFrame, df_generated: pd.DataFrame
):
    gen_dfs = []
    sends_dfs = []
    resp_dfs = []
    verbs = []
    for ind in range(len(df_generated)):
        req_verb = get_req_verb(df_generated, ind)
        i = indexOf(verbs, req_verb)
        if i < 0:
            gen_dfs.append(
                pd.DataFrame(
                    columns=df_generated.columns, data=[df_generated.iloc[ind].values]
                )
            )
            sends_dfs.append(
                pd.DataFrame(columns=df_sends.columns, data=[df_sends.iloc[ind].values])
            )
            resp_dfs.append(
                pd.DataFrame(
                    columns=df_responses.columns, data=[df_responses.iloc[ind].values]
                )
            )
            verbs.append(req_verb)
        else:
            gen_dfs[i].loc[len(gen_dfs[i])] = df_generated.iloc[ind].values
            sends_dfs[i].loc[len(sends_dfs[i])] = df_sends.iloc[ind].values
            resp_dfs[i].loc[len(resp_dfs[i])] = df_responses.iloc[ind].values
    return [verbs, gen_dfs, sends_dfs, resp_dfs]


class Requests:
    def __init__(
        self,
        req_verb: str,
        df_gen: pd.DataFrame,
        df_send: pd.DataFrame,
        df_resp: pd.DataFrame,
    ):
        self.latency_list = []
        self.ms_latency_list = []
        self.verb = req_verb
        self.total_requests = 0
        self.successful_requests = 0
        self.generator_df = df_gen
        self.send_df = df_send
        self.responses_df = df_resp
        self.success = 0

    def get_latency_list(self) -> List:
        return self.latency_list

    def get_ms_latency_list(self) -> List:
        return self.ms_latency_list

    def iter_for_success_and_latency(self) -> float:
        successful_reqs = 0

        for i in range(len(self.send_df.index)):
            successful_reqs += check_success(self.responses_df, i)

            latency_i = get_latency_at_i(self.send_df, self.responses_df, i)
            self.latency_list.append(latency_i)
            self.ms_latency_list.append(latency_i * SEC_MS)

        self.success = successful_reqs / len(self.send_df.index) * 100
        return self.success


def get_req_type(df_responses: pd.DataFrame) -> str:
    return df_responses.iloc[0]["rawResponse"].split(" ")[0]


def get_req_verb(df_generated: pd.DataFrame, row: int) -> str:
    return df_generated.iloc[row]["request"].split(" ")[0]


def get_latency_at_i(df_sends: pd.DataFrame, df_responses: pd.DataFrame, req_id: int):
    # will need to handle the re-submission response from submitter when decided
    return df_responses.iloc[req_id]["receiveTime"] - df_sends.iloc[req_id]["sendTime"]


def check_success(df_responses: pd.DataFrame, req_id: int) -> int:
    req_resp = df_responses.iloc[req_id]["rawResponse"].split("\n")
    status_list = req_resp[0].split(" ")
    # if we get a full status and says ok increase the successful
    if len(status_list) > 1 and status_list[1][:3] == "200":
        return 1
    return 0


def total_time_in_sec(df_sends: pd.DataFrame, df_responses: pd.DataFrame):
    # time_spent is: last timestamp of responses - first timestamp of sends
    return df_responses.iloc[-1]["receiveTime"] - df_sends.iloc[0]["sendTime"]


def sec_to_ms(time_in_sec: float) -> float:
    return time_in_sec / SEC_MS


def time_success_throughput_table(request_obj: Requests) -> PrettyTable:
    generic_output_table = PrettyTable()

    generic_output_table.field_names = [
        "Total Requests",
        "Total Time (s)",
        "Pass (%)",
        "Fail (%)",
        "Throughput (req/s)",
    ]

    time_spent = total_time_in_sec(request_obj.send_df, request_obj.responses_df)

    generic_output_table.add_row(
        [
            len(request_obj.send_df.index),
            round(time_spent, 3),
            round(request_obj.success, 1),
            round(100 - request_obj.success, 1),
            round(len(request_obj.send_df.index) / time_spent, 1),
        ]
    )
    return generic_output_table


def latencies_table(request_object: Requests) -> PrettyTable:
    ms_time_spent_sum = (
        total_time_in_sec(request_object.send_df, request_object.responses_df) * SEC_MS
    )
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
            round(np.percentile(request_object.ms_latency_list, 50), 3),
            round(ms_time_spent_sum / len(request_object.send_df.index), 3),
            round(np.percentile(request_object.ms_latency_list, 80), 3),
            round(np.percentile(request_object.ms_latency_list, 90), 3),
            round(np.percentile(request_object.ms_latency_list, 95), 3),
            round(np.percentile(request_object.ms_latency_list, 99), 3),
            round(np.percentile(request_object.ms_latency_list, 99.9), 3),
        ]
    )
    return latency_output_table


def customize_table(fields_list: List[str], values_list: List[List]):
    custom_table = PrettyTable()
    custom_table.field_names = fields_list
    for val_row in values_list:
        custom_table.add_row(val_row)
    return custom_table


def plot_latency_by_id(request_object: Requests) -> None:
    id_unit = [x for x in range(0, len(request_object.send_df.index))]
    lat_unit = request_object.ms_latency_list
    plt.figure()
    plt.scatter(id_unit, lat_unit, s=1)
    plt.ylabel("Latency_ms")
    plt.xlabel("ids")
    plt.savefig("latency_per_id.png")
    plt.figure(figsize=(15, 15), dpi=80)


def plot_latency_across_time(request_object: Requests) -> None:
    time_unit = [
        x - request_object.responses_df["receiveTime"][0] + 1
        for x in request_object.responses_df["receiveTime"]
    ]
    plt.figure()
    plt.scatter(time_unit, request_object.ms_latency_list, s=1)
    plt.ylabel("Latency(ms)")
    plt.xlabel("time(s)")
    plt.savefig("latency_across_time.png")
    plt.figure(figsize=(15, 15), dpi=80)


def plot_throughput_per_block(df_responses: pd.DataFrame, time_block: float) -> None:
    """
    It splits the dataset in buckets of time_block seconds difference
    and will plot the throughput for each bucket
    """
    # sort the latencies as it make sense to get the throughput
    # by time unit ignoring the ids
    sorted_latencies = sorted(df_responses["receiveTime"].tolist())
    block_indexes = [0]
    for i, lat in enumerate(sorted_latencies):
        if lat > sorted_latencies[block_indexes[-1]] + time_block:
            block_indexes.append(i)
    req_per_block = []
    block_latency = []
    if len(block_indexes) > 1:
        for i in range(len(block_indexes) - 1):
            req_per_block.append(block_indexes[i + 1] - block_indexes[i])
            block_latency.append(time_block * SEC_MS * (i + 1))
        req_per_block.append(len(sorted_latencies) - 1 - block_indexes[-1])
        block_latency.append(
            block_latency[-1]
            + int((sorted_latencies[-1] - sorted_latencies[block_indexes[-1]]) * SEC_MS)
        )
    throughput_per_block = [
        x / time_block for x in req_per_block
    ]  # x/time_block comes from rule of three
    plt.figure()
    plt.plot(block_latency, throughput_per_block)
    plt.ylabel("Throughput(req/s)")
    plt.xlabel("time(ms)")
    plt.savefig("throughput_across_time.png")


def get_df_from_parquet_file(input_file: str):
    return pd.read_parquet(input_file, engine="fastparquet")


def plot_latency_distribution(
    request_object: Requests, ms_separator: float, highest_vals=15
):
    """
    Starting from minimum latency with ms_separator
    step split the ms latency list in buckets
    and plots the highest_vals top buckets
    """
    max_latency = max(request_object.ms_latency_list)
    min_latency = min(request_object.ms_latency_list)

    if max_latency < ms_separator:
        LOG.remove()
        LOG.add(
            sys.stdout,
            format="<red>[ERROR]:</red> {message}",
        )

        LOG.error(
            f"Latency values are less than {ms_separator}, cannot produce latency distribution graph"
        )
        return

    bins_number = (
        int(
            (max_latency - min_latency) // ms_separator
            + bool((max_latency - min_latency) % ms_separator)
        )
        + 1
    )

    counts = [0] * bins_number
    bins = [min_latency]
    bin_val = min_latency
    for _ in range(bins_number):
        bin_val += ms_separator
        bins.append(bin_val)

    for lat in request_object.ms_latency_list:
        counts[
            int(
                (lat - min_latency) // ms_separator
                + bool((lat - min_latency) % ms_separator)
            )
        ] += 1

    top_bins = []
    top_counts = []
    min_count = sorted(counts)[-highest_vals]
    for ind in range(len(counts)):
        if counts[ind] >= min_count:
            top_bins.append(round(bins[ind], 3))
            top_counts.append(counts[ind])

    x_axis = range(len(top_bins))
    plt.figure()
    fig, ax = plt.subplots()
    ax.bar(x_axis, top_counts, 0.9, align="center")
    ax.set_xticks(x_axis)
    ax.set_xticklabels(top_bins, rotation=25)
    plt.ylabel("Count")
    plt.xlabel("Latency")
    fig.subplots_adjust(bottom=0.2)
    plt.savefig("latency_distribution.png")


def default_analysis(send_file, response_file, generator_file):
    """
    Produce the analysis results
    """

    df_generated = get_df_from_parquet_file(generator_file)
    df_sends = get_df_from_parquet_file(send_file)
    df_responses = get_df_from_parquet_file(response_file)
    df_list = split_dfs_per_verb(df_sends, df_responses, df_generated)

    req_objs = [
        Requests(df_list[0][x], df_list[1][x], df_list[2][x], df_list[3][x])
        for x in range(len(df_list[0]))
    ]

    successful_percent = req_objs[1].iter_for_success_and_latency()
    print(successful_percent)

    LOG.info(f"The request verb is {req_objs[1].verb}")
    LOG.info(f"The request type sent is {get_req_type(req_objs[1].responses_df)}")

    # print(time_success_throughput_table(req_objs[1]))
    # print(latencies_table(req_objs[1]))

    # x = ["-"] * 20
    # LOG.info(f'{"".join(x)} Start plotting  {"".join(x)}')

    # plot_latency_by_id(df_sends)
    # plot_latency_across_time(df_responses)
    # plot_throughput_per_block(df_responses, 0.1)

    # LOG.info(f'{"".join(x)}Finished plotting{"".join(x)}')
