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

include(${CCF_DIR}/cmake/tools.cmake)
include(${CCF_DIR}/cmake/crypto.cmake)

include_directories(${CCF_DIR}/include)
include_directories(${CCF_DIR}/3rdparty/exported)
include_directories(${CCF_DIR}/src)

target_link_libraries(submit PRIVATE arrow)
target_link_libraries(submit PRIVATE parquet)
target_link_libraries(submit PRIVATE curl)
target_link_libraries(submit PRIVATE uv)
target_link_libraries(submit PRIVATE ssl)
target_link_libraries(submit PRIVATE crypto)
target_link_libraries(submit PRIVATE ccfcrypto.host)
target_link_libraries(
  submit
  PRIVATE
    ${CCF_DIR}/build/CMakeFiles/http_parser.host.dir/3rdparty/exported/llhttp/llhttp.c.o
)
target_link_libraries(
  submit
  PRIVATE
    ${CCF_DIR}/build/CMakeFiles/http_parser.host.dir/3rdparty/exported/llhttp/api.c.o
)
target_link_libraries(
  submit
  PRIVATE
    ${CCF_DIR}/build/CMakeFiles/http_parser.host.dir/3rdparty/exported/llhttp/http.c.o
)
