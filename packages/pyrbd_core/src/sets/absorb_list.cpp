#include <pyrbd_core/sets.hpp>
#include <algorithm>
#include <unordered_set>

namespace pyrbd_core::sets
{
    // ================================================================
    // AbsorbList — C++ port of Python AbsorbList
    //
    // Maintains a family of sets where no set is a subset or superset
    // of another. Sets are stored sorted for efficient comparison.
    // ================================================================

    // Check if sorted set a ⊆ sorted set b
    bool AbsorbList::isSubsetSorted(const Set& a, const Set& b)
    {
        return std::includes(b.begin(), b.end(), a.begin(), a.end());
    }

    bool AbsorbList::add(const Set& s)
    {
        // Store sets sorted internally
        Set sorted_s = s;
        std::sort(sorted_s.begin(), sorted_s.end());
        size_t m = sorted_s.size();

        // Case 0: exact duplicate
        auto it = buckets_.find(m);
        if (it != buckets_.end())
        {
            for (const auto& existing : it->second)
            {
                if (existing == sorted_s)
                    return false;
            }
        }

        // Case 1: if any existing set (smaller or equal) is a subset of new → discard new
        for (const auto& [k, bucket] : buckets_)
        {
            if (k > m) continue;
            for (const auto& existing : bucket)
            {
                if (isSubsetSorted(existing, sorted_s))
                    return false; // existing ⊆ new → discard new
            }
        }

        // Case 2: remove all existing supersets of the new one
        std::vector<Set> to_remove;
        for (const auto& [k, bucket] : buckets_)
        {
            if (k < m) continue;
            for (const auto& existing : bucket)
            {
                if (isSubsetSorted(sorted_s, existing))
                    to_remove.push_back(existing);
            }
        }

        for (const auto& rem : to_remove)
            discardInternal(rem);

        addInternal(sorted_s);
        return true;
    }

    int AbsorbList::addMany(const std::vector<Set>& sets)
    {
        // Sort by size first (insert smaller sets first to prune more)
        std::vector<Set> sorted_sets = sets;
        std::sort(sorted_sets.begin(), sorted_sets.end(),
                  [](const Set& a, const Set& b) { return a.size() < b.size(); });

        int changed = 0;
        for (const auto& s : sorted_sets)
        {
            if (add(s)) ++changed;
        }
        return changed;
    }

    std::vector<Set> AbsorbList::toSetList() const
    {
        std::vector<Set> result;
        result.reserve(count_);
        for (const auto& [_, bucket] : buckets_)
        {
            for (const auto& s : bucket)
                result.push_back(s);
        }
        return result;
    }

    void AbsorbList::clear()
    {
        buckets_.clear();
        count_ = 0;
    }

    void AbsorbList::addInternal(const Set& s)
    {
        buckets_[s.size()].push_back(s);
        ++count_;
    }

    void AbsorbList::discardInternal(const Set& s)
    {
        auto it = buckets_.find(s.size());
        if (it == buckets_.end()) return;

        auto& bucket = it->second;
        auto pos = std::find(bucket.begin(), bucket.end(), s);
        if (pos != bucket.end())
        {
            bucket.erase(pos);
            --count_;
            if (bucket.empty())
                buckets_.erase(it);
        }
    }

} // namespace pyrbd_core::sets
