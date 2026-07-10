# Source files
set(SRC
    common.cpp
    utils.cpp
    bindings.cpp
    sets/minimalpaths.cpp
    sets/absorb_list.cpp
    sets/cutsets_common.cpp
    sets/cutsets_cnf_tree.cpp
    sets/cutsets_shannon.cpp
    sets/cutsets_multiplication.cpp
    sets/cutsets_combination.cpp
    sets/cutsets_combination_matrix.cpp
    availability/mcs.cpp
    availability/pathset.cpp
    availability/sdp.cpp
)

# Find pybind11
include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.13.6
)
FetchContent_MakeAvailable(pybind11)

# Find OpenMP
find_package(OpenMP REQUIRED)

# pybind11 module
pybind11_add_module(pyrbd_core_cpp ${SRC})
set_target_properties(pyrbd_core_cpp PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)

# Link OpenMP
if(OpenMP_CXX_FOUND)
    target_link_libraries(pyrbd_core_cpp PUBLIC OpenMP::OpenMP_CXX)
endif()

# Compile options
target_compile_options(pyrbd_core_cpp PRIVATE
    -Wall -O3 -march=native
)

# Include directories
target_include_directories(pyrbd_core_cpp PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Clean target
add_custom_target(distclean
    COMMAND ${CMAKE_COMMAND} -E remove_directory CMakeFiles
    COMMAND ${CMAKE_COMMAND} -E remove CMakeCache.txt
    COMMAND ${CMAKE_COMMAND} -E remove cmake_install.cmake
    COMMAND ${CMAKE_COMMAND} -E remove Makefile
    COMMAND ${CMAKE_COMMAND} -E remove -f ${CMAKE_CURRENT_SOURCE_DIR}/*.so
    COMMAND ${CMAKE_COMMAND} -E remove_directory _deps
    COMMENT "Removing all build files"
)

# Install target
install(TARGETS pyrbd_core_cpp
    LIBRARY DESTINATION pyrbd_core
    RUNTIME DESTINATION pyrbd_core
)
