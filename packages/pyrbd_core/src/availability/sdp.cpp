#include <pyrbd_core/availability/sdp.hpp>
#include <numeric>
#include <chrono>
#include <mutex>
#include <algorithm>
#include <queue>
#include <iostream>
#include <fstream>
#include <set>

namespace pyrbd_core::sdp
{

    using pyrbd_core::utils::isSubSet;
    using pyrbd_core::utils::hasCommonElement;
    using pyrbd_core::utils::toString;

    SDPSets eliminateSDPSet(SDPSets& sdpSets)
    {
        std::sort(sdpSets.begin(), sdpSets.end(), [](const SDP& a, const SDP& b) {
            return a.isComplementary() < b.isComplementary();
        });

        std::vector<NodeID> eliminatedElements;
        SDPSets eliminatedSet;
        eliminatedSet.reserve(sdpSets.size());
        std::vector<int> newSet;

        for (auto& sdp : sdpSets)
        {
            if (!sdp.isComplementary())
            {
                eliminatedElements.insert(eliminatedElements.end(), sdp.begin(), sdp.end());
                std::sort(eliminatedElements.begin(), eliminatedElements.end());
                eliminatedSet.push_back(std::move(sdp));
            }
            else
            {
                newSet.clear();
                std::set_difference(sdp.begin(), sdp.end(),
                    eliminatedElements.begin(), eliminatedElements.end(),
                    std::back_inserter(newSet));
                if (!newSet.empty())
                    eliminatedSet.emplace_back(true, std::move(newSet));
            }
        }
        return eliminatedSet;
    }

    SDPSets absorbSDPSet(SDPSets sdpSets)
    {
        SDPSets absorbedSDPs;
        absorbedSDPs.reserve(sdpSets.size());
        std::vector<bool> absorbed(sdpSets.size(), false);

        for (size_t i = 0; i < sdpSets.size(); ++i)
        {
            if (absorbed[i]) continue;
            const auto& currentSDP = sdpSets[i];

            for (size_t j = i + 1; j < sdpSets.size(); ++j)
            {
                if (absorbed[j]) continue;
                const auto& otherSDP = sdpSets[j];

                if (currentSDP.equals(otherSDP))
                {
                    absorbed[j] = true;
                }
                else if (isSubSet(currentSDP, otherSDP))
                {
                    absorbed[j] = true;
                }
                else if (isSubSet(otherSDP, currentSDP))
                {
                    absorbed[i] = true;
                    break;
                }
            }

            if (!absorbed[i])
                absorbedSDPs.push_back(sdpSets[i]);
        }
        return absorbedSDPs;
    }

    std::vector<SDPSets> decomposeSDPSet(SDPSets sdpSets)
    {
        std::vector<SDPSets> results;
        std::queue<SDPSets> queue;
        queue.push(std::move(sdpSets));

        while (!queue.empty())
        {
            SDPSets current = std::move(queue.front());
            queue.pop();

            if (!hasCommonElement(current))
            {
                results.push_back(std::move(current));
                continue;
            }

            SDPSets complementarySDPs, normalSDPs;
            for (auto& sdp : current)
            {
                if (sdp.isComplementary())
                    complementarySDPs.push_back(std::move(sdp));
                else
                    normalSDPs.push_back(std::move(sdp));
            }

            std::pair<SDP, SDP> commonSDPpair;
            std::vector<NodeID> commonElements;
            bool found = false;
            size_t foundI = 0, foundJ = 0;

            for (size_t i = 0; i < complementarySDPs.size() && !found; ++i)
            {
                for (size_t j = i + 1; j < complementarySDPs.size(); ++j)
                {
                    commonElements.clear();
                    std::set_intersection(
                        complementarySDPs[i].begin(), complementarySDPs[i].end(),
                        complementarySDPs[j].begin(), complementarySDPs[j].end(),
                        std::back_inserter(commonElements));
                    if (!commonElements.empty())
                    {
                        commonSDPpair = std::make_pair(complementarySDPs[i], complementarySDPs[j]);
                        found = true;
                        foundI = i;
                        foundJ = j;
                        break;
                    }
                }
            }

            if (!found)
            {
                results.push_back(std::move(current));
                continue;
            }

            for (size_t i = 0; i < complementarySDPs.size(); ++i)
            {
                if (i != foundI && i != foundJ)
                    normalSDPs.push_back(std::move(complementarySDPs[i]));
            }

            for (const auto& elem : commonElements)
            {
                commonSDPpair.first.remove(elem);
                commonSDPpair.second.remove(elem);
            }

            SDPSets decomposed1, decomposed2;
            decomposed1.reserve(normalSDPs.size() + 1);
            decomposed2.reserve(normalSDPs.size() + 3);

            decomposed1 = normalSDPs;
            decomposed1.emplace_back(true, commonElements);

            decomposed2 = std::move(normalSDPs);
            decomposed2.emplace_back(false, std::move(commonElements));
            decomposed2.push_back(std::move(commonSDPpair.first));
            decomposed2.push_back(std::move(commonSDPpair.second));

            decomposed1 = eliminateSDPSet(decomposed1);
            decomposed2 = eliminateSDPSet(decomposed2);

            decomposed1 = absorbSDPSet(decomposed1);
            decomposed2 = absorbSDPSet(decomposed2);

            queue.push(std::move(decomposed1));
            queue.push(std::move(decomposed2));
        }

        return results;
    }

    PathSets sortPathSet(PathSets pathSets)
    {
        if (pathSets.empty())
            return {};

        PathSets sortedPathSet;
        sortedPathSet.reserve(pathSets.size());

        for (auto& set : pathSets)
            std::sort(set.begin(), set.end());

        std::sort(pathSets.begin(), pathSets.end(), [](const std::vector<int>& a, const std::vector<int>& b) {
            if (a.size() != b.size()) return a.size() < b.size();
            return a < b;
        });

        std::map<int, PathSets> pathSetMap;
        for (auto& set : pathSets)
            pathSetMap[set.size()].push_back(std::move(set));

        auto it = pathSetMap.begin();
        if (it != pathSetMap.end())
        {
            std::move(it->second.begin(), it->second.end(), std::back_inserter(sortedPathSet));
            ++it;
        }

        for (; it != pathSetMap.end(); ++it)
        {
            auto& unsortedSets = it->second;
            Set maxCommonCounts;
            maxCommonCounts.reserve(unsortedSets.size());

            std::transform(unsortedSets.begin(), unsortedSets.end(),
                std::back_inserter(maxCommonCounts),
                [&sortedPathSet](const std::vector<int>& set) {
                    int maxCommonNum = 0;
                    for (const auto& precedSet : sortedPathSet)
                    {
                        int commonNum = std::count_if(set.begin(), set.end(),
                            [&precedSet](int elem) {
                                return std::find(precedSet.begin(), precedSet.end(), elem) != precedSet.end();
                            });
                        if (commonNum > maxCommonNum)
                            maxCommonNum = commonNum;
                    }
                    return maxCommonNum;
                });

            std::vector<size_t> indices(unsortedSets.size());
            std::iota(indices.begin(), indices.end(), 0);
            std::sort(indices.begin(), indices.end(),
                [&maxCommonCounts](size_t a, size_t b) {
                    return maxCommonCounts[a] < maxCommonCounts[b];
                });

            for (size_t idx : indices)
                sortedPathSet.push_back(std::move(unsortedSets[idx]));
        }

        return sortedPathSet;
    }

    std::vector<SDPSets> toSDPSet(NodeID src, NodeID dst, PathSets pathSets)
    {
        PathSets sortedPathSet = sortPathSet(std::move(pathSets));

        if (sortedPathSet.empty())
            return {};

        std::vector<SDPSets> finalSDPs = {{{false, sortedPathSet.front()}}};

        for (size_t i = 1; i < sortedPathSet.size(); ++i)
        {
            SDPSets resultSDPs;
            const auto& currentSet = sortedPathSet[i];
            resultSDPs.emplace_back(false, currentSet);

            for (size_t j = 0; j < i; ++j)
            {
                std::vector<int> RC;
                const auto& precedingSet = sortedPathSet[j];
                std::set_difference(precedingSet.begin(), precedingSet.end(),
                    currentSet.begin(), currentSet.end(),
                    std::back_inserter(RC));
                if (!RC.empty())
                    resultSDPs.emplace_back(true, std::move(RC));
            }

            resultSDPs = absorbSDPSet(std::move(resultSDPs));

            if (hasCommonElement(resultSDPs))
            {
                std::vector<SDPSets> decomposedResults = decomposeSDPSet(std::move(resultSDPs));
                std::move(decomposedResults.begin(), decomposedResults.end(),
                    std::back_inserter(finalSDPs));
            }
            else
            {
                finalSDPs.push_back(std::move(resultSDPs));
            }
        }

        return finalSDPs;
    }

    std::vector<SDPSets> toSDPSetParallel(NodeID src, NodeID dst, PathSets pathSets)
    {
        if (pathSets.size() < 200)
            return toSDPSet(src, dst, pathSets);

        PathSets sortedPathSet = sortPathSet(std::move(pathSets));
        std::vector<std::vector<SDPSets>> threadResults(sortedPathSet.size());
        threadResults[0] = {{{false, sortedPathSet.front()}}};

        #pragma omp parallel for schedule(dynamic)
        for (size_t i = 1; i < sortedPathSet.size(); ++i)
        {
            SDPSets resultSDPs;
            const auto& currentSet = sortedPathSet[i];
            resultSDPs.emplace_back(false, currentSet);

            for (size_t j = 0; j < i; ++j)
            {
                std::vector<int> RC;
                const auto& precedingSet = sortedPathSet[j];
                std::set_difference(precedingSet.begin(), precedingSet.end(),
                    currentSet.begin(), currentSet.end(),
                    std::back_inserter(RC));
                if (!RC.empty())
                    resultSDPs.emplace_back(true, std::move(RC));
            }

            resultSDPs = absorbSDPSet(std::move(resultSDPs));

            if (hasCommonElement(resultSDPs))
                threadResults[i] = decomposeSDPSet(std::move(resultSDPs));
            else
                threadResults[i] = {std::move(resultSDPs)};
        }

        std::vector<SDPSets> finalSDPs;
        for (const auto& threadResult : threadResults)
            std::move(threadResult.begin(), threadResult.end(), std::back_inserter(finalSDPs));

        return finalSDPs;
    }

    double SDPSetToAvail(const ProbabilityMap& probaMap,
                         const std::vector<SDPSets>& sdpSets)
    {
        double availability = 0.0;

        for (const auto& set : sdpSets)
        {
            double setAvailability = 1.0;
            for (const auto& sdp : set)
            {
                if (sdp.isComplementary())
                {
                    double tmp_avail = 1.0;
                    for (const auto& elem : sdp.getSet())
                        tmp_avail *= probaMap[elem];
                    setAvailability *= (1.0 - tmp_avail);
                }
                else
                {
                    for (const auto& elem : sdp.getSet())
                        setAvailability *= probaMap[elem];
                }
            }
            availability += setAvailability;
        }
        return availability;
    }

    double evalAvail(NodeID src, NodeID dst,
                     const ProbabilityMap& probaMap,
                     PathSets& pathSets)
    {
        std::vector<SDPSets> SDPs = toSDPSet(src, dst, pathSets);
        return SDPSetToAvail(probaMap, SDPs);
    }

    double evalAvailParallel(NodeID src, NodeID dst,
                             const ProbabilityMap& probaMap,
                             PathSets& pathSets)
    {
        std::vector<SDPSets> SDPs = toSDPSetParallel(src, dst, pathSets);
        return SDPSetToAvail(probaMap, SDPs);
    }

    std::vector<AvailTriple> evalAvailTopo(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        std::vector<PathSets>& pathsetsList)
    {
        std::vector<AvailTriple> availList;
        for (size_t i = 0; i < nodePairs.size(); ++i)
        {
            const auto& [src, dst] = nodePairs[i];
            auto& pathSets = pathsetsList[i];
            double availability = evalAvail(src, dst, probaMap, pathSets);
            availList.emplace_back(src, dst, availability);
        }
        return availList;
    }

    std::vector<AvailTriple> evalAvailTopoParallel(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        std::vector<PathSets>& pathsetsList)
    {
        std::vector<AvailTriple> availList(nodePairs.size());

        #pragma omp parallel for schedule(dynamic)
        for (size_t i = 0; i < nodePairs.size(); ++i)
        {
            const auto& [src, dst] = nodePairs[i];
            auto& pathSets = pathsetsList[i];
            double availability = evalAvail(src, dst, probaMap, pathSets);
            availList[i] = std::make_tuple(src, dst, availability);
        }
        return availList;
    }

} // namespace pyrbd_core::sdp
