#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103, C0330, R0914, W1639

from __future__ import absolute_import, division
from math import ceil, floor, log2
from multiprocessing import Pool
from itertools import chain, product
from sys import argv
from typing import List, Tuple

from scipy.special import comb


def binomial(n: int, k: int) -> int:
    return comb(n, k, exact=True)


def tau_length(t: int, n: int, s: int) -> int:
    k = min(t, floor(s / (n + 1)))
    tau = 0

    for i in range(k + 1):
        tau += (
            (-1) ** i
            * binomial(t, i)
            * binomial(s - (n + 1) * i + t - 1, t - 1)
        )

    return tau


def mul_tau(
    t: int, n: int, s_min: int, s_max: int, m: int
) -> List[Tuple[int, int, int, int]]:
    results = []

    for s in range(s_min, min(ceil(t * n / 2), s_max) + 1):
        tau_len = tau_length(t, n, s)
        if (m + 1) > log2(tau_len) > m:
            results.append((t, n, s, t * n))

    return results


def mul_tau_wrapper(args: List[str]):
    mode, t_min, t_max, n_min, n_max, s_min, s_max, m = args
    params = product(
        range(t_min, t_max + 1), range(n_min, n_max + 1), [s_min], [s_max], [m]
    )

    if mode == "equal":
        params = [(t, n, n, n, m) for t, n, smin, smax, m in params]

    params = filter(lambda x: x[1] <= x[2], params)
    if mode in ("equal", "all"):
        with Pool() as pool:
            results = pool.starmap(mul_tau, params)
            for t, n, s, tn in chain.from_iterable(results):
                print("{:3d} {:4d} {:6d} {:6d}".format(t, n, s, tn))


if __name__ == "__main__":
    assert len(argv) == 3

    PARAMS = {
        "min": {
            "256": ["all", 30, 80, 16, 512, 256, 4096, 256],
            "512": ["all", 60, 140, 16, 512, 512, 8192, 512],
        },
        "equal": {
            "256": ["equal", 8, 80, 8, 16384, 0, 0, 256],
            "512": ["equal", 20, 140, 8, 16384, 0, 0, 512],
        },
    }

    mul_tau_wrapper(PARAMS[argv[1]][argv[2]])
