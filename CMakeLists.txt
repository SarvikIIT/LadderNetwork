cmake_minimum_required(VERSION 3.15)
project(NetworkLadder CXX)
set(CMAKE_CXX_STANDARD 17)

# Set source directory
set(SOURCES_DIR src)

add_library(network_core
  ${SOURCES_DIR}/Polynomial.cpp
  ${SOURCES_DIR}/ContinuedFraction.cpp
  ${SOURCES_DIR}/NetworkUtils.cpp
  ${SOURCES_DIR}/CSVMaker.cpp
)

target_include_directories(network_core PUBLIC ${SOURCES_DIR})

add_executable(app ${SOURCES_DIR}/main.cpp)
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
