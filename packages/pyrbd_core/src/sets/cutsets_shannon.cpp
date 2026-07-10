#include <pyrbd_core/sets.hpp>
#include <algorithm>

namespace pyrbd_core::sets
{
    // ================================================================
    // Shannon expansion — C++ port of _cutsets_shannon.py
    // ================================================================

    namespace {

        std::vector<Set> shannonExpansion(const std::vector<Set>& pathsets, int max_node)
        {
            auto [pivot_elem, counts] = mostCommonElement(pathsets, max_node);

            if (counts < 2)
            {
                return multiplyPathsets(pathsets);
            }

            std::vector<Set> left_subset, right_subset;
            for (const auto& subset : pathsets)
            {
                // Left: remove pivot_elem from all sets
                Set left_s;
                for (int e : subset)
                    if (e != pivot_elem) left_s.push_back(e);
                left_subset.push_back(std::move(left_s));

                // Right: only sets not containing pivot_elem
                bool has_pivot = false;
                for (int e : subset)
                    if (e == pivot_elem) { has_pivot = true; break; }
                if (!has_pivot)
                    right_subset.push_back(subset);
            }
            right_subset.push_back({pivot_elem});

            // Multiply both subsets
            auto left_result = multiplyPathsets(left_subset);
            auto right_result = multiplyPathsets(right_subset);

            // Combine with absorption
            AbsorbList absorbed;
            absorbed.addMany(left_result);
            absorbed.addMany(right_result);

            return absorbed.toSetList();
        }

    } // anonymous namespace

    MinCutSets minimalcuts_shannon(const AdjList& adj, NodeID src, NodeID dst, int num_nodes)
    {
        PathSets mps = minimalpaths(adj, src, dst);

        if (mps.size() == 1 && mps[0].size() == 2 &&
            mps[0][0] == src && mps[0][1] == dst)
        {
            return {{src}, {dst}};
        }

        std::sort(mps.begin(), mps.end(),
                  [](const Set& a, const Set& b) { return a.size() < b.size(); });

        std::vector<Set> pathsets;
        for (auto& mp : mps)
        {
            Set ps;
            for (int node : mp)
                if (node != src && node != dst) ps.push_back(node);
            std::sort(ps.begin(), ps.end());
            pathsets.push_back(std::move(ps));
        }

        auto result_sets = shannonExpansion(pathsets, num_nodes);

        // Sort
        for (auto& s : result_sets)
            std::sort(s.begin(), s.end());
        std::sort(result_sets.begin(), result_sets.end(),
                  [](const Set& a, const Set& b) {
                      if (a.size() != b.size()) return a.size() < b.size();
                      return a < b;
                  });

        MinCutSets result = {{src}, {dst}};
        result.insert(result.end(), result_sets.begin(), result_sets.end());
        return result;
    }

} // namespace pyrbd_core::sets
