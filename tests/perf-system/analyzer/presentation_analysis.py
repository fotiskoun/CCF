# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.

import analyzer
import numpy as np
import matplotlib.pyplot as plt

df_sends_virt_m0 = analyzer.get_df_from_parquet_file(
    "../submitter/100k_single_read_send_virt_m_0.parquet"
)
df_responses_virt_m0 = analyzer.get_df_from_parquet_file(
    "../submitter/100k_single_read_response_virt_m_0.parquet"
)

analysis_virt_m0 = analyzer.Analyze()


df_sends_virt_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/100k_single_read_send_virt_m_1000.parquet"
)
df_responses_virt_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/100k_single_read_response_virt_m_1000.parquet"
)

analysis_virt_m1000 = analyzer.Analyze()

js_df_sends_virt_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/js_100k_single_read_send_virt_m_1000.parquet"
)
js_df_responses_virt_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/js_100k_single_read_response_virt_m_100.parquet"
)

js_analysis_virt_m1000 = analyzer.Analyze()


df_sends_virt_m_1 = analyzer.get_df_from_parquet_file(
    "../submitter/100k_single_read_send_virt_m_-1.parquet"
)
df_responses_virt_m_1 = analyzer.get_df_from_parquet_file(
    "../submitter/100k_single_read_response_virt_m_-1.parquet"
)

analysis_virt_m1 = analyzer.Analyze()


df_sends_sgx_m0 = analyzer.get_df_from_parquet_file(
    "../submitter/100k_single_read_send_sgx_m_0.parquet"
)
df_responses_sgx_m0 = analyzer.get_df_from_parquet_file(
    "../submitter/100k_single_read_response_sgx_m_0.parquet"
)
analysis_sgx_m0 = analyzer.Analyze()

df_sends_sgx_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/100k_single_read_send_sgx_m_1000.parquet"
)
df_responses_sgx_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/100k_single_read_response_sgx_m_1000.parquet"
)
analysis_sgx_m1000 = analyzer.Analyze()


# POSTS

df_sends_post_small_virt_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/posts_small_message_100k_send_virt_m_1000.parquet"
)
df_responses_post_small_virt_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/posts_small_message_100k_response_virt_m_100.parquet"
)
analysis_post_small_virt_m1000 = analyzer.Analyze()

df_sends_post_small_virt_m0 = analyzer.get_df_from_parquet_file(
    "../submitter/posts_small_message_100k_send_virt_m_0.parquet"
)
df_responses_post_small_virt_m0 = analyzer.get_df_from_parquet_file(
    "../submitter/posts_small_message_100k_response_virt_m_0.parquet"
)
analysis_post_small_virt_m0 = analyzer.Analyze()


df_sends_post_large_virt_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/posts_large_message_100k_send_virt_m_1000.parquet"
)
df_responses_post_large_virt_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/posts_large_message_100k_response_virt_m_100.parquet"
)
analysis_post_large_virt_m1000 = analyzer.Analyze()


df_generator_posts_commits = analyzer.get_df_from_parquet_file(
    "../generator/posts_commits_100x1000.parquet"
)
df_sends_posts_commits_virt_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/posts_commits_100x1000_send_virt_m_1000.parquet"
)
df_responses_posts_commits_virt_m1000 = analyzer.get_df_from_parquet_file(
    "../submitter/posts_commits_100x1000_response_virt_m_100.parquet"
)
analysis_post_large_virt_m1000 = analyzer.Analyze()

## PLOT POSTS vs COMMITS WINDOW START
# analysis_post_large_virt_m1000.plot_commits(
#     df_responses_posts_commits_virt_m1000, df_generator_posts_commits
# )
## PLOT POSTS vs COMMITS WINDOW FIN

# success_post_small_virt_m0 = analysis_post_small_virt_m0.iter_for_success_and_latency(
#     df_sends_post_small_virt_m0, df_responses_post_small_virt_m0
# )

# success_virt_m1000 = analysis_virt_m1000.iter_for_success_and_latency(
#     df_sends_virt_m1000, df_responses_virt_m1000
# )

# print(
#     analysis_virt_m0.time_success_throughput_table(
#         df_sends_virt_m0, df_responses_virt_m0, success_virt_m0
#     )
# )


# PLOT GET THROUGHPUT VIRT vs SGX START

time_spent = analysis_post_small_virt_m0.total_time_in_sec(
    df_sends_post_small_virt_m0, df_responses_post_small_virt_m0
)

virt_m0 = analysis_virt_m0.plot_throughput_per_block(df_responses_virt_m0, 0.5)
virt_m1000 = analysis_virt_m1000.plot_throughput_per_block(
    df_responses_virt_m1000, 0.05
)
sgx_0 = analysis_sgx_m0.plot_throughput_per_block(df_responses_sgx_m0, 0.5)
sgx_1000 = analysis_sgx_m1000.plot_throughput_per_block(df_responses_sgx_m1000, 0.05)

plt.figure()
plt.plot(virt_m1000[0][:-1], virt_m1000[1][:-1], label="virtual m=1000")
plt.plot(sgx_1000[0][:-1], sgx_1000[1][:-1], label="sgx m=1000")
plt.ylabel("Throughput(req/s)")
plt.xlabel("Time(s)")
# plt.xscale("log")
plt.ylim([0, 105000])
plt.xlim([0, 3.5])
plt.legend()
plt.tight_layout()

plt.savefig("virt_sgx_m1000_throughput_across_time.png", dpi=300)
# plt.figure(2)

# plt.plot(virt_m0[0], virt_m0[1], label="virtual m=0")
# plt.plot(sgx_0[0], sgx_0[1], label="sgx m=0")
# plt.ylabel("Throughput(req/s)")
# plt.xlabel("Time(s)")
# # plt.xscale("log")
# plt.legend()
# plt.tight_layout()
# plt.ylim([0, 105000])
# plt.xlim([0, 115])

# plt.savefig("virt_sgx_m0_throughput_across_time.png", dpi=300)

# PLOT GET THROUGHPUT VIRT vs SGX FIN


# PLOT GET THROUGHPUT JS AND C++ START
# js_virt_m1000 = js_analysis_virt_m1000.plot_throughput_per_block(
#     js_df_responses_virt_m1000, 0.05
# )
# virt_m1000 = analysis_virt_m1000.plot_throughput_per_block(
#     df_responses_virt_m1000, 0.05
# )

# plt.figure()
# plt.plot(js_virt_m1000[0][:-1], js_virt_m1000[1][:-1], label="JS")
# plt.plot(virt_m1000[0][:-1], virt_m1000[1][:-1], label="C++")
# plt.ylabel("Throughput(req/s)")
# plt.xlabel("Time(s)")
# plt.xlim([0, 24])
# plt.legend()
# plt.tight_layout()

# plt.savefig("c++_js+virt_m1000_throughput_across_time.png", dpi=300)
# PLOT GET THROUGHPUT JS AND C++ FIN


#### PLOT POST SMALL vs LARGE START
# virt1000_small = analysis_post_small_virt_m1000.plot_throughput_per_block(
#     df_responses_post_small_virt_m1000, 0.05
# )


# virt1000_large = analysis_post_large_virt_m1000.plot_throughput_per_block(
#     df_responses_post_large_virt_m1000, 0.05
# )
# plt.figure()

# plt.plot(virt1000_small[0], virt1000_small[1], label="small")
# plt.plot(virt1000_large[0], virt1000_large[1], label="large")
# plt.ylabel("Throughput(req/s)")
# plt.xlabel("Time(s)")
# plt.legend()
# plt.xlim([0, 5.5])
# plt.tight_layout()

# plt.savefig("post_small_large_virtual_m1000_throughput_across_time.png", dpi=300)
#### PLOT POST SMALL vs LARGE FIN

# LATENCY POSTS START
# s = analysis_post_small_virt_m0.iter_for_success_and_latency(
#     df_sends_post_small_virt_m0, df_responses_post_small_virt_m0
# )
# analysis_post_small_virt_m0.plot_latency_across_time(df_responses_post_small_virt_m0)


# time_spent = analysis_post_small_virt_m0.total_time_in_sec(
#     df_sends_post_small_virt_m0, df_responses_post_small_virt_m0
# )

# col_names = [
#     "Reqs",
#     "Time(s)",
#     "Pass",
#     "Throughput(req/s)",
#     "Latency (50th) (ms)",
#     "Latency 99.9th (ms)",
# ]
# rows = [
#     [
#         len(df_sends_post_small_virt_m0.index),
#         round(time_spent, 3),
#         round(s, 1),
#         round(len(df_sends_post_small_virt_m0.index) / time_spent, 1),
#         round(np.percentile(analysis_post_small_virt_m0.ms_latency_list, 50), 3),
#         round(np.percentile(analysis_post_small_virt_m0.ms_latency_list, 99.9), 3),
#     ]
# ]
# print(analysis_post_small_virt_m0.customize_table(col_names, rows))
# LATENCY POSTS FIN

# LATENCY GET START
# s = analysis_virt_m0.iter_for_success_and_latency(
#     df_sends_virt_m0, df_responses_virt_m0
# )
# analysis_virt_m0.plot_latency_across_time(df_responses_virt_m0)


# time_spent = analysis_virt_m0.total_time_in_sec(df_sends_virt_m0, df_responses_virt_m0)

# col_names = [
#     "Reqs",
#     "Time(s)",
#     "Pass",
#     "Throughput(req/s)",
#     "Latency (50th) (ms)",
#     "Latency 99.9th (ms)",
# ]
# rows = [
#     [
#         len(df_sends_virt_m0.index),
#         round(time_spent, 3),
#         round(s, 1),
#         round(len(df_sends_virt_m0.index) / time_spent, 1),
#         round(np.percentile(analysis_virt_m0.ms_latency_list, 50), 3),
#         round(np.percentile(analysis_virt_m0.ms_latency_list, 99.9), 3),
#     ]
# ]
# print(analysis_virt_m0.customize_table(col_names, rows))
# LATENCY GET FIN
