#include <pyrbd_core/sets.hpp>
#include <algorithm>
#include <cmath>
#include <unordered_set>
#include <unordered_map>
#include <numeric>

namespace pyrbd_core::sets
{
    // ================================================================
    // Combination method — C++ port of _cutsets_combination.py
    //
    // Uses incidence matrix approach to find combinations of nodes
    // that disconnect all paths.
    // ================================================================

    MinCutSets minimalcuts_combination(const AdjList& adj, NodeID src, NodeID dst,
                                       int num_nodes, int order)
    {
        if (order < 0)
            order = static_cast<int>(std::ceil(num_nodes / 2.0));

        MinCutSets minimal;

        // Get paths
        PathSets paths = minimalpaths(adj, src, dst);
        std::cout << "[DEBUG] Got " << paths.size() << " paths from minimalpaths." << std::endl;
        for (size_t i = 0; i < paths.size(); ++i) {
            std::cout << "[DEBUG] Path " << i << ":";
            for (int n : paths[i]) std::cout << " " << n;
            std::cout << std::endl;
        }

        if (paths.size() == 1 && paths[0].size() == 2 &&
            paths[0][0] == src && paths[0][1] == dst)
        {
            return {{src}, {dst}};
        }

        // Build valid nodes (all nodes except src and dst)
        std::vector<NodeID> valid_nodes;
        for (int n = 1; n <= num_nodes; ++n)
        {
            if (n != src && n != dst)
                valid_nodes.push_back(n);
        }

        // Build incidence matrix: paths × valid_nodes
        // incidence[p][n] = true if node n is in path p
        size_t P = paths.size();
        size_t N = valid_nodes.size();

        std::unordered_map<int, size_t> node_to_col;
        for (size_t i = 0; i < N; ++i)
            node_to_col[valid_nodes[i]] = i;

        std::vector<std::vector<bool>> incidence(P, std::vector<bool>(N, false));
        for (size_t p = 0; p < P; ++p)
        {
            for (int node : paths[p])
            {
                auto it = node_to_col.find(node);
                if (it != node_to_col.end())
                    incidence[p][it->second] = true;
            }
        }

        // Find order-1 cut sets (single nodes that are in ALL paths)
        std::vector<NodeID> firstpairs;
        for (size_t n = 0; n < N; ++n)
        {
            bool all_true = true;
            for (size_t p = 0; p < P; ++p)
            {
                if (!incidence[p][n]) { all_true = false; break; }
            }
            if (all_true)
                minimal.push_back({valid_nodes[n]});
            else
                firstpairs.push_back(valid_nodes[n]);
        }

        std::cout << "[DEBUG] firstpairs.size() = " << firstpairs.size() << std::endl;
        // Iteratively find higher-order cut sets
        for (int k = 1; k < order; ++k)
        {
            size_t combo_size = k + 1;
            if (firstpairs.size() < combo_size) break;

            // Generate all combinations of size combo_size from firstpairs
            std::vector<Set> newpairs;
            {
                std::vector<size_t> indices(combo_size);
                std::iota(indices.begin(), indices.end(), 0);

                while (true)
                {
                    Set combo;
                    for (size_t idx : indices)
                        combo.push_back(firstpairs[idx]);

                    // Check if combo is a superset of any existing minimal cut set
                    bool is_superset = false;
                    std::unordered_set<int> combo_set(combo.begin(), combo.end());
                    for (const auto& m : minimal)
                    {
                        bool subset = true;
                        for (int e : m)
                        {
                            if (combo_set.count(e) == 0) { subset = false; break; }
                        }
                        if (subset) { is_superset = true; break; }
                    }

                    if (!is_superset) {
                        newpairs.push_back(combo);
                    } else {
                        if (combo_set.count(13) && combo_set.count(14) && combo_set.count(16) && combo.size() == 3) {
                            std::cout << "[DEBUG] 13, 14, 16 skipped due to superset!" << std::endl;
                        }
                    }

                    // Next combination
                    int i = combo_size - 1;
                    while (i >= 0 && indices[i] == firstpairs.size() - combo_size + i)
                        --i;
                    if (i < 0) break;
                    ++indices[i];
                    for (size_t j = i + 1; j < combo_size; ++j)
                        indices[j] = indices[j - 1] + 1;
                }
            }

            // Build incidence matrix for new pairs
            for (const auto& combo : newpairs)
            {
                bool all_paths_covered = true;
                for (size_t p = 0; p < P; ++p)
                {
                    bool covered = false;
                    for (int node : combo)
                    {
                        auto it = node_to_col.find(node);
                        if (it != node_to_col.end() && incidence[p][it->second])
                        {
                            covered = true;
                            break;
                        }
                    }
                    if (!covered) { all_paths_covered = false; break; }
                }

                if (all_paths_covered) {
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
