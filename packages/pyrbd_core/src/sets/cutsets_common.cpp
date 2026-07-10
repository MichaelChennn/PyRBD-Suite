#include <pyrbd_core/sets.hpp>
#include <algorithm>
#include <numeric>
#include <unordered_set>

namespace pyrbd_core::sets
{
    // ================================================================
    // Shared helpers used by multiple cutset algorithms
    // ================================================================

    std::pair<int, int> mostCommonElement(const std::vector<Set>& sets, int max_node)
    {
        std::vector<int> counts(max_node + 1, 0);
        for (const auto& s : sets)
        {
            for (int elem : s)
            {
                if (elem >= 0 && elem <= max_node)
                    ++counts[elem];
            }
        }
        int best_idx = 0;
        for (int i = 1; i <= max_node; ++i)
        {
            if (counts[i] > counts[best_idx])
                best_idx = i;
        }
        return {best_idx, counts[best_idx]};
    }

    std::vector<Set> multiplyTwoPathsets(const std::vector<Set>& partial_set_list,
                                          const Set& factor_set)
    {
        std::unordered_set<int> factor_elems(factor_set.begin(), factor_set.end());

        AbsorbList absorbed;
        for (const auto& partial : partial_set_list)
        {
            // Check disjointness
            bool disjoint = true;
            for (int e : partial)
            {
                if (factor_elems.count(e))
                {
                    disjoint = false;
                    break;
                }
            }

            if (disjoint)
            {
                for (int f : factor_set)
                {
                    Set new_set = partial;
                    new_set.push_back(f);
                    std::sort(new_set.begin(), new_set.end());
                    absorbed.add(new_set);
                }
            }
            else
            {
                Set sorted_partial = partial;
                std::sort(sorted_partial.begin(), sorted_partial.end());
                absorbed.add(sorted_partial);
            }
        }
        return absorbed.toSetList();
    }

    std::vector<Set> multiplyPathsets(const std::vector<Set>& pathsets)
    {
        if (pathsets.empty()) return {};

        // Initialize with singleton sets from first path
        std::vector<Set> result;
        for (int elem : pathsets[0])
            result.push_back({elem});

        // Multiply with each subsequent set
        for (size_t i = 1; i < pathsets.size(); ++i)
            result = multiplyTwoPathsets(result, pathsets[i]);

        return result;
    }

    // ================================================================
    // Unified entry point
    // ================================================================
    MinCutSets minimalcuts(const AdjList& adj, NodeID src, NodeID dst,
                           int num_nodes, const std::string& method)
    {
        if (method == "cnf_tree")
            return minimalcuts_cnf_tree(adj, src, dst, num_nodes);
        else if (method == "shannon")
            return minimalcuts_shannon(adj, src, dst, num_nodes);
        else if (method == "multiplication")
            return minimalcuts_multiplication(adj, src, dst, num_nodes);
        else if (method == "combination")
            return minimalcuts_combination(adj, src, dst, num_nodes);
        else if (method == "combination_matrix")
            return minimalcuts_combination_matrix(adj, src, dst, num_nodes);
        else
            throw std::invalid_argument("Unknown minimalcuts method: " + method);
    }

} // namespace pyrbd_core::sets
