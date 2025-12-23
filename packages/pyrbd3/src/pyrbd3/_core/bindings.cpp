#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pyrbd3/sdp.hpp>

namespace py = pybind11;
using namespace pyrbd3;
using namespace pyrbd3::sdp;

PYBIND11_MODULE(pyrbd3_cpp, m)
{
    m.doc() = "PyRBD3 - Reliability Block Diagram analysis library";

    // Bind Classes
    py::class_<ProbabilityMap>(m, "ProbabilityMap")
        .def(py::init<const std::map<int, double>&>())
        .def("print", &ProbabilityMap::print)
        .def("__getitem__", &ProbabilityMap::operator[]);

    py::class_<SDP>(m, "SDP")
        .def(py::init<bool, std::vector<int>>())
        .def("isComplementary", &SDP::isComplementary)
        .def("getSet", &SDP::getSet, py::return_value_policy::reference_internal);

    // SDP Algorithm
    auto sdp_mod = m.def_submodule("sdp", "Module for SDP algorithm");
    sdp_mod.doc() = "Module for SDP algorithm";

    sdp_mod.def("to_sdp_set", &sdp::toSDPSet,
                "Convert path sets to SDP sets (serial)",
                py::arg("src"), py::arg("dst"), py::arg("path_sets"));
    
    sdp_mod.def("to_sdp_set_parallel", &sdp::toSDPSetParallel,
                "Convert path sets to SDP sets (parallel)",
                py::arg("src"), py::arg("dst"), py::arg("path_sets"),
                py::call_guard<py::gil_scoped_release>());

    sdp_mod.def("eval_avail", 
                [](NodeID src, NodeID dst, const std::map<int, double>& probabilities, PathSets& path_sets) {
                    ProbabilityMap probMap(probabilities); 
                    return sdp::evalAvail(src, dst, probMap, path_sets);
                },
                "Evaluate availability for single source destination pair using SDP approach",
                py::arg("src"), py::arg("dst"), py::arg("probabilities"), py::arg("path_sets"));

    sdp_mod.def("eval_avail_parallel", 
                [](NodeID src, NodeID dst, const std::map<int, double>& probabilities, PathSets& path_sets) {
                    ProbabilityMap probMap(probabilities); 
                    return sdp::evalAvailParallel(src, dst, probMap, path_sets);
                },
                "Evaluate availability for single source destination pair using SDP approach (parallel)",
                py::arg("src"), py::arg("dst"), py::arg("probabilities"), py::arg("path_sets"),
                py::call_guard<py::gil_scoped_release>());
    
    sdp_mod.def("eval_avail_topo", 
                [](const std::vector<std::pair<NodeID, NodeID>>& node_pairs, 
                   const std::map<int, double>& probabilities, 
                   std::vector<PathSets>& pathsets_list) {
                    ProbabilityMap probMap(probabilities); 
                    return sdp::evalAvailTopo(node_pairs, probMap, pathsets_list);
                },
                "Evaluate availability for each node pairs in topology using SDP (serial)",
                py::arg("node_pairs"), py::arg("probabilities"), py::arg("pathsets_list"));

    sdp_mod.def("eval_avail_topo_parallel", 
                [](const std::vector<std::pair<NodeID, NodeID>>& node_pairs, 
                   const std::map<int, double>& probabilities, 
                   std::vector<PathSets>& pathsets_list) {
                    ProbabilityMap probMap(probabilities); 
                    return sdp::evalAvailTopoParallel(node_pairs, probMap, pathsets_list);
                },
                "Evaluate availability for each node pairs in topology using SDP (parallel)",
                py::arg("node_pairs"), py::arg("probabilities"), py::arg("pathsets_list"),
                py::call_guard<py::gil_scoped_release>());
}