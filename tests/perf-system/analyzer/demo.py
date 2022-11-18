# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.

import analyzer


df_sends = analyzer.get_df_from_parquet_file("../submitter/demo_send.parquet")
df_responses = analyzer.get_df_from_parquet_file("../submitter/demo_response.parquet")

analysis = analyzer.Analyze()

success = analysis.iter_for_success_and_latency(df_sends, df_responses)

time_spent = analysis.total_time_in_sec(df_sends, df_responses)

print(analysis.time_success_throughput_table(df_sends, df_responses, success))
analysis.plot_throughput_per_block(df_responses, 0.01)
