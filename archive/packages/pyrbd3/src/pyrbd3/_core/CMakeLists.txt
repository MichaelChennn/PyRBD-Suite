# set source files
set(SRC
    common.cpp
    sdp.cpp
    utils.cpp
    bindings.cpp
)

# find pybind11
include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.13.6
)
FetchContent_MakeAvailable(pybind11)

# find OpenMP
find_package(OpenMP REQUIRED)

# pybind11 module
pybind11_add_module(pyrbd3_cpp ${SRC})
set_target_properties(pyrbd3_cpp PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)

# Link OpenMP if found
if(OpenMP_CXX_FOUND)
    target_link_libraries(pyrbd3_cpp PUBLIC OpenMP::OpenMP_CXX)
endif()

# set complie options
target_compile_options(pyrbd3_cpp PRIVATE
    -Wall -O3 -march=native
)

# set the include directories
target_include_directories(pyrbd3_cpp PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# clean target
add_custom_target(distclean
    COMMAND ${CMAKE_COMMAND} -E remove_directory CMakeFiles
    COMMAND ${CMAKE_COMMAND} -E remove CMakeCache.txt
    COMMAND ${CMAKE_COMMAND} -E remove cmake_install.cmake
    COMMAND ${CMAKE_COMMAND} -E remove Makefile
    COMMAND ${CMAKE_COMMAND} -E remove -f ${CMAKE_CURRENT_SOURCE_DIR}/*.so
    COMMAND ${CMAKE_COMMAND} -E remove_directory _deps
    COMMENT "Removing all build files"
)

# install target
install(TARGETS pyrbd3_cpp
    LIBRARY DESTINATION pyrbd3/_core
    RUNTIME DESTINATION pyrbd3/_core
)