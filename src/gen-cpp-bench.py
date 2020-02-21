#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103, C0326, W0631

from __future__ import absolute_import
from collections import defaultdict
from sys import argv
from typing import Tuple


def create_bench_file(params: Tuple[Tuple[str, int, int, int]]) -> str:
    header = (
        """#include "OpenSSLSha256.h"\n"""
        """#include "OpenSSLSha512.h"\n"""
        """#include "Wots.h"\n"""
        """#include "WotsCS.h"\n"""
        """#include "WotsDCS.h"\n"""
        """#include "WotsMDCS.h"\n"""
        """#include "WotsDBCS.h"\n"""
        """#include "WotsMDBCS.h"\n"""
        """#include <benchmark/benchmark.h>\n"""
        "\ntemplate <class OTS>\n"
        "class OTSFixture : public benchmark::Fixture, "
        "protected OpenSSLSha256 {\n"
        "public:\n"
        "  ByteArray data;\n"
        "  OTS * ots;\n"
        "  virtual void SetUp(benchmark::State &state) {\n"
        "    ots = new OTS();\n"
        """    data = hstoba("FFAB4DF3010102030F");\n"""
        "  }\n"
        "  virtual void TearDown(benchmark::State &state) {\n"
        "    delete ots;\n"
        "  }\n"
        "};\n\n"
    )
    footer = "BENCHMARK_MAIN();"

    template = (
        "BENCHMARK_TEMPLATE_F(OTSFixture, plot_{},\n"
        "                     {}<{}, {}, {}, {}>)\n"
        "(benchmark::State &state) {{\n"
        "  std::vector<unsigned int> a;\n"
        "  for (auto _ : state) {{\n"
        "    data = digest(data);\n"
        "    benchmark::DoNotOptimize(a = ots->gen_fingerprint(data));\n"
        "  }}\n"
        "}}\n\n"
    )

    _file = header
    for h, t, n, s in params:
        _set = (str(t) + str(n) + str(s), h, t, n, s)
        _file += template.format(_set[0] + "_DCS", "WotsDCS", *_set[1:])
        _file += template.format(_set[0] + "_MDCS", "WotsMDCS", *_set[1:])
        _file += template.format(_set[0] + "_DBCS", "WotsDBCS", *_set[1:])
        _file += template.format(_set[0] + "_MDBCS", "WotsMDBCS", *_set[1:])
    _file += footer
    _file.replace("OpenSSLSha256", "OpenSSLSha{}".format(h))

    return _file


def parse_params(path: str) -> defaultdict:
    with open(path) as f:
        data = f.readlines()

    lines = [list(map(int, x)) for x in map(str.split, data)]
    group_t = defaultdict(list)
    for t, n, s, tn in lines:
        group_t[t].append((n, tn, tn - s, s))

    return group_t


def get_params(mode: str, m: int) -> Tuple[Tuple[str, int, int, int]]:
    group_t = parse_params("params-{}-{}.txt".format(mode, m))
    results = ()

    for t, v in group_t.items():
        if mode == "min":
            mingc = min(v, key=lambda x: x[3])
            results += (("OpenSSLSha{}".format(m), t, mingc[0], mingc[-1]),)
        elif mode == "equal":
            mingc = min(v, key=lambda x: x[1])
            results += (("OpenSSLSha{}".format(m), t, mingc[0], mingc[0]),)

    return results


if __name__ == "__main__":
    assert len(argv) == 3
    assert argv[1] == "min" or argv[1] == "equal"
    print(create_bench_file(get_params(argv[1], int(argv[2]))))
