import time
import pyrbd_plusplus._core.pyrbd_plusplus_cpp as pyrbdpp_core
import pyrbd3._core.pyrbd3_cpp as pyrbd3_core


class AvailabilityBenchmarks:
    """
    Benchmark methods for PyRBD++ and PyRBD3 C++ bindings.
    These methods only measure the execution time of the C++ function calls.
    Data preparation (reading, relabeling, finding sets) should be done beforehand.
    """

    # ==============================
    # MCS Algorithm Benchmarks (PyRBD++)
    # ==============================

    @staticmethod
    def pyrbdpp_mcs_single_flow(src, dst, probabilities, min_cut_sets):
        """
        Benchmark mcs.eval_avail
        """
        start_time = time.perf_counter()
        result = pyrbdpp_core.mcs.eval_avail(src, dst, probabilities, min_cut_sets)
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def pyrbdpp_mcs_whole_topo(node_pairs, probabilities, min_cut_sets_list):
        """
        Benchmark mcs.eval_avail_topo (Serial)
        """
        start_time = time.perf_counter()
        result = pyrbdpp_core.mcs.eval_avail_topo(
            node_pairs, probabilities, min_cut_sets_list
        )
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def pyrbdpp_mcs_whole_topo_parallel(node_pairs, probabilities, min_cut_sets_list):
        """
        Benchmark mcs.eval_avail_topo_parallel (Parallel)
        """
        start_time = time.perf_counter()
        result = pyrbdpp_core.mcs.eval_avail_topo_parallel(
            node_pairs, probabilities, min_cut_sets_list
        )
        end_time = time.perf_counter()
        return result, end_time - start_time

    # ==============================
    # PathSet Algorithm Benchmarks (PyRBD++)
    # ==============================
    @staticmethod
    def pyrbdpp_pathset_single_flow(src, dst, probabilities, path_sets):
        """
        Benchmark pathset.eval_avail
        """
        start_time = time.perf_counter()
        result = pyrbdpp_core.pathset.eval_avail(src, dst, probabilities, path_sets)
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def pyrbdpp_pathset_whole_topo(node_pairs, probabilities, pathsets_list):
        """
        Benchmark pathset.eval_avail_topo (Serial)
        """
        start_time = time.perf_counter()
        result = pyrbdpp_core.pathset.eval_avail_topo(
            node_pairs, probabilities, pathsets_list
        )
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def pyrbdpp_pathset_whole_topo_parallel(node_pairs, probabilities, pathsets_list):
        """
        Benchmark pathset.eval_avail_topo_parallel (Parallel)
        """
        start_time = time.perf_counter()
        result = pyrbdpp_core.pathset.eval_avail_topo_parallel(
            node_pairs, probabilities, pathsets_list
        )
        end_time = time.perf_counter()
        return result, end_time - start_time

    # ==============================
    # SDP Algorithm Benchmarks (PyRBD3)
    # ==============================
    @staticmethod
    def pyrbd3_sdp_single_flow(src, dst, probabilities, path_sets):
        """
        Benchmark sdp.eval_avail (Serial)
        """
        start_time = time.perf_counter()
        result = pyrbd3_core.sdp.eval_avail(src, dst, probabilities, path_sets)
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def pyrbd3_sdp_single_flow_parallel(src, dst, probabilities, path_sets):
        """
        Benchmark sdp.eval_avail_parallel (Parallel)
        """
        start_time = time.perf_counter()
        result = pyrbd3_core.sdp.eval_avail_parallel(src, dst, probabilities, path_sets)
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def pyrbd3_sdp_whole_topo(node_pairs, probabilities, pathsets_list):
        """
        Benchmark sdp.eval_avail_topo (Serial)
        """
        start_time = time.perf_counter()
        result = pyrbd3_core.sdp.eval_avail_topo(
            node_pairs, probabilities, pathsets_list
        )
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def pyrbd3_sdp_whole_topo_parallel(node_pairs, probabilities, pathsets_list):
        """
        Benchmark sdp.eval_avail_topo_parallel (Parallel)
        """
        start_time = time.perf_counter()
        result = pyrbd3_core.sdp.eval_avail_topo_parallel(
            node_pairs, probabilities, pathsets_list
        )
        end_time = time.perf_counter()
        return result, end_time - start_time
