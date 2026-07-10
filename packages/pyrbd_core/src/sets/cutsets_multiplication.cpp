#include <pyrbd_core/sets.hpp>
#include <algorithm>

namespace pyrbd_core::sets
{
    // ================================================================
    // Multiplication method — C++ port of _cutsets_multiplication.py
    // ================================================================

    MinCutSets minimalcuts_multiplication(const AdjList& adj, NodeID src, NodeID dst, int num_nodes)
    {
        PathSets mps = minimalpaths(adj, src, dst);

        if (mps.size() == 1 && mps[0].size() == 2 &&
            mps[0][0] == src && mps[0][1] == dst)
        {
            return {{src}, {dst}};
        }

        std::sort(mps.begin(), mps.end(),
                  [](const Set& a, const Set& b) { return a.size() < b.size(); });

        // Remove src and dst, sort each path
        std::vector<Set> pathsets;
        for (auto& mp : mps)
        {
            Set ps;
            for (int node : mp)
                if (node != src && node != dst) ps.push_back(node);
            std::sort(ps.begin(), ps.end());
            pathsets.push_back(std::move(ps));
        }

        // Multiply pathsets
        auto result_sets = multiplyPathsets(pathsets);

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
