# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.

import analyzer

analysis = analyzer.Analyze()

df_generator = analyzer.get_df_from_parquet_file(
    "../generator/posts_commits_100x1000.parquet"
)
df_sends = analyzer.get_df_from_parquet_file(
    "../submitter/posts_commits_100x1000_send_virt_m_1000.parquet"
)
df_responses = analyzer.get_df_from_parquet_file(
    "../submitter/posts_commits_100x1000_response_virt_m_100.parquet"
)


analysis.plot_commits(df_responses, df_generator)
