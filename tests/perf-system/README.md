# Generic Performance Testing System

A Performance Testing System which consists from three different components:
_Generator_
_Submitter_
_Analysis_

The folder containing each these components is the **CCF/perf-system**

The required Python packages are included inside the the  **CCF/perf-system/requirements.txt** and can be installed running the following command from the **CCF/perf-system** directory.

```sh
pip install -r requirements.txt
```

For installation of the required libraries for C++ see on the description of the [Submitter](#submitter) component

After that, run your CCF system.

## Generator

Inside the **CCF/perf-system/generator** exists the generator component and you can execute it from this directory with the following command:

```sh
python3 generator.py
```

By default, the generator will create a .parquet file, which is necessary for the following component, using the configurations provided. To provide another configuration file please use the following options:

### Optional arguments:
- `-h, --help`: show this help message and exit
- `-hs HOST, --host HOST`: The host to submit the request. (default: 127.0.0.1:8000)
- `-p PATH, --path PATH`: The relative path to submit the request. (default: /app/log/private)
- `-vr VERB, --verb VERB`: The request action. (default: POST)
- `-r ROWS, --rows ROWS`: The number of requests to send. (default: 16)
- `-rt REQUEST_TYPE, --request_type REQUEST_TYPE`: The transfer protocol for the request. (default: HTTP/1.1)
- `-pf PATH_TO_PARQUET, --path_to_parquet PATH_TO_PARQUET`: Path to the parquet file to store the generated requests (default: ./requests.parquet)
- `-ct CONTENT_TYPE, --content_type CONTENT_TYPE`: The Content-Type representation header is used to indicate the original media type of the resource. (default: application-json)
- `-d DATA, --data DATA`: A string with the data to be sent with a request (default: {"id": 1, "msg": "Send message with id 1"})

This component consists of different files including the **CCF/perf-system/Generator/loggin_generator.py**, which is an alternative of the command line options, providing more flexibility to the user in order to create his own more complex requests. There exist some samples, creating an object to initialize a dataframe and call `append()` function to add requests specified by the arguments given to the dataframe. The `append()` function returns the last batch of requests created as a dataframe in order to create more requests based on the already appended. 
All requests in the end should be followed by the `to_parquet_file()` function in order to generate the parquet file.
You can either edit **CCF/perf-system/Generator/loggin_generator.py** or create your own file in the same directory calling functions from the **CCF/perf-system/Generator/generator.py** in order to construct your own series of requests.

<a id="submitter"></a>
## Submitter

In the **CCF/perf-system/submitter** there are two submitter components one written in C++ language and a simpler in Python.

### C++

For the **C++** submitter one of the main requirements is Apache Arrow and Parquet. To install these requirements, if you haven't done yet, please install the requirements from the **CCF/getting-started/setup_vm** directory following the below command.

```sh
./run.sh ccf-dev.yml
```

After installing arrow you can build and run the submitter from the root CCF directory **CCF/build/**. If you haven't done before, create a build directory in `CCF` and then build and run using the following commands:

```sh
mkdir build
cd build
cmake -GNinja ..
ninja submit
./submit -manual_configurations
```

You can provide certification files or configure import/export files by replacing `-manual_configurations` in the latest command with one or more of the following options, providing after each option the corresponding argument (where necessary).

### Optional arguments:
- `-h,--help`: Print this help message and exit
- `--cert`: Use the provided certificate file when working with a SSL-based protocol.
- `--key`: Specify the path to the file containing the private key.
- `--cacert`: Use the specified file for certificate verification.
- `--server-address`: Specify the address to submit requests. (default: 127.0.0.1:8000)
- `--send-filepath`: Path to parquet file to store the submitted requests. (default: ../perf-system/submitter/cpp_send.parquet)
- `--response-filepath`: Path to parquet file to store the responses from the submitted requests. (default: ../perf-system/submitter/cpp_respond.parquet)
- `--generator-filepath`: Path to parquet file with the generated requests to be submitted. (default: ../perf-system/generator/requests.parquet)
- `--pipeline`: Enable HTTP/1.1 pipelining option.

### Python

To run the submitter written in **Python** you need to run from the current directory the following command

```sh
python3 submitter.py
```

When running the submitter you have the following options to configure the submitter:

### Optional arguments:
- `-h, --help`: Show this help message and exit
- `-ca CACERT, --cacert CACERT`: Use the specified file for certificate verification.
- `-c CERT, --cert CERT`: Use the provided certificate file when working with a SSL-based protocol.
- `-k KEY, --key KEY`: Specify the path to the file containing the private key.
- `-d DURATION, --duration DURATION`: Time duration for the submitter to run (default: -1)
- `-gf GENERATOR_FILEPATH, --generator_filepath GENERATOR_FILEPATH`: Path to parquet file with the generated requests to be submitted. (default: ../generator/requests.parquet)
- `-sf SEND_FILEPATH, --send_filepath SEND_FILEPATH`: Path to parquet file to store the submitted requests. (default: ./sends.parquet)
- `-rf RESPONSE_FILEPATH, --response_filepath RESPONSE_FILEPATH`: Path to parquet file to store the responses from the submitted requests. (default: ./responses.parquet)
- `-sa SERVER_ADDRESS, --server_address SERVER_ADDRESS`: Specify the address to submit requests. (default: 127.0.0.1:8000)

When the submitter is executed successfully, there will be two .parquet files generated in this directory.

## Analyzer

The **CCF/perf-system/analyzer** directory, contains the last component which is used to produce some metrics based on the submitted data of the previous component. There are two files in this directory, one containing the library with the available functions in order to run your experiments and a second that has a command line tool to run a default analysis. By creating a new python file to handle the dataframes and latencies for the requests, you can create your own analysis. For the default analysis you can run the following command from the current directory:

```sh
python3 analysis.py
```

You have the following options to specify the exported files:

### Optional arguments:
- `-h, --help`: Show this help message and exit
- `-sf SEND_FILE_PATH, --send_file_path SEND_FILE_PATH`: Path to the parquet file that contains the submitted requests (default: ../submitter/cpp_send.parquet)
- `-rf RESPONSE_FILE_PATH, --response_file_path RESPONSE_FILE_PATH`: Path to the parquet file that contains the responses from the submitted requests (default: ../submitter/cpp_respond.parquet)

After the execution, in the command prompt will be written two tables with some metrics and in the current directory there will be exported images plotting the latency across time or based on the id and the throughput of the requests.
