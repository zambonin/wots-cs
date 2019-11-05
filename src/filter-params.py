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
        "    parameters of \\wots{}. Underlines are averaged\n"
        "    over multiple signatures.}\\label{tab:wots}\n"
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


def subtable_2(path: str, m: int) -> str:
    with open(path) as f:
        data = f.readlines()

    lines = [list(map(float, x)) for x in map(str.split, data)]
    group_t = defaultdict(list)
    for t, n, s, tn in lines:
        group_t[t].append((n, tn, tn - s, s))

    wint = defaultdict(list)
    for w in [1 << 4, 1 << 6, 1 << 8]:  # winternitz parameter
        t = wt(m, w)
        gc = t * (w - 1)
        sc = vc = "$\\underline{{{}}}$".format(gc // 2)
        wint[t].append((w, gc, sc, vc))

    subtable_header = (
        "  \\subfloat[$m = {}$]{{\\begin{{tabular}}{{rc*{{5}}{{r}}}}\n"
        "    \\toprule\n"
        "    $t$ & Variant & $n$ & $G_{{c}}$ & $S_{{c}}$ & $V_{{c}}$ "
        "& $\\Delta V_{{c}}$ \\\\ \\midrule\n".format(m)
    )
    subtable_footer = "    \\bottomrule\n" "  \\end{tabular}}\n"
    line_fmt = (
        "{:>24} & {:>14} & {:>5.0f} & {:>5.0f} "
        "& {:>20} & {:>20} & {:>10} \\\\\n"
    )

    subtable = subtable_header
    for k, v in wint.items():
        t1, var1, n1, gc1, sc1, vc1 = (
            "\\multirow{{3}}{{*}}{{{:>3}}}".format(k),
            "Classical",
            *v[0],
        )
        t2, var2, n2, gc2, sc2, vc2 = (
            "",
            "$\\min(V_{c})$",
            *min(group_t[k], key=lambda x: x[3]),
        )
        t3, var3, n3, gc3, sc3, vc3 = (
            "",
            "$\\min(G_{c})$",
            *min(group_t[k], key=lambda x: x[1]),
        )
        delta2 = "${:>+6.2f}\\%$".format(100 * (-1 + vc2 / (gc1 // 2)))
        delta3 = "${:>+6.2f}\\%$".format(100 * (-1 + vc3 / (gc1 // 2)))
        subtable += line_fmt.format(t1, var1, n1, gc1, sc1, vc1, "---")
        subtable += line_fmt.format(
            t2, var2, n2, gc2, int(sc2), int(vc2), delta2
        )
        subtable += (
            line_fmt.format(t3, var3, n3, gc3, int(sc3), int(vc3), delta3)
            + "    \\midrule\n"
        )
    subtable += subtable_footer

    return subtable


def table_2():
    table_header = (
        "\\begin{table*}[htbp]\n"
        "  \\setlength{\\tabcolsep}{6pt}\n"
        "  \\centering\n"
        "  \\caption{Suggested generalized parameters for constant-sum "
        "\\wots{},\n"
        "    minimizing key generation or signature verification costs.\n"
        "    Mean costs over multiple signatures are underlined.}"
        "\\label{tab:params}\n"
    )
    table_footer = "\\end{table*}"

    table = table_header
    table += subtable_2("params-min-256.txt", 256)
    table += "  \\qquad\n"
    table += subtable_2("params-min-512.txt", 512)
    table += table_footer

    return table


if __name__ == "__main__":
    print(table_1())
    print(table_2())
