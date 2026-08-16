cmake_minimum_required(VERSION 3.20)
project(coolride_pq_core VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(coolride_pq_core STATIC src/controller.cpp)
target_include_directories(coolride_pq_core PUBLIC include)
target_compile_options(coolride_pq_core PRIVATE -Wall -Wextra -Wpedantic -Werror)

add_executable(coolride-controller src/cli.cpp)
target_link_libraries(coolride-controller PRIVATE coolride_pq_core)
target_compile_options(coolride-controller PRIVATE -Wall -Wextra -Wpedantic -Werror)

enable_testing()
add_executable(coolride-core-test tests/controller_test.cpp)
target_link_libraries(coolride-core-test PRIVATE coolride_pq_core)
target_compile_options(coolride-core-test PRIVATE -Wall -Wextra -Wpedantic -Werror)
add_test(NAME coolride-core-test COMMAND coolride-core-test)
