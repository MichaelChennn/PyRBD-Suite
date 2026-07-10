#pragma once
#include <pyrbd_core/common.hpp>
#include <functional>
#include <string>

namespace pyrbd_core::sets
{
    // Convenience aliases
    using PathSets    = std::vector<Set>;
    using MinCutSets  = std::vector<Set>;

    // ================================================================
    // Minimal paths (DFS)
    // ================================================================

    /**
     * @brief Find all minimal (simple) paths between src and dst using DFS.
     * @param adj Adjacency list (1-indexed).
     * @param src Source node.
     * @param dst Destination node.
     * @return All simple paths as vector<vector<NodeID>>.
     */
    PathSets minimalpaths(const AdjList& adj, NodeID src, NodeID dst);

    // ================================================================
    // AbsorbList — maintains a family of sets where no set is
    // a subset/superset of another (absorption invariant).
    // ================================================================
    class AbsorbList
    {
    public:
        AbsorbList() = default;

        /**
         * @brief Insert a new set. Returns true if the family changed.
         */
        bool add(const Set& s);

        /**
         * @brief Batch insert multiple sets. Returns number of changes.
         */
        int addMany(const std::vector<Set>& sets);

        /**
         * @brief Return all stored sets.
         */
        std::vector<Set> toSetList() const;

        /**
         * @brief Number of stored sets.
         */
        size_t size() const { return count_; }

        void clear();

    private:
        // Buckets keyed by set size
        std::map<size_t, std::vector<Set>> buckets_;
        size_t count_ = 0;

        // Internal helpers
        void addInternal(const Set& s);
        void discardInternal(const Set& s);
        static bool isSubsetSorted(const Set& a, const Set& b);
    };

    // ================================================================
    // Minimal cut sets algorithms
    // ================================================================

    /**
     * @brief Unified entry point for minimal cut set computation.
     * @param adj Adjacency list (1-indexed).
     * @param src Source node.
     * @param dst Destination node.
     * @param num_nodes Total number of nodes in the graph.
     * @param method Algorithm to use: "cnf_tree", "shannon", "multiplication",
     *               "combination", "combination_matrix".
     * @return Minimal cut sets (including {src} and {dst}).
     */
    MinCutSets minimalcuts(const AdjList& adj, NodeID src, NodeID dst,
                           int num_nodes, const std::string& method = "cnf_tree");

    // Individual algorithm implementations
    MinCutSets minimalcuts_cnf_tree(const AdjList& adj, NodeID src, NodeID dst, int num_nodes);
    MinCutSets minimalcuts_shannon(const AdjList& adj, NodeID src, NodeID dst, int num_nodes);
    MinCutSets minimalcuts_multiplication(const AdjList& adj, NodeID src, NodeID dst, int num_nodes);
    MinCutSets minimalcuts_combination(const AdjList& adj, NodeID src, NodeID dst, int num_nodes, int order = -1);
    MinCutSets minimalcuts_combination_matrix(const AdjList& adj, NodeID src, NodeID dst, int num_nodes, int order = -1);

    // ================================================================
    // Internal helpers used by cut set algorithms
    // ================================================================

    /**
     * @brief Find the most common element across a list of sets.
     * @return (element, count)
     */
    std::pair<int, int> mostCommonElement(const std::vector<Set>& sets, int max_node);

    /**
     * @brief Multiply (expand) a list of path sets into cut sets.
     */
    std::vector<Set> multiplyPathsets(const std::vector<Set>& pathsets);

    /**
     * @brief Multiply partial sets with a factor set (absorption-aware).
     */
    std::vector<Set> multiplyTwoPathsets(const std::vector<Set>& partial_set_list,
                                          const Set& factor_set);

} // namespace pyrbd_core::sets
