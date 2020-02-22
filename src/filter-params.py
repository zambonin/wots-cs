#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103, C0330, R0914

from __future__ import absolute_import, division
from collections import defaultdict
from math import ceil, floor, log2


def wt(m: int, w: int) -> int:
    t1 = ceil(m / log2(w))
    return t1 + floor(log2(t1 * (w - 1)) / log2(w)) + 1


def table_1() -> str:
    table_header = (
        "\\begin{table}[htbp]\n"
        "  \\setlength{\\tabcolsep}{7pt}\n"
        "  \\centering\n"
        "  \\caption{Number of iterations of $f$ for usual\n"
        "    parameters of \\wots{}. Values underlined are\n"
        "    averages over multiple signatures.}\\label{tab:wots}\n"
        "  \\begin{tabular}{*{6}{r}}\n"
        "    \\toprule\n"
        "    $m$ & $w$ & $t$ & $G_{c}$ & $S_{c}$ & $V_{c}$ \\\\ \\midrule\n"
    )
    table_footer = "    \\bottomrule\n" "  \\end{tabular}\n" "\\end{table}"
    line_fmt = (
        "{:>24} & {:>6.0f} & {:>6.0f} & {:>6.0f} " "& {:>20} & {:>20} \\\\\n"
    )

    results = defaultdict(list)
    for m in [256, 512]:  # e.g. sha-256, sha-512
        for w in [1 << 4, 1 << 6, 1 << 8]:  # winternitz parameter
            t = wt(m, w)
            gc = t * (w - 1)
            sc = vc = "$\\underline{{{}}}$".format(gc // 2)
            results[m].append((w, t, gc, sc, vc))

    table = table_header
    for t, v in results.items():
        table += line_fmt.format("\\multirow{{3}}{{*}}{{{}}}".format(t), *v[0])
        table += line_fmt.format("", *v[1])
        table += line_fmt.format("", *v[2]) + "    \\midrule\n"
    table += table_footer

    return table


def subtable_4(path: str, m: int) -> str:
    with open(path) as f:
        data = f.readlines()

    lines = [list(map(float, x)) for x in map(str.split, data)]
    group_t = defaultdict(list)
    for t, n, s, _ in lines:
        group_t[t].append((n, t * n, t * n - s, s))

    wint = defaultdict(list)
    for w in [1 << 4, 1 << 6, 1 << 8]:  # winternitz parameter
        t = wt(m, w)
        gc = t * (w - 1)
        sc = vc = gc // 2
        wint[t].append((w, gc, sc, vc))

    line_fmt = (
        "{:>24} & {:>4} & {:>4.0f} & {:>6.0f} "
        "& {:>6.0f} & {:>10} & {:>10} \\\\\n"
    )

    subtable = ""
    for index, params in enumerate(wint.items()):
        _, gc1, _, vc1 = params[1][0]
        n2, gc2, _, vc2 = min(group_t[params[0]], key=lambda x: x[1])
        delta_gc = "${:>+6.2f}\\%$".format(100 * (-1 + gc2 / gc1))
        delta_vc = "${:>+6.2f}\\%$".format(100 * (-1 + vc2 / vc1))

        first = "\\multirow{{3}}{{*}}{{{}}}".format(m) if not index else ""
        subtable += line_fmt.format(
            first, params[0], n2, gc2, vc2, delta_gc, delta_vc
        )
    subtable += "    \\midrule\n"

    return subtable


def table_4():
    table_header = (
        "\\begin{table}[htbp]\n"
        "  \\setlength{\\tabcolsep}{6.9pt}\n"
        "  \\renewcommand{\\arraystretch}{1.2}\n"
        "  \\centering\n"
        "  \\caption{Suggested parameters for\n"
        "    \\textsc{Wots-cs}, with $G_{c}$ and\n"
        "    $V_{c}$ as compared to \\textsc{Wots}.}"
        "\\label{tab:params}\n"
        "  \\begin{tabular}{rc*{5}rr}\n"
        "    \\toprule\n"
        "    $m$ & $t$ & $n$ & $G_{c}$ & $V_{c}$ &\n"
        "      $\\Delta G_{c}$ & $\\Delta V_{c}$ \\\\ \\midrule \n"
    )
    table_footer = "    \\bottomrule\n  \\end{tabular}\n\\end{table}"

    table = table_header
    table += subtable_4("params-min-256.txt", 256)
    table += subtable_4("params-min-512.txt", 512)
    table += table_footer

    return table


if __name__ == "__main__":
    print(table_1())
    print(table_4())
