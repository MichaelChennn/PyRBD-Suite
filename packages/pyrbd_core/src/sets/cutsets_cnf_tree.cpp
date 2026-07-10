#include <pyrbd_core/sets.hpp>
#include <algorithm>
#include <queue>
#include <memory>
#include <numeric>

namespace pyrbd_core::sets
{
    // ================================================================
    // CNF Decision Tree — C++ port of _cnf_decision_tree.py
    // ================================================================

    namespace {

        struct DecisionTreeNode
        {
            std::vector<Set> value;   // CNF clauses
            int max_val;
            int most_common_value;    // -1 if none
            std::vector<Set> evaluation;
            std::unique_ptr<DecisionTreeNode> left;
            std::unique_ptr<DecisionTreeNode> right;

            DecisionTreeNode(std::vector<Set> val, int max_v, int mcv = -1)
                : value(std::move(val)), max_val(max_v), most_common_value(mcv)
            {
                auto [common_elem, counts] = mostCommonElement(value, max_val);

                if (counts > 1)
                {
                    std::vector<Set> with_elem, without_elem;
                    for (const auto& subset : value)
                    {
                        bool has = false;
                        for (int e : subset)
                            if (e == common_elem) { has = true; break; }

                        if (has)
                        {
                            Set new_subset;
                            for (int e : subset)
                                if (e != common_elem) new_subset.push_back(e);
                            with_elem.push_back(std::move(new_subset));
                        }
                        else
                        {
                            without_elem.push_back(subset);
                        }
                    }

                    if (!without_elem.empty())
                        left = std::make_unique<DecisionTreeNode>(std::move(without_elem), max_val);
                    if (!with_elem.empty())
                        right = std::make_unique<DecisionTreeNode>(std::move(with_elem), max_val, common_elem);
                }
            }

            void evaluate()
            {
                if (!left && !right)
                {
                    if (evaluation.empty())
                        evaluateSelf();
                    return;
                }

                if (left && left->evaluation.empty())
                    left->evaluate();
                if (right && right->evaluation.empty())
                    right->evaluate();

                const std::vector<Set>* left_eval = left ? &left->evaluation : nullptr;
                const std::vector<Set>* right_eval = right ? &right->evaluation : nullptr;

                if ((!left_eval || left_eval->empty()) && (!right_eval || right_eval->empty()))
                {
                    if (evaluation.empty())
                        evaluateSelf();
                }
                else if (evaluation.empty())
                {
                    evaluateTwoLeaf(left_eval, right_eval);
                }
            }

        private:
            void evaluateSelf()
            {
                if (value.empty())
                {
                    evaluation.clear();
                    return;
                }

                // Start with singletons from first clause
                std::vector<Set> final_eval;
                for (int e : value[0])
                    final_eval.push_back({e});

                // Multiply with remaining clauses
                for (size_t i = 1; i < value.size(); ++i)
                    final_eval = multiplyTwoPathsets(final_eval, value[i]);

                if (most_common_value >= 0)
                    final_eval.push_back({most_common_value});

                evaluation = std::move(final_eval);
            }

            void evaluateTwoLeaf(const std::vector<Set>* left_eval,
                                 const std::vector<Set>* right_eval)
            {
                AbsorbList final_eval;

                if (most_common_value >= 0)
                    final_eval.add({most_common_value});

                if (!left_eval || left_eval->empty())
                {
                    if (right_eval)
                        final_eval.addMany(*right_eval);
                    evaluation = final_eval.toSetList();
                    return;
                }

                if (!right_eval || right_eval->empty())
                {
                    final_eval.addMany(*left_eval);
                    evaluation = final_eval.toSetList();
                    return;
                }

                // Multiply left × right
                for (const auto& l : *left_eval)
                {
                    for (const auto& r : *right_eval)
                    {
                        Set new_set = l;
                        new_set.insert(new_set.end(), r.begin(), r.end());
                        std::sort(new_set.begin(), new_set.end());
                        // Remove duplicates
                        new_set.erase(std::unique(new_set.begin(), new_set.end()), new_set.end());
                        final_eval.add(new_set);
                    }
                }

                evaluation = final_eval.toSetList();
            }
        };

    } // anonymous namespace

    MinCutSets minimalcuts_cnf_tree(const AdjList& adj, NodeID src, NodeID dst, int num_nodes)
    {
        // Get minimal paths
        PathSets mps = minimalpaths(adj, src, dst);

        // Direct connection
        if (mps.size() == 1 && mps[0].size() == 2 &&
            mps[0][0] == src && mps[0][1] == dst)
        {
            return {{src}, {dst}};
        }

        // Sort by length
        std::sort(mps.begin(), mps.end(),
                  [](const Set& a, const Set& b) { return a.size() < b.size(); });

        // Remove src and dst from each path, convert to sets
        std::vector<Set> pathsets;
        for (auto& mp : mps)
        {
            Set ps;
            for (int node : mp)
            {
                if (node != src && node != dst)
                    ps.push_back(node);
            }
            std::sort(ps.begin(), ps.end());
            pathsets.push_back(std::move(ps));
        }

        // Build decision tree and evaluate
        DecisionTreeNode tree(pathsets, num_nodes);
        tree.evaluate();

        // Sort results
        std::vector<Set> temp_result;
        for (auto& s : tree.evaluation)
        {
            std::sort(s.begin(), s.end());
            temp_result.push_back(std::move(s));
        }
        std::sort(temp_result.begin(), temp_result.end(),
                  [](const Set& a, const Set& b) {
                      if (a.size() != b.size()) return a.size() < b.size();
                      return a < b;
                  });

        MinCutSets result = {{src}, {dst}};
        result.insert(result.end(), temp_result.begin(), temp_result.end());
        return result;
    }

} // namespace pyrbd_core::sets
