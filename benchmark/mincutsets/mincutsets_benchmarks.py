import time
from pyrbd_plusplus.algorithms.sets import minimalcuts as pyrbdpp_minimalcuts
from pyrbd3.algorithms.sets import minimalcuts as pyrbd3_minimalcuts


class MincutsetsBenchmarks:
    """
    Benchmark methods for PyRBD++ and PyRBD3 Mincutsets algorithms.
    These methods measure the execution time of the Python implementations.
    """

    # ==============================
    # PyRBD++ Algorithms
    # ==============================

    @staticmethod
    def pyrbdpp_combination(G, src, dst, order=None):
        """
        Benchmark pyrbd_plusplus minimalcuts with method='combination'
        """
        start_time = time.perf_counter()
        result = pyrbdpp_minimalcuts(G, src, dst, order=order, method="combination")
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def pyrbdpp_combination_matrix(G, src, dst, order=None):
        """
        Benchmark pyrbd_plusplus minimalcuts with method='combination_matrix'
        """
        start_time = time.perf_counter()
        result = pyrbdpp_minimalcuts(
            G, src, dst, order=order, method="combination_matrix"
        )
        end_time = time.perf_counter()
        return result, end_time - start_time

    # ==============================
    # PyRBD3 Algorithms
    # ==============================

    @staticmethod
    def pyrbd3_shannon(G, src, dst):
        """
        Benchmark pyrbd3 minimalcuts with method='shannon'
        """
        start_time = time.perf_counter()
        result = pyrbd3_minimalcuts(G, src, dst, method="shannon")
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def pyrbd3_cnf_tree(G, src, dst):
        """
        Benchmark pyrbd3 minimalcuts with method='cnf_tree'
        """
        start_time = time.perf_counter()
        result = pyrbd3_minimalcuts(G, src, dst, method="cnf_tree")
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def pyrbd3_multiplication(G, src, dst):
        """
        Benchmark pyrbd3 minimalcuts with method='multiplication'
        """
        start_time = time.perf_counter()
        result = pyrbd3_minimalcuts(G, src, dst, method="multiplication")
        end_time = time.perf_counter()
        return result, end_time - start_time
