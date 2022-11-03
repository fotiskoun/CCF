# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the Apache 2.0 License.
"""
Submit requests
"""

import asyncio
import time
import ssl
import argparse

# pylint: disable=import-error
import httpx  # type: ignore
import pandas as pd  # type: ignore

# pylint: disable=import-error
import fastparquet as fp  # type: ignore


async def read(certificates, file_names, duration, server_address):
    """
    Read the dataframes and call requests submission
    """
    req_df = pd.read_parquet(file_names[0], engine="fastparquet")
    df_sends = pd.DataFrame(columns=["messageID", "sendTime"])
    df_responses = pd.DataFrame(columns=["messageID", "receiveTime", "rawResponse"])

    sslcontext = ssl.create_default_context(cafile=certificates[0])
    sslcontext.load_cert_chain(certificates[1], certificates[2])

    # formalize the server_address
    if not server_address.startswith("http"):
        server_address = "https://" + server_address

    req_details = []
    req_headers = []
    req_data = []

    print("Starting Formalizing Data")

    # get the http version from the first request
    http_vers = req_df.iloc[0]["request"].split("\r\n")[0].split(" ")[-1]
    is_http2 = False
    if http_vers.upper() == "HTTP/2":
        is_http2 = True

    # create the requests
    for i, req_row in req_df.iloc[:].iterrows():
        req = req_row["request"].split("\r\n")
        req_details.append(req[0].split(" "))
        req_headers.append(
            {x.split(":")[0].strip(): x.split(":")[1].strip() for x in req[1:-2]}
        )
        if req_details[i][0] == "GET":
            req_data.append("")
        else:
            req_data.append(req[-1])

    print("Finished Formalizing Data")

    print("Starting Submission")

    if duration > 0:
        duration_end_time = time.time() + (duration)
        run_loop_once = False
        duration_run = True
    else:
        duration_end_time = -1
        run_loop_once = True
        duration_run = False

    while (duration_end_time > 0 and duration_run) or (
        duration_end_time < 0 and run_loop_once
    ):
        last_index = len(df_sends.index)
        async with httpx.AsyncClient(verify=sslcontext, http2=is_http2) as session:
            for i in range(len(req_details)):
                if req_details[i][0] == "POST":
                    df_sends.loc[i + last_index] = [i + last_index, time.time()]
                    resp = await session.post(
                        server_address + req_details[i][1],
                        data=req_data[i],
                        headers=req_headers[i],
                    )
                    end_time = time.time()
                    write_response(resp, df_responses, end_time, i, last_index)

                elif req_details[i][0] == "GET":
                    df_sends.loc[i + last_index] = [i + last_index, time.time()]
                    resp = await session.get(
                        server_address + req_details[i][1],
                        headers=req_headers[i],
                    )
                    end_time = time.time()
                    write_response(resp, df_responses, end_time, i, last_index)

                elif req_details[i][0] == "DELETE":
                    df_sends.loc[i + last_index] = [i + last_index, time.time()]
                    resp = await session.delete(
                        server_address + req_details[i][1],
                        headers=req_headers[i],
                    )
                    end_time = time.time()
                    write_response(resp, df_responses, end_time, i, last_index)

                if time.time() > duration_end_time and not run_loop_once:
                    duration_run = False
                    break
            run_loop_once = False

    fp.write(file_names[1], df_sends)
    fp.write(file_names[2], df_responses)


def write_response(resp, df_responses, end_time, i, last_index):
    """
    Populate the dataframe for responses
    """
    resp_headers = str(resp.headers)
    if len(resp_headers) > 10:
        resp_headers = resp_headers[9:-2].replace("'", "")
        resp_headers = resp_headers.replace(", ", "\n")
    df_responses.loc[i + last_index] = [
        i + last_index,
        end_time,
        str(resp.http_version)
        + " "
        + str(resp.status_code)
        + "\n"
        + resp_headers
        + "\n"
        + resp.text[10:-1],
    ]


def main():
    """
    Receives the command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Sample Submitter for perf workloads",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-ca",
        "--cacert",
        help="Use the specified file for certificate verification.",
        type=str,
    )
    parser.add_argument(
        "-c",
        "--cert",
        help="Use the provided certificate file when working with a SSL-based protocol.",
        type=str,
    )
    parser.add_argument(
        "-k",
        "--key",
        help="Specify the path to the file containing the private key.",
        type=str,
    )
    parser.add_argument(
        "-d",
        "--duration",
        help="Time duration for the submitter to run",
        default=-1,
        type=int,
    )
    parser.add_argument(
        "-gf",
        "--generator_filepath",
        help="Path to parquet file with the generated requests to be submitted.",
        default="../generator/requests.parquet",
        type=str,
    )
    parser.add_argument(
        "-sf",
        "--send_filepath",
        help="Path to parquet file to store the submitted requests.",
        default="./sends.parquet",
        type=str,
    )
    parser.add_argument(
        "-rf",
        "--response_filepath",
        help="Path to parquet file to store the responses from the submitted requests.",
        default="./responses.parquet",
        type=str,
    )

    parser.add_argument(
        "-sa",
        "--server_address",
        help="Specify the address to submit requests.",
        default="127.0.0.1:8000",
        type=str,
    )

    args = parser.parse_args()

    asyncio.run(
        read(
            [args.cacert, args.cert, args.key],
            [args.generator_filepath, args.send_filepath, args.response_filepath],
            args.duration,
            args.server_address,
        )
    )
    print("Finished Submission")


if __name__ == "__main__":
    main()
