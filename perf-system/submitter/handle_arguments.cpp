// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the Apache 2.0 License.

#include "handle_arguments.hpp"

ArgumentParser::ArgumentParser() {}

void ArgumentParser::argument_assigner(int argc, char** argv)
{
  for (int argIter = 1; argIter < argc; argIter++)
  {
    std::string string_argument(argv[argIter]);
    if (string_argument.compare("-c") == 0)
    {
      cert = argv[argIter + 1];
    }
    else if (string_argument.compare("-k") == 0)
    {
      key = argv[argIter + 1];
    }
    else if (string_argument.compare("-ca") == 0)
    {
      rootCa = argv[argIter + 1];
    }
    else if (string_argument.compare("-sf") == 0)
    {
      send_filename = argv[argIter + 1];
    }
    else if (string_argument.compare("-rf") == 0)
    {
      response_filename = argv[argIter + 1];
    }
    else if (string_argument.compare("-pipeline") == 0)
    {
      isPipeline = true;
    }
    else if (string_argument.compare("-gf") == 0)
    {
      generator_filename = argv[argIter + 1];
    }
    else if (string_argument.compare("-d") == 0)
    {
      duration = atoi(argv[argIter + 1]);
    }
    else if (string_argument.compare("-sa") == 0)
    {
      server_address = argv[argIter + 1];
    }
  }
}