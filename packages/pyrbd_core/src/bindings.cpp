#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pyrbd_core/common.hpp>
#include <pyrbd_core/sets.hpp>
#include <pyrbd_core/availability/mcs.hpp>
#include <pyrbd_core/availability/pathset.hpp>
#include <pyrbd_core/availability/sdp.hpp>

namespace py = pybind11;
using namespace pyrbd_core;

// ================================================================
// Offset helpers: Python uses 0-based node IDs, C++ uses 1-based.
// These functions transparently apply the +1/-1 offset.
// ================================================================

namespace {

    // Apply +1 offset to a single node ID
    inline NodeID toInternal(NodeID id) { return id + 1; }

    // Apply -1 offset to a single node ID
    inline NodeID toExternal(NodeID id) { return id - 1; }

    // Apply +1 offset to a flat set of node IDs
    Set offsetSetIn(const Set& s)
    {
        Set result;
        result.reserve(s.size());
        for (int v : s) result.push_back(v + 1);
        return result;
    }

    // Apply -1 offset to a flat set of node IDs
    Set offsetSetOut(const Set& s)
    {
        Set result;
        result.reserve(s.size());
        for (int v : s) result.push_back(v - 1);
        return result;
    }

    // Apply +1 offset to a list of sets
    std::vector<Set> offsetSetsIn(const std::vector<Set>& sets)
    {
        std::vector<Set> result;
        result.reserve(sets.size());
        for (const auto& s : sets) result.push_back(offsetSetIn(s));
        return result;
    }

    // Apply -1 offset to a list of sets
    std::vector<Set> offsetSetsOut(const std::vector<Set>& sets)
    {
        std::vector<Set> result;
        result.reserve(sets.size());
        for (const auto& s : sets) result.push_back(offsetSetOut(s));
        return result;
    }

    // Apply +1 offset to a probability map (keys only)
    std::map<int, double> offsetProbMapIn(const std::map<int, double>& m)
    {
        std::map<int, double> result;
        for (const auto& [k, v] : m) result[k + 1] = v;
        return result;
    }

    // Apply +1 offset to node pairs
    NodePairs offsetPairsIn(const NodePairs& pairs)
    {
        NodePairs result;
        result.reserve(pairs.size());
        for (const auto& [a, b] : pairs) result.emplace_back(a + 1, b + 1);
        return result;
    }

    // Apply -1 offset to AvailTriple list
    std::vector<AvailTriple> offsetTriplesOut(const std::vector<AvailTriple>& triples)
    {
        std::vector<AvailTriple> result;
        result.reserve(triples.size());
        for (const auto& [a, b, c] : triples)
            result.emplace_back(a - 1, b - 1, c);
        return result;
    }

    // Apply +1 offset to adjacency list
    AdjList offsetAdjIn(const AdjList& adj)
    {
        // Input: adj[0-based] = list of 0-based neighbours
        // Output: adj[1-based] = list of 1-based neighbours (size = adj.size() + 1)
        AdjList result(adj.size() + 1);
        for (size_t i = 0; i < adj.size(); ++i)
        {
            result[i + 1].reserve(adj[i].size());
            for (int n : adj[i])
                result[i + 1].push_back(n + 1);
        }
        return result;
    }

    // Apply +1 offset to a list of list of sets (e.g. pathsets_list for topo)
    std::vector<std::vector<Set>> offsetSetsListIn(const std::vector<std::vector<Set>>& sl)
    {
        std::vector<std::vector<Set>> result;
        result.reserve(sl.size());
        for (const auto& sets : sl)
            result.push_back(offsetSetsIn(sets));
        return result;
    }

} // anonymous namespace

PYBIND11_MODULE(pyrbd_core_cpp, m)
{
    m.doc() = "PyRBD-Core — Unified reliability analysis C++ library";

    // ================================================================
    // ProbabilityMap binding
    // ================================================================
    py::class_<ProbabilityMap>(m, "ProbabilityMap")
        .def(py::init([](const std::map<int, double>& avail) {
            return ProbabilityMap(offsetProbMapIn(avail));
        }))
        .def("print", &ProbabilityMap::print)
        .def("__getitem__", [](const ProbabilityMap& pm, int i) {
            return pm[i + 1]; // offset for Python access
        });

    // ================================================================
    // SDP class binding
    // ================================================================
    py::class_<SDP>(m, "SDP")
        .def(py::init<bool, std::vector<int>>())
        .def("isComplementary", &SDP::isComplementary)
        .def("getSet", &SDP::getSet, py::return_value_policy::reference_internal);

    // ================================================================
    // Sets module (minimalpaths, minimalcuts)
    // ================================================================
    auto sets_mod = m.def_submodule("sets", "Sets discovery algorithms");

    sets_mod.def("minimalpaths",
        [](const AdjList& adj, NodeID src, NodeID dst) {
            AdjList adj_int = offsetAdjIn(adj);
            auto result = sets::minimalpaths(adj_int, toInternal(src), toInternal(dst));
            return offsetSetsOut(result);
        },
        "Find all minimal (simple) paths between src and dst",
        py::arg("adj"), py::arg("src"), py::arg("dst"));

    sets_mod.def("minimalcuts",
        [](const AdjList& adj, NodeID src, NodeID dst, int num_nodes, const std::string& method) {
            AdjList adj_int = offsetAdjIn(adj);
            auto result = sets::minimalcuts(adj_int, toInternal(src), toInternal(dst),
                                            num_nodes, method);
            return offsetSetsOut(result);
        },
        "Find minimal cut sets between src and dst",
        py::arg("adj"), py::arg("src"), py::arg("dst"),
        py::arg("num_nodes"), py::arg("method") = "cnf_tree");

    // ================================================================
    // MCS module
    // ================================================================
    auto mcs_mod = m.def_submodule("mcs", "MCS availability algorithm");

    mcs_mod.def("to_probaset",
        [](NodeID src, NodeID dst, const std::vector<Set>& min_cut_sets) {
            auto sets_int = offsetSetsIn(min_cut_sets);
            auto result = mcs::toProbaSet(toInternal(src), toInternal(dst), sets_int);
            return offsetSetsOut(result);
        },
        "Convert minimal cut sets to probability sets",
        py::arg("src"), py::arg("dst"), py::arg("min_cut_sets"));

    mcs_mod.def("to_probaset_debug",
        [](NodeID src, NodeID dst, const std::vector<Set>& min_cut_sets) {
            auto sets_int = offsetSetsIn(min_cut_sets);
            return mcs::toProbaSetDebug(toInternal(src), toInternal(dst), sets_int);
        },
        "Debug version: convert minimal cut sets to probability sets",
        py::arg("src"), py::arg("dst"), py::arg("min_cut_sets"));

    mcs_mod.def("eval_avail",
        [](NodeID src, NodeID dst, const std::map<int, double>& probabilities,
           const std::vector<Set>& min_cut_sets) {
            ProbabilityMap probMap(offsetProbMapIn(probabilities));
            auto sets_int = offsetSetsIn(min_cut_sets);
            return mcs::evalAvail(toInternal(src), toInternal(dst), probMap, sets_int);
        },
        "Evaluate availability using MCS approach",
        py::arg("src"), py::arg("dst"), py::arg("probabilities"), py::arg("min_cut_sets"));

    mcs_mod.def("eval_avail_topo",
        [](const NodePairs& node_pairs, const std::map<int, double>& probabilities,
           const std::vector<std::vector<Set>>& min_cut_sets_list) {
            ProbabilityMap probMap(offsetProbMapIn(probabilities));
            auto pairs_int = offsetPairsIn(node_pairs);
            auto sets_int = offsetSetsListIn(min_cut_sets_list);
            auto result = mcs::evalAvailTopo(pairs_int, probMap, sets_int);
            return offsetTriplesOut(result);
        },
        "Evaluate availability for all node pairs using MCS (serial)",
        py::arg("node_pairs"), py::arg("probabilities"), py::arg("min_cut_sets_list"));

    mcs_mod.def("eval_avail_topo_parallel",
        [](const NodePairs& node_pairs, const std::map<int, double>& probabilities,
           const std::vector<std::vector<Set>>& min_cut_sets_list) {
            ProbabilityMap probMap(offsetProbMapIn(probabilities));
            auto pairs_int = offsetPairsIn(node_pairs);
            auto sets_int = offsetSetsListIn(min_cut_sets_list);
            auto result = mcs::evalAvailTopoParallel(pairs_int, probMap, sets_int);
            return offsetTriplesOut(result);
        },
        "Evaluate availability for all node pairs using MCS (parallel)",
        py::arg("node_pairs"), py::arg("probabilities"), py::arg("min_cut_sets_list"),
        py::call_guard<py::gil_scoped_release>());

    // ================================================================
    // Pathset module
    // ================================================================
    auto pathset_mod = m.def_submodule("pathset", "Pathset availability algorithm");

    pathset_mod.def("to_probaset",
        [](NodeID src, NodeID dst, const std::vector<Set>& path_sets) {
            auto sets_int = offsetSetsIn(path_sets);
            auto result = pathset::toProbaSet(toInternal(src), toInternal(dst), sets_int);
            return offsetSetsOut(result);
        },
        "Convert path sets to probability sets",
        py::arg("src"), py::arg("dst"), py::arg("path_sets"));

    pathset_mod.def("to_probaset_debug",
        [](NodeID src, NodeID dst, const std::vector<Set>& path_sets) {
            auto sets_int = offsetSetsIn(path_sets);
            return pathset::toProbaSetDebug(toInternal(src), toInternal(dst), sets_int);
        },
        "Debug version: convert path sets to probability sets",
        py::arg("src"), py::arg("dst"), py::arg("path_sets"));

    pathset_mod.def("eval_avail",
        [](NodeID src, NodeID dst, const std::map<int, double>& probabilities,
           const std::vector<Set>& path_sets) {
            ProbabilityMap probMap(offsetProbMapIn(probabilities));
            auto sets_int = offsetSetsIn(path_sets);
            return pathset::evalAvail(toInternal(src), toInternal(dst), probMap, sets_int);
        },
        "Evaluate availability using Pathset approach",
        py::arg("src"), py::arg("dst"), py::arg("probabilities"), py::arg("path_sets"));

    pathset_mod.def("eval_avail_topo",
        [](const NodePairs& node_pairs, const std::map<int, double>& probabilities,
           const std::vector<std::vector<Set>>& pathsets_list) {
            ProbabilityMap probMap(offsetProbMapIn(probabilities));
            auto pairs_int = offsetPairsIn(node_pairs);
            auto sets_int = offsetSetsListIn(pathsets_list);
            auto result = pathset::evalAvailTopo(pairs_int, probMap, sets_int);
            return offsetTriplesOut(result);
        },
        "Evaluate availability for all node pairs using Pathset (serial)",
        py::arg("node_pairs"), py::arg("probabilities"), py::arg("pathsets_list"));

    pathset_mod.def("eval_avail_topo_parallel",
        [](const NodePairs& node_pairs, const std::map<int, double>& probabilities,
           const std::vector<std::vector<Set>>& pathsets_list) {
            ProbabilityMap probMap(offsetProbMapIn(probabilities));
            auto pairs_int = offsetPairsIn(node_pairs);
            auto sets_int = offsetSetsListIn(pathsets_list);
            auto result = pathset::evalAvailTopoParallel(pairs_int, probMap, sets_int);
            return offsetTriplesOut(result);
        },
        "Evaluate availability for all node pairs using Pathset (parallel)",
        py::arg("node_pairs"), py::arg("probabilities"), py::arg("pathsets_list"),
        py::call_guard<py::gil_scoped_release>());

    // ================================================================
    // SDP module
    // ================================================================
    auto sdp_mod = m.def_submodule("sdp", "SDP availability algorithm");

    sdp_mod.def("to_sdp_set",
        [](NodeID src, NodeID dst, const std::vector<Set>& path_sets) {
            auto sets_int = offsetSetsIn(path_sets);
            return sdp::toSDPSet(toInternal(src), toInternal(dst), sets_int);
        },
        "Convert path sets to SDP sets (serial)",
        py::arg("src"), py::arg("dst"), py::arg("path_sets"));

    sdp_mod.def("to_sdp_set_parallel",
        [](NodeID src, NodeID dst, const std::vector<Set>& path_sets) {
            auto sets_int = offsetSetsIn(path_sets);
            return sdp::toSDPSetParallel(toInternal(src), toInternal(dst), sets_int);
        },
        "Convert path sets to SDP sets (parallel)",
        py::arg("src"), py::arg("dst"), py::arg("path_sets"),
        py::call_guard<py::gil_scoped_release>());

    sdp_mod.def("eval_avail",
        [](NodeID src, NodeID dst, const std::map<int, double>& probabilities,
           std::vector<Set> path_sets) {
            ProbabilityMap probMap(offsetProbMapIn(probabilities));
            auto sets_int = offsetSetsIn(path_sets);
            return sdp::evalAvail(toInternal(src), toInternal(dst), probMap, sets_int);
        },
        "Evaluate availability using SDP approach",
        py::arg("src"), py::arg("dst"), py::arg("probabilities"), py::arg("path_sets"));

    sdp_mod.def("eval_avail_parallel",
        [](NodeID src, NodeID dst, const std::map<int, double>& probabilities,
           std::vector<Set> path_sets) {
            ProbabilityMap probMap(offsetProbMapIn(probabilities));
            auto sets_int = offsetSetsIn(path_sets);
            return sdp::evalAvailParallel(toInternal(src), toInternal(dst), probMap, sets_int);
        },
        "Evaluate availability using SDP approach (parallel)",
        py::arg("src"), py::arg("dst"), py::arg("probabilities"), py::arg("path_sets"),
        py::call_guard<py::gil_scoped_release>());

    sdp_mod.def("eval_avail_topo",
        [](const NodePairs& node_pairs, const std::map<int, double>& probabilities,
           std::vector<std::vector<Set>> pathsets_list) {
            ProbabilityMap probMap(offsetProbMapIn(probabilities));
            auto pairs_int = offsetPairsIn(node_pairs);
            auto sets_int = offsetSetsListIn(pathsets_list);
            auto result = sdp::evalAvailTopo(pairs_int, probMap, sets_int);
            return offsetTriplesOut(result);
        },
        "Evaluate availability for all node pairs using SDP (serial)",
        py::arg("node_pairs"), py::arg("probabilities"), py::arg("pathsets_list"));

    sdp_mod.def("eval_avail_topo_parallel",
        [](const NodePairs& node_pairs, const std::map<int, double>& probabilities,
           std::vector<std::vector<Set>> pathsets_list) {
            ProbabilityMap probMap(offsetProbMapIn(probabilities));
            auto pairs_int = offsetPairsIn(node_pairs);
            auto sets_int = offsetSetsListIn(pathsets_list);
            auto result = sdp::evalAvailTopoParallel(pairs_int, probMap, sets_int);
            return offsetTriplesOut(result);
        },
        "Evaluate availability for all node pairs using SDP (parallel)",
        py::arg("node_pairs"), py::arg("probabilities"), py::arg("pathsets_list"),
        py::call_guard<py::gil_scoped_release>());
}
