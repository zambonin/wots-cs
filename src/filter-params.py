#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103, C0330, R0914

from __future__ import absolute_import, division
from collections import defaultdict
from importlib import import_module
from math import log2


def table_1() -> str:
    table_header = (
        "\\begin{table}[htbp]\n"
        "  \\renewcommand{\\arraystretch}{1.2}\n"
        "  \\setlength{\\tabcolsep}{10pt}\n"
        "  \\centering\n"
        "  \\caption{Number of iterations of $c_{k}$ for usual\n"
        "    parameters of \\textsc{Wots+}.}\\label{tab:wots}\n"
        "  \\begin{tabular}{*{6}{r}}\n"
        "    \\toprule\n"
        "    $m$ & $t$ & $w$ & $C(\\textsc{Gen})$ & "
        "$\\overline{C(\\textsc{Sig})}$\n"
        "      & $\\overline{C(\\textsc{Ver})}$ \\\\ \\midrule\n"
    )
    table_footer = "    \\bottomrule\n" "  \\end{tabular}\n" "\\end{table}"
    line_fmt = "{:>24} & {:>6d} & {:>6d} & {:>6d} & {:>10} & {:>10} \\\\\n"

    results = defaultdict(list)
    for m in [256, 512]:  # e.g. sha-256, sha-512
        for w in [1 << 4, 1 << 6, 1 << 8]:  # winternitz parameter
            t = SEARCH.wt(m, w)
            gc = t * (w - 1)
            sc = vc = "${:>6.1f}$".format(gc / 2)
            results[m].append((t, w, gc, sc, vc))

    table = table_header
    for t, v in results.items():
        table += line_fmt.format("\\multirow{{3}}{{*}}{{{}}}".format(t), *v[0])
        table += line_fmt.format("", *v[1])
        table += line_fmt.format("", *v[2]) + "    \\midrule\n"
    table += table_footer

    return table


def table_2() -> str:
    table_header = (
        "\\begin{table}[htbp]\n"
        "  \\renewcommand{\\arraystretch}{1.2}\n"
        "  \\centering\n"
        "  \\caption{Number of iterations of $c_{k}$ for \\textsc{Wots-cs}\n"
        "    using \\textsc{MinVer}, and success probability of\n"
        "    \\textsc{cky-i} given as $\\Pr_{enc}$. Recall that\n"
        "    $C(\\textsc{Ver}) = s$.}\\label{tab:cswots}\n"
        "  \\begin{tabular}{*{7}{r}}\n"
        "    \\toprule\n"
        "    $m$ & $t$ & $n$ & $C(\\textsc{Gen})$ & $C(\\textsc{Sig})$\n"
        "      & $C(\\textsc{Ver})$ & $\\Pr_{enc}$ \\\\ \\midrule\n"
    )
    table_footer = "    \\bottomrule\n" "  \\end{tabular}\n" "\\end{table}"
    line_fmt = (
        "{:>24} & {:>24} & {:>6d} & {:>8d} & {:>8d} & {:>24} & {:>14} \\\\\n"
    )
    ts = "\\multirow{{2}}{{*}}{{{}}}"

    results = defaultdict(list)
    for m in [256, 512]:  # e.g. sha-256, sha-512
        for w in [1 << 4, 1 << 6, 1 << 8]:  # winternitz parameter
            t = SEARCH.wt(m, w)
            n, s = SEARCH.single_tau_min_ver(t, m)
            pr_enc = SEARCH.tau_length(t, n, s) / SEARCH.tau_length(t, s, s)
            results[m].append(
                (ts.format(t), s, t * s, t * s - s, ts.format(s), "$1.00$")
            )
            results[m].append(
                ("", n, t * n, t * n - s, "", "$\\sim{:.4f}$".format(pr_enc))
            )

    table = table_header
    for t, v in results.items():
        table += line_fmt.format("\\multirow{{6}}{{*}}{{{}}}".format(t), *v[0])
        table += line_fmt.format("", *v[1])
        table += line_fmt.format("", *v[2])
        table += line_fmt.format("", *v[3])
        table += line_fmt.format("", *v[4])
        table += line_fmt.format("", *v[5]) + "    \\midrule\n"
    table += table_footer

    return table


def subtable_3(path: str, m: int) -> str:
    with open(path) as f:
        data = f.readlines()

    lines = [list(map(float, x)) for x in map(str.split, data)]
    group_t = defaultdict(list)
    for t, n, s, _ in lines:
        group_t[t].append((n, t * n, t * n - s, s))

    wint = defaultdict(list)
    for w in [1 << 4, 1 << 6, 1 << 8]:  # winternitz parameter
        t = SEARCH.wt(m, w)
        gc = t * (w - 1)
        sc = vc = gc // 2
        wint[t].append((w, gc, sc, vc))

    line_fmt = (
        "{:>24} & {:>4} & {:>4.0f} & {:>6.0f} & {:>6.0f} "
        "& {:>6.0f} & {:>10} \\\\\n"
    )

    subtable = ""
    for index, params in enumerate(wint.items()):
        _, gc1, sc1, vc1 = params[1][0]
        n2, gc2, sc2, vc2 = min(group_t[params[0]], key=lambda x: x[1])
        delta_gc = "${:>+6.2f}\\%$".format(100 * (-1 + gc2 / gc1))

        first = "\\multirow{{3}}{{*}}{{{}}}".format(m) if not index else ""
        subtable += line_fmt.format(
            first, params[0], n2, gc2, sc2, vc2, delta_gc,
        )
    subtable += "    \\midrule\n"

    return subtable


def table_3():
    table_header = (
        "\\begin{table}[htbp]\n"
        "  \\renewcommand{\\arraystretch}{1.2}\n"
        "  \\setlength{\\tabcolsep}{6pt}\n"
        "  \\centering\n"
        "  \\caption{Suggested parameters for \\textsc{Wots-cs}\n"
        "    using \\textsc{MinGen} for a given $t$\n"
        "    as compared to \\textsc{Wots+}.}\\label{tab:params}\n"
        "  \\begin{tabular}{rc*{5}rr}\n"
        "    \\toprule\n"
        "    $m$ & $t$ & $n$ & $C(\\textsc{Gen})$ & $C(\\textsc{Sig})$\n"
        "      & $C(\\textsc{Ver})$ & $\\Delta C(\\textsc{Gen})$ "
        "\\\\ \\midrule \n"
    )
    table_footer = "    \\bottomrule\n  \\end{tabular}\n\\end{table}"

    table = table_header
    table += subtable_3("params-min-256.txt", 256)
    table += subtable_3("params-min-512.txt", 512)
    table += table_footer

    return table


def table_5():
    def wotsp_sec_level(l, t, w):
        return l - log2(t * w) - log2(2 * w + 1)

    def wotscs_sec_level(l, t, n, s):
        return (
            l
            + log2(SEARCH.tau_length(t - 1, n, s - n + 1))
            - log2(t * (2 * n + 1) * SEARCH.tau_length(t, n, s))
        )

    l = 256
    params = {
        34: (256, 226, 3643),
        67: (16, 15, 400),
    }

    table_header = (
        "\\begin{table}[htbp]\n"
        "  \\renewcommand{\\arraystretch}{1.2}\n"
        "  \\setlength{\\tabcolsep}{7pt}\n"
        "  \\centering\n"
        "  \\caption{Security level $q$ for \\textsc{Wots+} and\n"
        "    \\textsc{Wots-cs} and $\lambda = m = 256$.}\\label{tab:bounds}\n"
        "  \\begin{tabular}{rc*{5}rr}\n"
        "    \\toprule\n"
        "    Adversary & $t$ & $w$ & $n$ & $s$ & \\textsc{Wots+}\n"
        "      & \\textsc{Wots-cs} \\\\ \\midrule\n"
    )
    table_footer = "    \\bottomrule\n  \\end{tabular}\n\\end{table}"

    line_fmt = (
        "{:>30} & {:>4} & {:>4} & {:>4} & {:>4} & {:>4.2f} & {:>4.2f} \\\\\n"
    )

    table = table_header

    for lamb in [l, l / 2]:
        for t, v in params.items():
            header = ""
            if t == 34 and lamb == l:
                header = "\\multirow{{2}}{{*}}{{{}}}".format("Classical")
            elif t == 34 and lamb == l / 2:
                header = "\\multirow{{2}}{{*}}{{{}}}".format("Quantum")
            table += line_fmt.format(
                header, t, *v, wotsp_sec_level(lamb, t, v[0]),
                wotscs_sec_level(lamb, t, v[1], v[2]),
            )

    table += table_footer

    return table


if __name__ == "__main__":
    SEARCH = import_module("search-params")
    print(table_1())
    print(table_2())
    print(table_3())
    print(table_5())
