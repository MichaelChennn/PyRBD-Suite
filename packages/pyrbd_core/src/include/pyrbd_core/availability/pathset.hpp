#pragma once
#include <pyrbd_core/common.hpp>

namespace pyrbd_core::pathset
{
    using PathSets = std::vector<Set>;

    /**
     * @brief Convert path sets to probability sets via iterative disjoint-set construction.
     */
    ProbaSets toProbaSet(NodeID src, NodeID dst, PathSets pathSets);

    /**
     * @brief Debug version returning per-iteration timing info.
     */
    DebugInfo toProbaSetDebug(NodeID src, NodeID dst, PathSets pathSets);

    /**
     * @brief Evaluate probability from probability sets.
     * Result = sum(product_of_terms_per_set).
     */
    double probaSetToAvail(NodeID src, NodeID dst,
                           const ProbabilityMap& probaMap,
                           const ProbaSets& probaSets);

    /**
     * @brief Evaluate availability for a single (src, dst) pair via Pathset.
     */
    double evalAvail(NodeID src, NodeID dst,
                     const ProbabilityMap& probaMap,
                     const PathSets& pathSets);

    /**
     * @brief Evaluate availability for all node pairs (sequential).
     */
    std::vector<AvailTriple> evalAvailTopo(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        const std::vector<PathSets>& pathsetsList);

    /**
     * @brief Evaluate availability for all node pairs (OpenMP parallel).
     */
    std::vector<AvailTriple> evalAvailTopoParallel(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        const std::vector<PathSets>& pathsetsList);

} // namespace pyrbd_core::pathset
