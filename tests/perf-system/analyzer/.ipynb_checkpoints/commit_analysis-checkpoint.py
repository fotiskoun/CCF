# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.

import analyzer

analysis = analyzer.Analyze()

df_generator = analyzer.get_df_from_parquet_file(
    "../generator/small_commit_raw.parquet"
)
df_sends = analyzer.get_df_from_parquet_file("../submitter/small_commit_send.parquet")
df_responses = analyzer.get_df_from_parquet_file(
    "../submitter/small_commit_response.parquet"
)


analysis.plot_commits(df_responses, df_generator)
