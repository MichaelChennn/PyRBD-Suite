#include <pyrbd_core/sets.hpp>
#include <algorithm>
#include <cmath>
#include <numeric>
#include <unordered_map>
#include <unordered_set>
#include <set>

namespace pyrbd_core::sets
{
    // ================================================================
    // Combination Matrix method — C++ port of _cutsets_combination_matrix.py
    //
    // Uses incidence matrices with logical OR operations to efficiently
    // test higher-order cut sets.
    // ================================================================

    MinCutSets minimalcuts_combination_matrix(const AdjList& adj, NodeID src, NodeID dst,
                                              int num_nodes, int order)
    {
        if (order < 0)
            order = static_cast<int>(std::ceil(num_nodes / 2.0));

        MinCutSets minimal;

        // Check direct connection
        bool direct = false;
        if (src >= 0 && static_cast<size_t>(src) < adj.size())
        {
            for (NodeID n : adj[src])
            {
                if (n == dst) { direct = true; break; }
            }
        }

        // If directly connected, check all paths
        PathSets paths = minimalpaths(adj, src, dst);
        if (paths.size() == 1 && paths[0].size() == 2)
        {
            return {{src}, {dst}};
        }

        // If not directly connected, proceed with combination matrix method
        if (!direct || paths.size() > 1)
        {
            // Build valid nodes (all except src, dst)
            std::vector<NodeID> valid_nodes;
            for (int n = 1; n <= num_nodes; ++n)
            {
                if (n != src && n != dst)
                    valid_nodes.push_back(n);
            }

            size_t P = paths.size();
            size_t N = valid_nodes.size();

            std::unordered_map<int, size_t> node_to_col;
            for (size_t i = 0; i < N; ++i)
                node_to_col[valid_nodes[i]] = i;

            // Origin incidence matrix
            std::vector<std::vector<bool>> incidence_origin(P, std::vector<bool>(N, false));
            for (size_t p = 0; p < P; ++p)
            {
                for (int node : paths[p])
                {
                    auto it = node_to_col.find(node);
                    if (it != node_to_col.end())
                        incidence_origin[p][it->second] = true;
                }
            }

            // Find order-1 cut sets (columns that are all true)
            std::vector<NodeID> firstpairs;
            for (size_t n = 0; n < N; ++n)
            {
                bool all_true = true;
                for (size_t p = 0; p < P; ++p)
                {
                    if (!incidence_origin[p][n]) { all_true = false; break; }
                }
                if (all_true)
                    minimal.push_back({valid_nodes[n]});
                else
                    firstpairs.push_back(valid_nodes[n]);
            }

            // Iterate for higher orders
            for (int k = 1; k < order; ++k)
            {
                size_t combo_size = k + 1;
                if (firstpairs.size() < combo_size) break;

                // Build upper set (supersets of known minimals)
                std::unordered_set<int> firstpairset(firstpairs.begin(), firstpairs.end());
                std::set<std::vector<int>> upperset;

                for (const auto& tup : minimal)
                {
                    std::set<int> tupset(tup.begin(), tup.end());
                    std::vector<int> remainder;
                    for (int fp : firstpairs)
                    {
                        if (tupset.count(fp) == 0)
                            remainder.push_back(fp);
                    }

                    int need = static_cast<int>(combo_size) - static_cast<int>(tup.size());
                    if (need <= 0) continue;
                    if (remainder.size() < static_cast<size_t>(need)) continue;

                    // Generate combinations of remainder of size need
                    std::vector<size_t> indices(need);
                    std::iota(indices.begin(), indices.end(), 0);

                    while (true)
                    {
                        std::vector<int> combo;
                        for (int idx : indices)
                            combo.push_back(remainder[idx]);
                        for (int t : tup)
                            combo.push_back(t);
                        std::sort(combo.begin(), combo.end());
                        upperset.insert(combo);

                        int i = need - 1;
                        while (i >= 0 && indices[i] == remainder.size() - need + i)
                            --i;
                        if (i < 0) break;
                        ++indices[i];
                        for (int j = i + 1; j < need; ++j)
                            indices[j] = indices[j - 1] + 1;
                    }
                }

                // Generate all combinations and filter out upper sets
                std::vector<Set> newpairs;
                {
                    std::vector<size_t> indices(combo_size);
                    std::iota(indices.begin(), indices.end(), 0);

                    while (true)
                    {
                        std::vector<int> combo;
                        for (size_t idx : indices)
                            combo.push_back(firstpairs[idx]);
                        std::sort(combo.begin(), combo.end());

                        if (upperset.count(combo) == 0)
                            newpairs.push_back(combo);

                        int i = combo_size - 1;
                        while (i >= 0 && indices[i] == firstpairs.size() - combo_size + i)
                            --i;
                        if (i < 0) break;
                        ++indices[i];
                        for (size_t j = i + 1; j < combo_size; ++j)
                            indices[j] = indices[j - 1] + 1;
                    }
                }

                // Check each new combination using OR on origin incidence columns
                for (const auto& combo : newpairs)
                {
                    bool all_paths_covered = true;
                    for (size_t p = 0; p < P; ++p)
                    {
                        bool covered = false;
                        for (int node : combo)
                        {
                            auto it = node_to_col.find(node);
                            if (it != node_to_col.end() && incidence_origin[p][it->second])
                            {
                                covered = true;
                                break;
                            }
                        }
                        if (!covered) { all_paths_covered = false; break; }
                    }

                    if (all_paths_covered)
                        minimal.push_back(combo);
                }
            }
        }

        // Sort results
        for (auto& s : minimal)
            std::sort(s.begin(), s.end());
        std::sort(minimal.begin(), minimal.end(),
                  [](const Set& a, const Set& b) {
                      if (a.size() != b.size()) return a.size() < b.size();
                      return a < b;
                  });

        MinCutSets result = {{src}, {dst}};
        result.insert(result.end(), minimal.begin(), minimal.end());
        return result;
    }

} // namespace pyrbd_core::sets
