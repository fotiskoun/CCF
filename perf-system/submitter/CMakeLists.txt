cmake_minimum_required(VERSION 3.16)

project(submit)

set(CMAKE_CXX_STANDARD 20)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -w")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2")

add_executable(
  submit submit.cpp handle_arguments.cpp handle_arguments.hpp stdcpp.h
         parquet_data.hpp
)

set(CCF_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../..)
set(CCF_3RD_PARTY_EXPORTED_DIR "${CCF_DIR}/3rdparty/exported")

include(${CCF_DIR}/cmake/tools.cmake)
include(${CCF_DIR}/cmake/crypto.cmake)

include_directories(${CCF_DIR}/include)
include_directories(${CCF_3RD_PARTY_EXPORTED_DIR})
include_directories(${CCF_DIR}/src)


set(HTTP_PARSER_SOURCES
    ${CCF_3RD_PARTY_EXPORTED_DIR}/llhttp/api.c
    ${CCF_3RD_PARTY_EXPORTED_DIR}/llhttp/http.c
    ${CCF_3RD_PARTY_EXPORTED_DIR}/llhttp/llhttp.c
)


add_library(http_parser.host "${HTTP_PARSER_SOURCES}")


target_link_libraries(submit PRIVATE arrow)
target_link_libraries(submit PRIVATE parquet)
target_link_libraries(submit PRIVATE ccfcrypto.host)
target_link_libraries(submit PRIVATE http_parser.host)