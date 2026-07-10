#pragma once
#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
#include <tuple>

namespace pyrbd_core
{
    // ================================================================
    // Core type aliases (unified from pyrbd3 + pyrbdpp)
    // ================================================================
    using NodeID       = int;
    using Set          = std::vector<NodeID>;
    using DisjointSets = std::vector<Set>;
    using ProbaSets    = std::vector<Set>;
    using DebugInfo    = std::map<NodeID, std::pair<NodeID, double>>;
    using AvailTriple  = std::tuple<NodeID, NodeID, double>;
    using NodePairs    = std::vector<std::pair<NodeID, NodeID>>;

    // Adjacency list: adj[u] = list of neighbours of u
    using AdjList = std::vector<std::vector<NodeID>>;

    // ================================================================
    // ProbabilityMap
    //
    // Maps node IDs to availability probabilities. The sign convention
    // (+id → available, −id → unavailable) is used by the disjoint-set
    // algorithms. Indices are **1-based** inside pyrbd_core; the pybind
    // bindings layer automatically offsets user-facing 0-based IDs.
    // ================================================================
    class ProbabilityMap
    {
    private:
        std::vector<double> pos_array;
        std::vector<double> neg_array;

    public:
        explicit ProbabilityMap(const std::map<int, double>& avail_arr)
            : pos_array(avail_arr.size() + 1), neg_array(avail_arr.size() + 1)
        {
            for (const auto& pair : avail_arr)
            {
                if (pair.first <= 0)
                    throw std::invalid_argument(
                        "ProbabilityMap: node IDs must be >= 1 (0-node bug guard)");
                if (static_cast<size_t>(pair.first) >= pos_array.size())
                {
                    pos_array.resize(pair.first + 1, 0.0);
                    neg_array.resize(pair.first + 1, 0.0);
                }
                pos_array[pair.first] = pair.second;
                neg_array[pair.first] = 1.0 - pair.second;
            }
        }

        ProbabilityMap(std::initializer_list<std::pair<const int, double>> init_list)
        {
            int max_id = 0;
            for (const auto& pair : init_list)
            {
                if (pair.first <= 0)
                    throw std::invalid_argument(
                        "ProbabilityMap: node IDs must be >= 1 (0-node bug guard)");
                max_id = std::max(max_id, pair.first);
            }

            pos_array.resize(max_id + 1, 0.0);
            neg_array.resize(max_id + 1, 0.0);

            for (const auto& pair : init_list)
            {
                pos_array[pair.first] = pair.second;
                neg_array[pair.first] = 1.0 - pair.second;
            }
        }

        double operator[](int i) const
        {
            if (i == 0)
                throw std::invalid_argument(
                    "ProbabilityMap: node 0 is not allowed (0-node bug)");
            if (static_cast<size_t>(std::abs(i)) >= pos_array.size())
                throw std::out_of_range("Index out of range in ProbabilityMap");
            return (i > 0) ? pos_array[i] : neg_array[-i];
        }

        void print() const
        {
            std::cout << "Positive Array: ";
            for (double elem : pos_array) std::cout << elem << " ";
            std::cout << std::endl;
            std::cout << "Negative Array: ";
            for (double elem : neg_array) std::cout << elem << " ";
            std::cout << std::endl;
        }
    };

    // ================================================================
    // SDP (Sum of Disjoint Products) entry
    // ================================================================
    class SDP
    {
    private:
        bool is_complementary;
        std::vector<int> set;

    public:
        SDP(bool is_comp, std::vector<int> s)
            : is_complementary(is_comp), set(std::move(s)) {}

        SDP() : is_complementary(false), set() {}

        bool isComplementary() const { return is_complementary; }
        const std::vector<int>& getSet() const { return set; }

        std::vector<int>::iterator begin() { return set.begin(); }
        std::vector<int>::iterator end()   { return set.end(); }
        std::vector<int>::const_iterator begin() const { return set.begin(); }
        std::vector<int>::const_iterator end()   const { return set.end(); }

        int operator[](size_t idx) const { return set[idx]; }
        size_t size() const { return set.size(); }

        void remove(int elem)
        {
            set.erase(std::remove(set.begin(), set.end(), elem), set.end());
        }

        bool equals(const SDP& other) const
        {
            if (is_complementary != other.is_complementary || set.size() != other.set.size())
                return false;
            return std::equal(set.begin(), set.end(), other.set.begin());
        }

        friend std::ostream& operator<<(std::ostream& os, const SDP& sdp)
        {
            if (sdp.is_complementary) os << "-";
            os << "{ ";
            for (const auto& elem : sdp.set) os << elem << " ";
            os << "}";
            return os;
        }

        void print() const
        {
            if (is_complementary) std::cout << "-";
            std::cout << "{ ";
            for (const auto& elem : set) std::cout << elem << " ";
            std::cout << "}";
        }
    };

    // ================================================================
    // makeDisjointSet
    // ================================================================
    /**
     * @brief Create disjoint sets from set1 and set2.
     *
     * Algorithm:
     * 1. RC = set1 \ set2
     * 2. Progressively append -RC[i] to set2 producing disjoint products.
     */
    DisjointSets makeDisjointSet(const Set& set1, Set set2);

} // namespace pyrbd_core
