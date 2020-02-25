#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103, C0330, R0914, W1639

from __future__ import absolute_import, division
from math import floor, log2
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


def mul_tau_min(
    low_t: int, upp_t: int, m: int
) -> List[Tuple[int, int, int, int]]:
    params = []

    for t in range(upp_t, low_t - 1, -1):
        n = 0
        s = floor(t * n / 2)

        while log2(tau_length(t, n, s)) < m:
            n += 1
            s = floor(t * n / 2)

        while log2(tau_length(t, n, s)) >= m:
            n -= 1
        n += 1

        while log2(tau_length(t, n, s)) >= m:
            s -= 1
        s += 1
        params.append((t, n, s, m))

    return params


def mul_tau_eq(
    low_t: int, upp_t: int, m: int
) -> List[Tuple[int, int, int, int]]:
    params = []

    for t in range(upp_t, low_t - 1, -1):
        s = 0
        while log2(tau_length(t, s, s)) < m:
            s += 1

        while log2(tau_length(t, s, s)) >= m:
            s -= 1
        s += 1
        params.append((t, s, s, m))

    return params


if __name__ == "__main__":
    assert len(argv) == 3

    PARAMS = {
        "min": {"256": [30, 80, 256], "512": [60, 140, 512]},
        "equal": {"256": [10, 80, 256], "512": [20, 140, 512]},
        "prob": {"256": [34, 34, 256], "512": [131, 131, 512]},
    }

    if argv[1] == "min":
        param = mul_tau_min(*PARAMS[argv[1]][argv[2]])
    elif argv[1] == "equal":
        param = mul_tau_eq(*PARAMS[argv[1]][argv[2]])
    elif argv[1] == "prob":
        param = mul_tau_min(*PARAMS[argv[1]][argv[2]])
        T, N, S, M = param[0]
        param = [(T, i, S, M) for i in range(N, S, 50)] + [(T, S, S, M)]

    for p in param:
        print(*p)
