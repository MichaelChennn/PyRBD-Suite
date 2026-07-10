#include <pyrbd_core/sets.hpp>
#include <stack>
#include <unordered_set>

namespace pyrbd_core::sets
{
    // ================================================================
    // DFS-based minimal paths (ported from Python pathsets.py)
    //
    // Implements the "dontgo" pruning strategy:
    //   For each node in visited (except the last), all its neighbours
    //   are forbidden for the current extension. This prunes paths
    //   that revisit neighbours of already-traversed intermediate nodes.
    // ================================================================

    namespace {
        // Collect neighbours of all visited nodes except the last one
        std::unordered_set<NodeID> getDontgo(const AdjList& adj,
                                              const std::vector<NodeID>& visited)
        {
            std::unordered_set<NodeID> dontgo;
            if (visited.size() > 1)
            {
                // For all nodes in visited except the last, add their neighbours
                for (size_t i = 0; i < visited.size() - 1; ++i)
                {
                    NodeID node = visited[i];
                    if (node >= 0 && static_cast<size_t>(node) < adj.size())
                    {
                        for (NodeID neigh : adj[node])
                            dontgo.insert(neigh);
                    }
                }
            }
            return dontgo;
        }
    } // anonymous namespace

    PathSets minimalpaths(const AdjList& adj, NodeID src, NodeID dst)
    {
        PathSets result;

        // Stack-based iterative DFS
        std::vector<NodeID> visited = {src};
        std::unordered_set<NodeID> visitedSet = {src};

        // Stack of iterators (index into adjacency list)
        std::stack<size_t> iterStack;
        iterStack.push(0); // start at first neighbour of src

        while (!iterStack.empty())
        {
            NodeID current = visited.back();

            if (static_cast<size_t>(current) >= adj.size() || iterStack.top() >= adj[current].size())
            {
                // Backtrack
                iterStack.pop();
                visitedSet.erase(visited.back());
                visited.pop_back();
                if (!iterStack.empty())
                    ++iterStack.top(); // advance parent's iterator
                continue;
            }

            NodeID child = adj[current][iterStack.top()];
            auto dontgo = getDontgo(adj, visited);

            if (dontgo.count(child))
            {
                ++iterStack.top();
                continue;
            }

            if (child == dst)
            {
                // Found a path
                Set path = visited;
                path.push_back(dst);
                result.push_back(std::move(path));
                ++iterStack.top();
            }
            else if (visitedSet.count(child) == 0)
            {
                // Extend path
                visited.push_back(child);
                visitedSet.insert(child);
                iterStack.push(0);
            }
            else
            {
                ++iterStack.top();
            }
        }

        return result;
    }

} // namespace pyrbd_core::sets
