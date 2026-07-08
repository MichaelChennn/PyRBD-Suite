from collections import defaultdict
from typing import Iterable, Iterator, Hashable, Set, Dict

class AbsorbList:
    """
    Maintain a family of sets with the following invariant:
      - No set is a subset or superset of another.
      - When inserting a new set:
        * If an existing set is a subset of the new one → ignore the new set.
        * If an existing set is a superset of the new one → remove the supersets and insert the new set.
        * Otherwise, simply add the new set.
    """

    def __init__(self, sets: Iterable[Iterable[Hashable]] | None = None) -> None:
        # Store sets grouped by their size (bucketed by cardinality)
        self.buckets: Dict[int, Set[frozenset]] = defaultdict(set)
        self._count = 0
        if sets:
            self.add_many(sets)

    def __len__(self) -> int:
        return self._count

    def __iter__(self) -> Iterator[set]:
        # Iterate as normal Python sets
        for bucket in self.buckets.values():
            for fs in bucket:
                yield set(fs)

    def __contains__(self, s: Iterable[Hashable]) -> bool:
        fs = frozenset(s)
        return fs in self.buckets[len(fs)]

    def _add_fs(self, fs: frozenset) -> None:
        self.buckets[len(fs)].add(fs)
        self._count += 1

    def _discard_fs(self, fs: frozenset) -> None:
        bucket = self.buckets[len(fs)]
        if fs in bucket:
            bucket.remove(fs)
            self._count -= 1
            if not bucket:
                del self.buckets[len(fs)]

    def add(self, s: Iterable[Hashable]) -> bool:
        """
        Insert a new set `s`.

        Returns:
            True if the family changed (s was added, possibly replacing supersets).
            False if the new set was discarded or already existed.
        """
        fs = frozenset(s)
        m = len(fs)

        # Case 0: exact duplicate
        if fs in self.buckets[m]:
            return False

        # Case 1: if any existing set is a subset of the new one → discard new
        for k in list(self.buckets.keys()):
            if k > m:
                continue
            for exist in self.buckets[k]:
                if exist <= fs:
                    return False

        # Case 2: remove all existing supersets of the new one
        to_remove: list[frozenset] = []
        for k in list(self.buckets.keys()):
            if k < m:
                continue
            for exist in self.buckets[k]:
                if exist >= fs:
                    to_remove.append(exist)

        if to_remove:
            for exist in to_remove:
                self._discard_fs(exist)
            self._add_fs(fs)
            return True
        else:
            # Case 3: independent, just add it
            self._add_fs(fs)
            return True

    def add_many(self, it: Iterable[Iterable[Hashable]]) -> int:
        """
        Batch insert multiple sets.

        Returns:
            Number of times the structure actually changed.
        """
        changed = 0
        # Insert smaller sets first (helps prune supersets early)
        for s in sorted((frozenset(x) for x in it), key=len):
            changed += 1 if self.add(s) else 0
        return changed

    def to_frozensets(self) -> Set[frozenset]:
        """Return all sets as frozensets."""
        out: Set[frozenset] = set()
        for bucket in self.buckets.values():
            out |= set(bucket)
        return out
    
    def to_set_list(self) -> list[set]:
        """Return all sets as list of sets."""
        out: list[set] = []
        for bucket in self.buckets.values():
            for fs in bucket:
                out.append(set(fs))
        return out

    def clear(self) -> None:
        """Remove all stored sets."""
        self.buckets.clear()
        self._count = 0

    def __repr__(self) -> str:
        items = sorted((sorted(fs) for fs in self.to_frozensets()), key=lambda x: (len(x), x))
        return f"AbsorbList({items})"
    

