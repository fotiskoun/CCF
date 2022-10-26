// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the Apache 2.0 License.

#ifndef HANDLE_ARGUMENTS_H
#define HANDLE_ARGUMENTS_H
#include <iostream>

class ArgumentParser
{
public:
  std::string cert;
  std::string key;
  std::string rootCa;
  std::string server_address = "127.0.0.1:8000";
  std::string send_filename = "../perf-system/submitter/cpp_send.parquet";
  std::string response_filename =
    "../perf-system/submitter/cpp_respond.parquet";
  std::string generator_filename = "../perf-system/generator/requests.parquet";
  bool isPipeline = false;
  int duration = -1;
  ArgumentParser();
  void argument_assigner(int argc, char** argv);
};

#endif