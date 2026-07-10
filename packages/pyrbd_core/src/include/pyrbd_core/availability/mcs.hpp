#pragma once
#include <pyrbd_core/common.hpp>

namespace pyrbd_core::mcs
{
    using MinCutSets = std::vector<Set>;

    /**
     * @brief Convert minimal cut sets to probability sets.
     * Removes {src} and {dst}, inverts signs, then iteratively
     * applies makeDisjointSet.
     */
    ProbaSets toProbaSet(NodeID src, NodeID dst, MinCutSets minCutSets);

    /**
     * @brief Debug version returning per-iteration timing info.
     */
    DebugInfo toProbaSetDebug(NodeID src, NodeID dst, MinCutSets minCutSets);

    /**
     * @brief Evaluate probability from probability sets.
     * Result = P(src) * P(dst) * (1 - sum(product_of_terms_per_set)).
     */
    double probaSetToAvail(NodeID src, NodeID dst,
                           const ProbabilityMap& probaMap,
                           const ProbaSets& probaSets);

    /**
     * @brief Evaluate availability for a single (src, dst) pair via MCS.
     */
    double evalAvail(NodeID src, NodeID dst,
                     const ProbabilityMap& probaMap,
                     const MinCutSets& minCutSets);

    /**
     * @brief Evaluate availability for all node pairs (sequential).
     */
    std::vector<AvailTriple> evalAvailTopo(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        const std::vector<MinCutSets>& minCutSetsList);

    /**
     * @brief Evaluate availability for all node pairs (OpenMP parallel).
     */
    std::vector<AvailTriple> evalAvailTopoParallel(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        const std::vector<MinCutSets>& minCutSetsList);

} // namespace pyrbd_core::mcs
