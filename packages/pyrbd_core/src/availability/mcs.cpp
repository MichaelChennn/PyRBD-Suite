#include <pyrbd_core/availability/mcs.hpp>
#include <algorithm>
#include <chrono>
#include <omp.h>

namespace pyrbd_core::mcs
{

    ProbaSets toProbaSet(NodeID src, NodeID dst, MinCutSets minCutSets)
    {
        // Remove {src} and {dst}
        minCutSets.erase(
            std::remove(minCutSets.begin(), minCutSets.end(), std::vector<int>{src}),
            minCutSets.end());
        minCutSets.erase(
            std::remove(minCutSets.begin(), minCutSets.end(), std::vector<int>{dst}),
            minCutSets.end());

        if (minCutSets.empty())
            return {};

        // Inverse the minimal cut sets
        for (auto& set : minCutSets)
            std::transform(set.begin(), set.end(), set.begin(), [](int x) { return -x; });

        ProbaSets probaSets;
        probaSets.reserve(minCutSets.size() * 3);

        while (minCutSets.size() > 0)
        {
            if (minCutSets.size() == 1)
            {
                probaSets.push_back(minCutSets[0]);
                break;
            }

            Set selectedSet = minCutSets.front();
            probaSets.push_back(selectedSet);

            std::vector<std::vector<int>> remainingSets(minCutSets.begin() + 1, minCutSets.end());
            minCutSets.clear();

            for (const auto& set : remainingSets)
            {
                DisjointSets disjointSets = makeDisjointSet(selectedSet, set);
                minCutSets.insert(minCutSets.end(), disjointSets.begin(), disjointSets.end());
            }
        }

        return probaSets;
    }

    DebugInfo toProbaSetDebug(NodeID src, NodeID dst, MinCutSets minCutSets)
    {
        DebugInfo debugInfo;

        minCutSets.erase(
            std::remove(minCutSets.begin(), minCutSets.end(), std::vector<int>{src}),
            minCutSets.end());
        minCutSets.erase(
            std::remove(minCutSets.begin(), minCutSets.end(), std::vector<int>{dst}),
            minCutSets.end());

        if (minCutSets.empty())
            return debugInfo;

        for (auto& set : minCutSets)
            std::transform(set.begin(), set.end(), set.begin(), [](int x) { return -x; });

        ProbaSets probaSets;
        probaSets.reserve(minCutSets.size() * 3);
        int iteration = 0;

        while (minCutSets.size() > 0)
        {
            auto start = std::chrono::high_resolution_clock::now();

            if (minCutSets.size() == 1)
            {
                probaSets.push_back(minCutSets[0]);
                break;
            }

            const Set& selectedSet = minCutSets.front();
            probaSets.push_back(selectedSet);

            std::vector<std::vector<int>> remainingSets(minCutSets.begin() + 1, minCutSets.end());
            minCutSets.clear();

            for (const auto& set : remainingSets)
            {
                DisjointSets disjoint_sets = makeDisjointSet(selectedSet, set);
                minCutSets.insert(minCutSets.end(), disjoint_sets.begin(), disjoint_sets.end());
            }

            auto end = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> duration = end - start;
            debugInfo[iteration] = {static_cast<int>(probaSets.size()), duration.count()};
            iteration++;
        }

        return debugInfo;
    }

    double probaSetToAvail(NodeID src, NodeID dst,
                           const ProbabilityMap& probaMap,
                           const ProbaSets& probaSet)
    {
        double unavil = 0.0;
        for (const auto& set : probaSet)
        {
            double temp = 1.0;
            for (const auto& num : set)
                temp *= probaMap[num];
            unavil += temp;
        }

        double avail = 1.0 - unavil;
        return probaMap[src] * probaMap[dst] * avail;
    }

    double evalAvail(NodeID src, NodeID dst,
                     const ProbabilityMap& probaMap,
                     const MinCutSets& minCutSets)
    {
        ProbaSets probaSets = toProbaSet(src, dst, minCutSets);
        return probaSetToAvail(src, dst, probaMap, probaSets);
    }

    std::vector<AvailTriple> evalAvailTopo(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        const std::vector<MinCutSets>& minCutSetsList)
    {
        std::vector<AvailTriple> availList;
        for (size_t i = 0; i < nodePairs.size(); ++i)
        {
            const auto& [src, dst] = nodePairs[i];
            double availability = evalAvail(src, dst, probaMap, minCutSetsList[i]);
            availList.emplace_back(src, dst, availability);
        }
        return availList;
    }

    std::vector<AvailTriple> evalAvailTopoParallel(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        const std::vector<MinCutSets>& minCutSetsList)
    {
        std::vector<AvailTriple> availList(nodePairs.size());

        #pragma omp parallel for schedule(dynamic)
        for (size_t i = 0; i < nodePairs.size(); ++i)
        {
            const auto& [src, dst] = nodePairs[i];
            double availability = evalAvail(src, dst, probaMap, minCutSetsList[i]);
            availList[i] = std::make_tuple(src, dst, availability);
        }

        return availList;
    }

} // namespace pyrbd_core::mcs
