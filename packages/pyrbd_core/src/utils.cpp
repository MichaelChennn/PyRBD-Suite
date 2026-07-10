#include <pyrbd_core/utils.hpp>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <unordered_set>

namespace pyrbd_core::utils
{

    bool isSubSet(const SDP& sdp1, const SDP& sdp2)
    {
        if ((sdp1.isComplementary() && sdp2.isComplementary()) ||
            (!sdp1.isComplementary() && !sdp2.isComplementary()))
        {
            std::unordered_set<NodeID> set2Lookup(sdp2.begin(), sdp2.end());
            for (const auto& elem : sdp1)
            {
                if (set2Lookup.find(elem) == set2Lookup.end())
                    return false;
            }
            return true;
        }
        return false;
    }

    bool hasCommonElement(const std::vector<SDP>& sdps)
    {
        std::vector<const SDP*> complementarySDPs;
        for (const auto& sdp : sdps)
        {
            if (sdp.isComplementary())
                complementarySDPs.push_back(&sdp);
        }

        std::vector<NodeID> commonElements;
        for (size_t i = 0; i < complementarySDPs.size(); ++i)
        {
            for (size_t j = i + 1; j < complementarySDPs.size(); ++j)
            {
                commonElements.clear();
                std::set_intersection(
                    complementarySDPs[i]->begin(), complementarySDPs[i]->end(),
                    complementarySDPs[j]->begin(), complementarySDPs[j]->end(),
                    std::back_inserter(commonElements));
                if (!commonElements.empty())
                    return true;
            }
        }
        return false;
    }

    std::vector<Set> readPathsetsFromFile(const std::string& filename)
    {
        std::vector<Set> pathsets;
        std::ifstream file(filename);
        if (!file.is_open())
            throw std::runtime_error("Could not open file: " + filename);

        std::string line;
        while (std::getline(file, line))
        {
            Set pathset;
            std::istringstream iss(line);
            NodeID node;
            while (iss >> node)
                pathset.push_back(node);
            if (!pathset.empty())
                pathsets.push_back(pathset);
        }
        file.close();
        return pathsets;
    }

    void writeSDPSetsToFile(const std::vector<std::vector<SDP>>& sdpSets,
                            const std::string& filename)
    {
        std::ofstream file(filename);
        if (!file.is_open())
            throw std::runtime_error("Could not open file for writing: " + filename);

        for (size_t i = 0; i < sdpSets.size(); ++i)
        {
            const auto& sdpSet = sdpSets[i];
            file << "SDPSet " << i << " (size: " << sdpSet.size() << "): ";
            for (size_t j = 0; j < sdpSet.size(); ++j)
            {
                if (j > 0) file << " ";
                file << sdpSet[j];
            }
            file << std::endl;
        }
        file.close();
    }

    std::string toString(const Set& set)
    {
        std::ostringstream oss;
        oss << "[";
        for (size_t i = 0; i < set.size(); ++i) {
            if (i > 0) oss << ", ";
            oss << set[i];
        }
        oss << "]";
        return oss.str();
    }

    std::string toString(const SDPSets& sdpSets)
    {
        std::ostringstream oss;
        oss << "[";
        for (size_t i = 0; i < sdpSets.size(); ++i) {
            if (i > 0) oss << " ";
            oss << sdpSets[i];
        }
        oss << "]";
        return oss.str();
    }

    std::string toString(const std::vector<SDPSets>& vectorSDPSets)
    {
        std::ostringstream oss;
        oss << "Vector<SDPSets> {\n";
        for (size_t i = 0; i < vectorSDPSets.size(); ++i) {
            oss << "  SDPSet " << i << " (size: " << vectorSDPSets[i].size() << "): "
                << toString(vectorSDPSets[i]);
            if (i < vectorSDPSets.size() - 1) oss << ",";
            oss << "\n";
        }
        oss << "}";
        return oss.str();
    }

    std::string toString(const PathSets& pathSets)
    {
        std::ostringstream oss;
        oss << "PathSets {\n";
        for (size_t i = 0; i < pathSets.size(); ++i) {
            oss << "  " << i << ": " << toString(pathSets[i]);
            if (i < pathSets.size() - 1) oss << ",";
            oss << "\n";
        }
        oss << "}";
        return oss.str();
    }

} // namespace pyrbd_core::utils
