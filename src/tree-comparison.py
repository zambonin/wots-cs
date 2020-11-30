#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103, C0330, R0914, W1636

from __future__ import absolute_import
from collections import defaultdict


def table_4():
    table_header = (
        "\\begin{table*}[htbp]\n"
        "  \\renewcommand{\\arraystretch}{1.2}\n"
        "  \\setlength{\\tabcolsep}{13pt}\n"
        "  \\centering\n"
        "  \\caption{Performance of different encoding algorithms in the\n"
        "    context of \\texttt{XMSS\\_SHA2\\_10\\_256}, in tens of\n"
        "    millions of CPU cycles $(\\times 10^{7})$. Values in square\n"
        "    brackets are the percentage of the cost dedicated solely to\n"
        "    encoding.}\\label{tab:xmss}\n"
        "  \\begin{tabular}{l*{6}{r}}\n"
        "    \\toprule\n"
        "    \\multirow{2}{2cm}{Encoding algorithm(s)}\n"
        "      & \\multicolumn{3}{c}{$t = 67$}\n"
        "      & \\multicolumn{3}{c}{$t = 34$} \\\\\n"
        "      & $C_{x}(\\textsc{Gen})$ & $C_{x}(\\textsc{Sig})$\n"
        "      & $C_{x}(\\textsc{Ver})$ & $C_{x}(\\textsc{Gen})$\n"
        "      & $C_{x}(\\textsc{Sig})$ & $C_{x}(\\textsc{Ver})$ "
        "\\\\ \\midrule \n"
    )
    table_footer = "    \\bottomrule\n  \\end{tabular}\n\\end{table*}"

    with open("data-xmss-256-512.txt") as f:
        data = f.readlines()

    results = defaultdict(list)
    for line in data:
        row = line.split()
        name = row[0].rsplit("-", 1)[0]
        results[name] += map(float, (row[1], row[2], row[4], row[5], row[7]))

    first_row = {
        "./test/basew": "\\texttt{base-w}",
        "./test/dcs": "\\textsc{dcs}",
        "./test/dbcs": "\\textsc{dbcs}",
        "./test/dcs-vcs": "\\textsc{dcs} + \\textsc{vcs}",
        "./test/dbcs-vcs": "\\textsc{dbcs} + \\textsc{vcs}",
        "./test/dcs-m": "\\textsc{dcs-m}",
        "./test/dbcs-m": "\\textsc{dbcs-m}",
        "./test/dcs-m-vcs-m": "\\textsc{dcs-m} + \\textsc{vcs-m}",
        "./test/dbcs-m-vcs-m": "\\textsc{dbcs-m} + \\textsc{vcs-m}",
    }

    line_fmt = (
        "{:>32} & {:>8.2f} & {:>6.2f} \\scriptsize{{[${:>6.3f}\\%$]}}"
        " & {:>4.2f} \\scriptsize{{[${:>6.3f}\\%$]}}\n"
        "{:>32} & {:>8.2f} & {:>6.2f} \\scriptsize{{[${:>6.3f}\\%$]}}"
        " & {:>4.2f} \\scriptsize{{[${:>6.3f}\\%$]}} \\\\\n"
    )

    table = table_header
    for n, v in results.items():
        gen67, sig67, ver67 = v[0] / 1e7, v[1] / 1e7, v[3] / 1e7
        gen34, sig34, ver34 = v[5] / 1e7, v[6] / 1e7, v[8] / 1e7
        table += line_fmt.format(
            first_row[n], gen67, sig67, v[2], ver67, v[4],
            "", gen34, sig34, v[7], ver34, v[9],
        )
    table += "    \\midrule\n" + table_footer

    return table


if __name__ == "__main__":
    print(table_4())
