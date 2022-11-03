// // Copyright (c) Microsoft Corporation. All rights reserved.
// // Licensed under the Apache 2.0 License.

// #include "handle_arguments.hpp"

// ArgumentParser::ArgumentParser() {}

// void ArgumentParser::argument_assigner(int argc, char** argv)
// {
//   for (int argIter = 1; argIter < argc; argIter++)
//   {
//     std::string string_argument(argv[argIter]);
//     if (string_argument.compare("--cert") == 0)
//     {
//       cert = argv[argIter + 1];
//     }
//     else if (string_argument.compare("--key") == 0)
//     {
//       key = argv[argIter + 1];
//     }
//     else if (string_argument.compare("--cacert") == 0)
//     {
//       rootCa = argv[argIter + 1];
//     }
//     else if (string_argument.compare("--send-filepath") == 0)
//     {
//       send_filepath = argv[argIter + 1];
//     }
//     else if (string_argument.compare("--response-filepath") == 0)
//     {
//       response_filepath = argv[argIter + 1];
//     }
//     else if (string_argument.compare("--pipeline") == 0)
//     {
//       isPipeline = true;
//     }
//     else if (string_argument.compare("--generator-filepath") == 0)
//     {
//       generator_filepath = argv[argIter + 1];
//     }
//     else if (string_argument.compare("--server-address") == 0)
//     {
//       server_address = argv[argIter + 1];
//     }
//   }
// }