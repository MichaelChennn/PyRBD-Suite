from typing import Set, List
from ._absorb_list import AbsorbList
import numpy as np

# e.g. Clause (2 + 4 + 6) represent as {2,4,6}
Clause = Set[int]

# e.g. CNF ((2 + 4 + 6) * (1 + 3)) represent as [{2,4,6}, {1,3}]
CNF = List[Clause]


def multiply(partial_set_list, factor_set):
    """
    Multiply each set in the partial_set_list with the factor_set.
    For each partial set in the list, merge it with each element in the factor_set if they are disjoint.
    Else keep the original set.
    Add all the new sets in a list
    """
    absorbed_list = AbsorbList()

    for partial_set in partial_set_list:
        if partial_set.isdisjoint(factor_set):
            for f in factor_set:
                new_set = partial_set.union({f})
                absorbed_list.add(new_set)
        else:
            absorbed_list.add(partial_set)

    return absorbed_list.to_set_list()


class DecisionTreeNode:
    def __init__(self, value: CNF, nodes_num, most_common_value=None):
        self.value = value
        self.max_val = nodes_num
        self.most_common_value = most_common_value
        self.evaluation = None
        self.left = None
        self.right = None

        # find the most common element
        common_elem, counts = self._most_common_element(value)

        # split the set list into two parts if counts > 1
        if counts > 1:
            with_elem, without_elem = self._split_cnf(value, common_elem)

            # save the without element part to the left child
            self.left = (
                DecisionTreeNode(without_elem, self.max_val)
                if len(without_elem) > 0
                else None
            )

            # save the with element part to the right child
            self.right = (
                DecisionTreeNode(with_elem, self.max_val, most_common_value=common_elem)
                if len(with_elem) > 0
                else None
            )

    def _most_common_element(self, cnf: CNF):
        """Counts the most common element
         Args:
             cnf (CNF): list of sets
        Returns:
             most_common_element (int), count (int)
        """
        counts = np.zeros(self.max_val + 1, dtype=np.int32)
        for subset in cnf:
            counts[list(subset)] += 1
        idx = np.argmax(counts)

        return int(idx), int(counts[int(idx)])

    def _split_cnf(self, cnf: CNF, element: int):
        """Remove the element from the CNF and split into two parts.
        Args:
            cnf (CNF): list of sets
            element (int): element to split on
        Returns:
            with_elem (CNF): sets containing the element before removal
            without_elem (CNF): sets not containing the element
        """
        with_elem = []
        without_elem = []
        for subset in cnf:
            if element in subset:
                # remove the element from the subset
                new_subset = subset - {element}
                with_elem.append(new_subset)
            else:
                without_elem.append(subset)
        return with_elem, without_elem

    def _evaluate(self):
        """Evaluate this node using a bottom-up traversal.

        Behavior (framework):
        1. If this node is a leaf (no children), compute its evaluation by
           calling `_evaluate_self()` and store the resulting Clause in
           `self.evaluation`.
        2. Otherwise, descend to any child whose `evaluation` is None until
           reaching the deepest unevaluated nodes (depth-first). After child
           evaluations are available, combine them with `_evaluate_two_leaf()`
           and store the result in `self.evaluation`.
        """

        # If leaf node: compute its own evaluation
        if self.left is None and self.right is None:
            if self.evaluation is None:
                self.evaluation = self._evaluate_self()
            return

        # Depth-first descent: try to find/defer to deepest unevaluated child(s)
        # Prioritize left then right (deterministic)
        if self.left is not None and self.left.evaluation is None:
            self.left._evaluate()

        if self.right is not None and self.right.evaluation is None:
            self.right._evaluate()

        # At this point, children (that exist) have been asked to evaluate
        left_eval = self.left.evaluation if self.left is not None else None
        right_eval = self.right.evaluation if self.right is not None else None

        # If both child evaluations are missing, fallback to evaluate_self
        if left_eval is None and right_eval is None:
            if self.evaluation is None:
                self.evaluation = self._evaluate_self()
        else:
            # combine available child clauses into a parent clause
            if self.evaluation is None:
                self.evaluation = self._evaluate_two_leaf(left_eval, right_eval)

    # ----- Evaluation stubs (to be filled in by user) -----
    def _evaluate_self(self):
        """Compute this node's evaluation when it's a leaf (or when used as
        a fallback).
        """
        # Save the final evaluation, starting with the first clause
        final_eval = [{e} for e in self.value[0]]

        # Multiply with the rest of the clauses
        for s in self.value[1:]:
            final_eval = multiply(final_eval, s)

        if self.most_common_value is not None:
            final_eval.append({int(self.most_common_value)})

        return final_eval

    def _evaluate_two_leaf(self, left_eval: CNF, right_eval: CNF):
        """Combine two child Clauses into this node's Clause."""
        # Create a absorb list to store the final evaluation
        final_eval = AbsorbList()

        # Add the most common value as a singleton set
        if self.most_common_value is not None:
            final_eval.add({self.most_common_value})

        if left_eval is None:
            final_eval.add_many(right_eval)
            return final_eval.to_set_list()

        if right_eval is None:
            final_eval.add_many(left_eval)
            return final_eval.to_set_list()

        # Multiply left evaluation with right evaluation
        for l in left_eval:
            for r in right_eval:
                new_set = l.union(r)
                final_eval.add(new_set)

        result = final_eval.to_set_list()

        return result

    def __str__(self) -> str:
        """Readable representation: most_common value (int) + value (list of sets) + evaluation."""

        def fmt_clause_list(cl):
            if cl is None:
                return "None"
            try:
                clauses = []
                for s in cl:
                    elems = ",".join(str(x) for x in sorted(s))
                    clauses.append("{" + elems + "}")
                return "[" + ", ".join(clauses) + "]"
            except Exception:
                return repr(cl)

        try:
            clauses = []
            for s in self.value:
                # sort elements for deterministic output
                elems = ",".join(str(x) for x in sorted(s))
                clauses.append("{" + elems + "}")
            val_repr = "[" + ", ".join(clauses) + "]"
        except Exception:
            # fallback if self.value is not iterable as expected
            val_repr = repr(self.value)

        eval_repr = fmt_clause_list(self.evaluation)
        return f"TreeNode(most_common={self.most_common_value}, value={val_repr}, evaluation={eval_repr})"

    def __repr__(self) -> str:
        return self.__str__()


class CNFDecisionTree:
    def __init__(self, root_value: CNF, max_val: int):
        self.root = DecisionTreeNode(root_value, max_val)
        self.max_val = max_val

    def evaluate_all(self):
        """Compute evaluations for whole tree (bottom-up). Safe to call before printing."""

        if self.root.evaluation is None:
            self.root._evaluate()
            return self.root.evaluation
        else:
            return self.root.evaluation

    def __getattribute__(self, name: str):
        if name == "evaluation":
            return self.root.evaluation
        return super().__getattribute__(name)

    def iter_levels(self, with_parent: bool = False):
        """Breadth-first traversal.

        Yields either (node, level) or (node, level, parent) depending on
        the `with_parent` flag. Skips None nodes.
        """
        from collections import deque

        if self.root is None:
            return

        q = deque()
        q.append((self.root, 0, None))

        while q:
            node, level, parent = q.popleft()
            if node is None:
                continue
            if with_parent:
                yield node, level, parent
            else:
                yield node, level

            left = getattr(node, "left", None)
            right = getattr(node, "right", None)
            if left is not None:
                q.append((left, level + 1, node))
            if right is not None:
                q.append((right, level + 1, node))

    def to_string(self, max_levels: int = None) -> str:
        """Return a multi-line string representation of the tree, level by level.

        This mirrors what `pretty_print` prints but returns a string so it can be
        used by `__str__`/logging without side-effects.
        """
        # First pass: collect nodes with parent references and assign stable ids
        nodes = []  # tuples of (nid, node, lvl, parent_node)
        id_map = {}
        next_id = 0
        for node, lvl, parent in self.iter_levels(with_parent=True):
            if max_levels is not None and lvl >= max_levels:
                break

            # Skip nodes that are effectively empty:
            node_value = getattr(node, "value", None)
            has_left = getattr(node, "left", None) is not None
            has_right = getattr(node, "right", None) is not None
            is_empty_value = node_value is None or (
                hasattr(node_value, "__len__") and len(node_value) == 0
            )
            if not has_left and not has_right and is_empty_value:
                continue

            nid = next_id
            id_map[node] = nid
            nodes.append((nid, node, lvl, parent))
            next_id += 1

        # Group by level
        levels = {}
        for nid, node, lvl, parent in nodes:
            levels.setdefault(lvl, []).append((nid, node, parent))

        lines = []
        for lvl in sorted(levels.keys()):
            lines.append(f"Level {lvl}:")
            for nid, node, parent in levels[lvl]:
                parent_id = id_map.get(parent, None)
                node_lines = str(node).splitlines() or ["<node>"]
                first = node_lines[0]
                rest = node_lines[1:]
                # keep similar indentation as before but add [id] and parent info
                header = f"  [{nid}] {first} (parent={parent_id})"
                lines.append(header)
                for r in rest:
                    lines.append("      " + r)
            lines.append("")

        return "\n".join(lines)

    def __str__(self):
        # Return the full multi-line tree string by default so print(tree) shows whole tree
        try:
            return self.to_string()
        except Exception:
            # Fallback to a short summary
            try:
                root_repr = str(self.root)
            except Exception:
                root_repr = "<unrepresentable root>"
            return f"BinaryTree(max_val={self.max_val}, root={root_repr})"

    def __repr__(self) -> str:
        return self.__str__()
