cmake_minimum_required(VERSION 3.15)
project(NetworkLadder CXX)
set(CMAKE_CXX_STANDARD 17)

add_library(network_core
  Polynomial.cpp
  ContinuedFraction.cpp
  NetworkUtils.cpp
  CSVMaker.cpp
)

target_include_directories(network_core PUBLIC .)

add_executable(app main.cpp)
target_link_libraries(app PRIVATE network_core)

# Tests (GoogleTest)
option(BUILD_TESTING "Build tests" ON)
if(BUILD_TESTING)
  enable_testing()
  find_package(GTest REQUIRED)
  add_executable(network_tests tests/test_network.cpp)
  target_link_libraries(network_tests PRIVATE network_core GTest::gtest GTest::gtest_main)
  add_test(NAME network_tests COMMAND network_tests)
endif()
