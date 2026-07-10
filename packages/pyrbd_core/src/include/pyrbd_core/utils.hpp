#pragma once
#include <pyrbd_core/common.hpp>
#include <algorithm>
#include <unordered_set>

namespace pyrbd_core::utils
{
    // Convenience aliases
    using PathSets = std::vector<Set>;
    using SDPSets  = std::vector<SDP>;

    /**
     * @brief Check if sdp1 is a subset of sdp2.
     * Both must have the same complementary flag.
     */
    bool isSubSet(const SDP& sdp1, const SDP& sdp2);

    /**
     * @brief Check if any pair of complementary SDPs share a common element.
     */
    bool hasCommonElement(const std::vector<SDP>& sdps);

    /**
     * @brief Read pathsets from a file (space-separated integers per line).
     */
    std::vector<Set> readPathsetsFromFile(const std::string& filename);

    /**
     * @brief Write SDPSets to file.
     */
    void writeSDPSetsToFile(const std::vector<std::vector<SDP>>& sdpSets,
                            const std::string& filename = "SDPSets.txt");

    // toString helpers
    std::string toString(const Set& set);
    std::string toString(const SDPSets& sdpSets);
    std::string toString(const std::vector<SDPSets>& vectorSDPSets);
    std::string toString(const PathSets& pathSets);

} // namespace pyrbd_core::utils
