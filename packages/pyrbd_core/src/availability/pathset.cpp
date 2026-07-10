#include <pyrbd_core/availability/pathset.hpp>
#include <algorithm>
#include <chrono>
#include <omp.h>

namespace pyrbd_core::pathset
{

    ProbaSets toProbaSet(NodeID src, NodeID dst, PathSets pathSets)
    {
        if (pathSets.empty())
            return {};

        ProbaSets probaSets;
        probaSets.reserve(pathSets.size() * 3);

        while (pathSets.size() > 0)
        {
            if (pathSets.size() == 1)
            {
                probaSets.push_back(pathSets[0]);
                break;
            }

            Set selectedSet = pathSets.front();
            probaSets.push_back(selectedSet);

            std::vector<std::vector<int>> remainingSets(pathSets.begin() + 1, pathSets.end());
            pathSets.clear();

            for (const auto& set : remainingSets)
            {
                DisjointSets disjointSets = makeDisjointSet(selectedSet, set);
                pathSets.insert(pathSets.end(), disjointSets.begin(), disjointSets.end());
            }
        }

        return probaSets;
    }

    DebugInfo toProbaSetDebug(NodeID src, NodeID dst, PathSets pathSets)
    {
        DebugInfo debugInfo;
        ProbaSets probaSets;
        probaSets.reserve(pathSets.size() * 3);
        int iteration = 0;

        while (pathSets.size() > 0)
        {
            auto start = std::chrono::high_resolution_clock::now();

            if (pathSets.size() == 1)
            {
                probaSets.push_back(pathSets[0]);
                break;
            }

            Set selectedSet = pathSets.front();
            probaSets.push_back(selectedSet);

            std::vector<std::vector<int>> remainingSets(pathSets.begin() + 1, pathSets.end());
            pathSets.clear();

            for (const auto& set : remainingSets)
            {
                DisjointSets disjointSets = makeDisjointSet(selectedSet, set);
                pathSets.insert(pathSets.end(), disjointSets.begin(), disjointSets.end());
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
                           const ProbaSets& probaSets)
    {
        double avail = 0.0;
        for (const auto& set : probaSets)
        {
            double temp = 1.0;
            for (const auto& num : set)
                temp *= probaMap[num];
            avail += temp;
        }
        return avail;
    }

    double evalAvail(NodeID src, NodeID dst,
                     const ProbabilityMap& probaMap,
                     const PathSets& pathSets)
    {
        ProbaSets probaSets = toProbaSet(src, dst, pathSets);
        return probaSetToAvail(src, dst, probaMap, probaSets);
    }

    std::vector<AvailTriple> evalAvailTopo(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        const std::vector<PathSets>& pathsetsList)
    {
        std::vector<AvailTriple> availList;
        for (size_t i = 0; i < nodePairs.size(); ++i)
        {
            const auto& [src, dst] = nodePairs[i];
            double availability = evalAvail(src, dst, probaMap, pathsetsList[i]);
            availList.emplace_back(src, dst, availability);
        }
        return availList;
    }

    std::vector<AvailTriple> evalAvailTopoParallel(
        const NodePairs& nodePairs,
        const ProbabilityMap& probaMap,
        const std::vector<PathSets>& pathsetsList)
    {
        std::vector<AvailTriple> availList(nodePairs.size());

        #pragma omp parallel for schedule(dynamic)
        for (size_t i = 0; i < nodePairs.size(); ++i)
        {
            const auto& [src, dst] = nodePairs[i];
            double availability = evalAvail(src, dst, probaMap, pathsetsList[i]);
            availList[i] = std::make_tuple(src, dst, availability);
        }

        return availList;
    }

} // namespace pyrbd_core::pathset
