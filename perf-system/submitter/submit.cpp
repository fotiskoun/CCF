// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the Apache 2.0 License.

#include "ccf/crypto/verifier.h"
#include "ccf/ds/logger.h"
#include "ccf/service/node_info_network.h"
#include "clients/rpc_tls_client.h"
#include "ds/files.h"
#include "handle_arguments.hpp"
#include "parquet_data.hpp"
#include "stdcpp.h"

#include <arrow/api.h>
#include <arrow/array/array_binary.h>
#include <arrow/filesystem/localfs.h>
#include <arrow/io/file.h>
#include <chrono>
#include <ctime>
#include <curl/curl.h>
#include <iostream>
#include <openssl/bio.h>
#include <openssl/err.h>
#include <openssl/pem.h>
#include <openssl/ssl.h>
#include <parquet/arrow/reader.h>
#include <parquet/stream_writer.h>
#include <uv.h>
#include <vector>

using namespace std;
using namespace client;

crypto::Pem key = {};
std::string key_id = "Invalid";
std::shared_ptr<tls::Cert> tls_cert = nullptr;

void readParquetFile(string generatorFilename, ParquetData& data_handler)
{
  arrow::Status st;
  arrow::MemoryPool* pool = arrow::default_memory_pool();
  arrow::fs::LocalFileSystem file_system;
  std::shared_ptr<arrow::io::RandomAccessFile> input =
    file_system.OpenInputFile(generatorFilename).ValueOrDie();

  // Open Parquet file reader
  std::unique_ptr<parquet::arrow::FileReader> arrow_reader;
  st = parquet::arrow::OpenFile(input, pool, &arrow_reader);
  if (!st.ok())
  {
    std::cout << "Couldn't open Input file" << std::endl;
  }
  else
  {
    std::cout << "Read generator file" << std::endl;
  }

  // Read entire file as a single Arrow table
  auto selected_columns = {0, 1};
  std::shared_ptr<arrow::Table> table;
  st = arrow_reader->ReadTable(selected_columns, &table);
  if (!st.ok())
  {
    std::cout << "Couldn't read Input file" << std::endl;
  }
  else
  {
    std::cout << "Opened generator file" << std::endl;
  }

  std::shared_ptr<::arrow::ChunkedArray> column;

  ::arrow::Status column1Status = arrow_reader->ReadColumn(1, &column);
  std::shared_ptr<arrow::StringArray> col1Vals =
    std::dynamic_pointer_cast<arrow::StringArray>(column->chunk(
      0)); // ASSIGN there is only one chunk with col->num_chunks();

  ::arrow::Status column2Status = arrow_reader->ReadColumn(2, &column);
  std::shared_ptr<arrow::StringArray> col2Vals =
    std::dynamic_pointer_cast<arrow::StringArray>(column->chunk(
      0)); // ASSIGN there is only one chunk with col->num_chunks();
  for (int row = 0; row < col1Vals->length(); row++)
  {
    data_handler.IDS.push_back(col1Vals->GetString(row));
    data_handler.REQUEST.push_back(col2Vals->GetString(row));
  }
}

void writeResponseParquetFile(std::string filename, ParquetData& data_handler)
{
  std::shared_ptr<arrow::io::FileOutputStream> outfile;

  PARQUET_ASSIGN_OR_THROW(outfile, arrow::io::FileOutputStream::Open(filename));

  parquet::WriterProperties::Builder builder;

  parquet::schema::NodeVector fields;

  fields.push_back(parquet::schema::PrimitiveNode::Make(
    "messageID",
    parquet::Repetition::REQUIRED,
    parquet::Type::BYTE_ARRAY,
    parquet::ConvertedType::UTF8));

  fields.push_back(parquet::schema::PrimitiveNode::Make(
    "receiveTime",
    parquet::Repetition::REQUIRED,
    parquet::Type::DOUBLE,
    parquet::ConvertedType::NONE));

  fields.push_back(parquet::schema::PrimitiveNode::Make(
    "rawResponse",
    parquet::Repetition::OPTIONAL,
    parquet::Type::BYTE_ARRAY,
    parquet::ConvertedType::UTF8));

  std::shared_ptr<parquet::schema::GroupNode> schema =
    std::static_pointer_cast<parquet::schema::GroupNode>(
      parquet::schema::GroupNode::Make(
        "schema", parquet::Repetition::REQUIRED, fields));

  parquet::StreamWriter os{
    parquet::ParquetFileWriter::Open(outfile, schema, builder.build())};

  for (size_t i = 0; i < data_handler.RESPONSE_TIME.size(); i++)
  {
    os << to_string(i) << data_handler.RESPONSE_TIME[i]
       << data_handler.RAW_RESPONSE[i] << parquet::EndRow;
  }
}

void writeSendParquetFile(std::string filename, ParquetData& data_handler)
{
  std::shared_ptr<arrow::io::FileOutputStream> outfile;

  PARQUET_ASSIGN_OR_THROW(outfile, arrow::io::FileOutputStream::Open(filename));

  parquet::WriterProperties::Builder builder;

  parquet::schema::NodeVector fields;

  fields.push_back(parquet::schema::PrimitiveNode::Make(
    "messageID",
    parquet::Repetition::REQUIRED,
    parquet::Type::BYTE_ARRAY,
    parquet::ConvertedType::UTF8));

  fields.push_back(parquet::schema::PrimitiveNode::Make(
    "sendTime",
    parquet::Repetition::REQUIRED,
    parquet::Type::DOUBLE,
    parquet::ConvertedType::NONE));

  std::shared_ptr<parquet::schema::GroupNode> schema =
    std::static_pointer_cast<parquet::schema::GroupNode>(
      parquet::schema::GroupNode::Make(
        "schema", parquet::Repetition::REQUIRED, fields));

  parquet::StreamWriter os{
    parquet::ParquetFileWriter::Open(outfile, schema, builder.build())};

  for (size_t i = 0; i < data_handler.SEND_TIME.size(); i++)
  {
    os << to_string(i) << data_handler.SEND_TIME[i] << parquet::EndRow;
  }
}

std::shared_ptr<RpcTlsClient> create_connection(
  std::vector<string> certificates, std::string server_address)
{
  // Create a cert if this is our first rpc_connection
  const bool is_first_time = tls_cert == nullptr;

  if (is_first_time)
  {
    const auto raw_cert = files::slurp(certificates[0].c_str());
    const auto raw_key = files::slurp(certificates[1].c_str());
    const auto ca = files::slurp_string(certificates[2].c_str());

    key = crypto::Pem(raw_key);

    const crypto::Pem cert_pem(raw_cert);
    auto cert_der = crypto::cert_pem_to_der(cert_pem);
    key_id = crypto::Sha256Hash(cert_der).hex_str();

    tls_cert =
      std::make_shared<tls::Cert>(std::make_shared<tls::CA>(ca), cert_pem, key);
  }

  const auto [host, port] = ccf::split_net_address(server_address);
  auto conn =
    std::make_shared<RpcTlsClient>(host, port, nullptr, tls_cert, key_id);

  conn->set_prefix("app");

  // Report ciphersuite of first client (assume it is the same for each)
  if (is_first_time)
  {
    LOG_DEBUG_FMT(
      "Connected to server via TLS ({})", conn->get_ciphersuite_name());
  }

  return conn;
}

std::string get_response_string(client::HttpRpcTlsClient::Response resp)
{
  string response_string = "HTTP/1.1 " + std::to_string(resp.status) + " " +
    http_status_str(resp.status) + "\n";
  for (auto const& x : resp.headers)
  {
    response_string += (x.first + ':' + x.second + "\n");
  }

  response_string += std::string(resp.body.begin(), resp.body.end());
  return response_string;
}

int main(int argc, char** argv)
{
  ArgumentParser args;
  args.argument_assigner(argc, argv);
  ParquetData data_handler;
  std::vector<string> certificates = {args.cert, args.key, args.rootCa};
  readParquetFile(args.generatorFilename, data_handler);
  std::string server_address = "127.0.0.1:8000";
  int max_block_write = 1000; // Threshold for pending writes
  auto requests_size = data_handler.IDS.size();

  timeval start[requests_size];
  timeval end[requests_size];
  std::vector<uint8_t> raw_reqs[requests_size];
  // Store responses until they are processed to be written in parquet
  HttpRpcTlsClient::Response* resp = (HttpRpcTlsClient::Response*)malloc(
    sizeof(HttpRpcTlsClient::Response) * requests_size);

  // Add raw requests straight as uint8_t inside a vector
  for (size_t req = 0; req < requests_size; req++)
  {
    raw_reqs[req] = std::vector<uint8_t>(
      data_handler.REQUEST[req].begin(), data_handler.REQUEST[req].end());
  }

  std::cout << "Start Request Submission" << endl;

  if (!args.isPipeline)
  {
    // Request by Request
    for (size_t req = 0; req < requests_size; req++)
    {
      gettimeofday(&start[req], NULL);
      auto connection = create_connection(certificates, server_address);
      connection->write(raw_reqs[req]);
      resp[req] = connection->read_response();
      gettimeofday(&end[req], NULL);
    }
  }
  else
  {
    // Pipeline
    int read_reqs = 0; // use this to block writes
    auto connection = create_connection(certificates, server_address);

    for (size_t req = 0; req < requests_size; req++)
    {
      gettimeofday(&start[req], NULL);
      connection->write(raw_reqs[req]);
      if (connection->bytes_available() or req - read_reqs > max_block_write)
      {
        gettimeofday(&end[read_reqs], NULL);
        resp[read_reqs] = connection->read_response();
        read_reqs++;
      }
    }

    // Read remaining responses
    while (read_reqs < requests_size)
    {
      resp[read_reqs] = connection->read_response();
      gettimeofday(&end[read_reqs], NULL);
      read_reqs++;
    }
  }

  for (size_t req = 0; req < requests_size; req++)
  {
    data_handler.RAW_RESPONSE.push_back(get_response_string(resp[req]));
    double send_time = start[req].tv_sec + start[req].tv_usec / 1000000.0;
    double response_time = end[req].tv_sec + end[req].tv_usec / 1000000.0;
    data_handler.SEND_TIME.push_back(send_time);
    data_handler.RESPONSE_TIME.push_back(response_time);
  }
  std::cout << "Finished Request Submission" << endl;

  cout << "Start storing results" << endl;
  writeSendParquetFile(args.sendFilename, data_handler);
  writeResponseParquetFile(args.responseFilename, data_handler);
  cout << "Finished storing results" << endl;
}
