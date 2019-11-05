#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103, C0326

from __future__ import absolute_import
from collections import defaultdict
from sys import argv
from typing import Tuple


def create_bench_file(params: Tuple[Tuple[str, int, int, int]]) -> str:
    header = (
        """#include "primitives/OpenSSLSha256.h"\n"""
        """#include "primitives/OpenSSLSha512.h"\n"""
        """#include "wots/BSConstantSumWots.h"\n"""
        """#include "wots/ClassicWots.h"\n"""
        """#include "wots/ConstantSumWots.h"\n"""
        """#include "wots/MConstantSumWots.h"\n"""
        """#include "wots/OriginalConstantSumWots.h"\n"""
        """#include "wots/OriginalOptConstantSumWots.h"\n"""
        """#include <benchmark/benchmark.h>\n"""
        "\ntemplate <class OTS>\n"
        "class OTSFixture : public benchmark::Fixture, "
        "protected OpenSSLSha256 {\n"
        "public:\n"
        "  ByteArray data, data2;\n"
        "  OTS ots;\n"
        "  std::vector<unsigned int> fing;\n"
        "  virtual void SetUp(benchmark::State &state) {\n"
        """    data = hstoba("0102030F");\n"""
        "    data2 = digest(data);\n"
        "    fing = ots.genFingerprint(data2);\n"
        "  }\n"
        "};\n\n"
    )
    footer = "BENCHMARK_MAIN();"

    template = (
        "BENCHMARK_TEMPLATE_F(OTSFixture, plot_{},\n"
        "                     {}ConstantSumWots<{}, {}, {}, {}>)\n"
        "(benchmark::State &state) {{\n"
        "  std::vector<unsigned int> a;\n"
        "  for (auto _ : state) {{\n"
        "    data = digest(data);\n"
        "    benchmark::DoNotOptimize(a = ots.genFingerprint(data));\n"
        "  }}\n"
        "}}\n\n"
    )

    template_verify = (
        "BENCHMARK_TEMPLATE_F(OTSFixture, plot_{},\n"
        "                     {}ConstantSumWots<{}, {}, {}, {}>)\n"
        "(benchmark::State &state) {{\n"
        "  std::vector<unsigned int> a;\n"
        "  for (auto _ : state) {{\n"
        "    data = digest(data2);\n"
        "    benchmark::DoNotOptimize(ots.check_encoding(data, fing));\n"
        "  }}\n"
        "}}\n\n"
    )

    _file = header
    for h, t, n, s in params:
        _set = (str(t) + str(n) + str(s), h, n, t, s)
        _file += template.format(_set[0] + "O", "Original", *_set[1:])
        _file += template.format(_set[0] + "OS", "OriginalOpt", *_set[1:])
        _file += template.format(_set[0], "", *_set[1:])
        _file += template.format(_set[0] + "M", "M", *_set[1:])
        _file += template.format(_set[0] + "BS", "BS", *_set[1:])
        _file += template_verify.format(_set[0] + "BSV", "BS", *_set[1:])
    _file += footer

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
            # minvc = min(v, key=lambda x: x[1])
            # results += (("OpenSSLSha{}".format(m), t, minvc[0], minvc[-1]),)
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
