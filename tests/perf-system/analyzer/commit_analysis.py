# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.

import analyzer

analysis = analyzer.Analyze()

df_generator = analyzer.get_df_from_parquet_file("../generator/new_raw.parquet")
df_sends = analyzer.get_df_from_parquet_file("../submitter/commit_send.parquet")
df_responses = analyzer.get_df_from_parquet_file("../submitter/commit_response.parquet")

# print(df_responses.iloc[len(df_responses) - 1]["rawResponse"])
# print(df_responses.iloc[len(df_responses) - 2]["rawResponse"])
# print(df_responses.iloc[0]["rawResponse"])

analysis.plot_commits(df_responses, df_generator)

# successful_percent = analysis.iter_for_success_and_latency(df_sends, df_responses)

# time_spent = analysis.total_time_in_sec(df_sends, df_responses)

# col_names = ["Reqs", "Time", "Pass", "Throughput"]
# rows = [
#     [
#         len(df_sends.index),
#         round(time_spent, 3),
#         round(successful_percent, 1),
#         round(len(df_sends.index) / time_spent, 1),
#     ]
# ]
# my_table = analysis.customize_table(col_names, rows)

# print(my_table)
# analysis.plot_throughput_per_block(df_responses, 0.1)

# analysis.plot_latency_distribution(0.1)
