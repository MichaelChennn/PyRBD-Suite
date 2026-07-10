#pragma once
#include <pyrbd_core/common.hpp>
#include <pyrbd_core/utils.hpp>

namespace pyrbd_core::sdp
{
    using PathSets = std::vector<Set>;
    using SDPSets  = std::vector<SDP>;

    /**
     * @brief Eliminate redundant elements from complementary SDP sets.
     */
    SDPSets eliminateSDPSet(SDPSets& sdpSets);

    /**
     * @brief Absorb supersets within an SDP family.
     */
    SDPSets absorbSDPSet(SDPSets sdpSets);

    /**
     * @brief Recursively decompose SDP sets with common complementary elements.
     */
    std::vector<SDPSets> decomposeSDPSet(SDPSets sdpSets);

    /**
     * @brief Sort path sets for optimal SDP processing.
     */
    PathSets sortPathSet(PathSets pathSets);

    /**
     * @brief Convert path sets to SDP sets (sequential).
     */
    std::vector<SDPSets> toSDPSet(NodeID src, NodeID dst, PathSets pathSets);

    /**
     * @brief Convert path sets to SDP sets (OpenMP parallel).
     */
    std::vector<SDPSets> toSDPSetParallel(NodeID src, NodeID dst, PathSets pathSets);

    /**
     * @brief Evaluate availability from SDP sets.
     */
    double SDPSetToAvail(const ProbabilityMap& probaMap,
                         const std::vector<SDPSets>& sdpSets);

    /**
     * @brief Evaluate availability for single (src, dst) via SDP (sequential).
     */
    double evalAvail(NodeID src, NodeID dst,
                     const ProbabilityMap& probaMap,
                     PathSets& pathSets);

    /**
     * @brief Evaluate availability for single (src, dst) via SDP (parallel).
     */
    double evalAvailParallel(NodeID src, NodeID dst,
                             const ProbabilityMap& probaMap,
                             PathSets& pathSets);

    /**
     * @brief Evaluate availability for all node pairs (sequential).
     */
    std::vector<AvailTriple> evalAvailTopo(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        std::vector<PathSets>& pathsetsList);

    /**
     * @brief Evaluate availability for all node pairs (OpenMP parallel).
     */
    std::vector<AvailTriple> evalAvailTopoParallel(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        std::vector<PathSets>& pathsetsList);

} // namespace pyrbd_core::sdp
