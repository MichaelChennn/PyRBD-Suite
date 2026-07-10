#include <pyrbd_core/common.hpp>
#include <algorithm>

namespace pyrbd_core
{
    DisjointSets makeDisjointSet(const Set& set1, Set set2)
    {
        // RC set: elements in set1 but not in set2
        Set RC;

        // Check if set1 and set2 are disjoint: if x in set1 and -x in set2
        for (const int& elem : set1)
        {
            if (std::find(set2.begin(), set2.end(), -elem) != set2.end())
            {
                return {set2};
            }
            if (std::find(set2.begin(), set2.end(), elem) == set2.end())
            {
                RC.push_back(elem);
            }
        }

        if (RC.empty())
        {
            return DisjointSets{};
        }

        DisjointSets result;

        for (size_t i = 0; i < RC.size(); i++)
        {
            set2.push_back(-RC[i]);
            result.push_back(set2);
            set2.back() = -set2.back();
        }

        return result;
    }
} // namespace pyrbd_core
