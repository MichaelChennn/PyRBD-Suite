import time
from pyrbd_plusplus.algorithms.sets.pathsets import minimalpaths as pyrbdpp_minimalpaths


class PathsetsBenchmarks:
    """
    Benchmark methods for Pathsets algorithms.
    These methods measure the execution time of the Python implementations.
    """

    # ==============================
    # PyRBD++ Algorithms
    # ==============================

    @staticmethod
    def pyrbdpp_minimalpaths(G, src, dst):
        """
        Benchmark pyrbd_plusplus minimalpaths
        """
        start_time = time.perf_counter()
        result = pyrbdpp_minimalpaths(G, src, dst)
        end_time = time.perf_counter()
        return result, end_time - start_time
