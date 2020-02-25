#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103, C0326, W0631

from __future__ import absolute_import, division
from collections import defaultdict
from math import floor
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

    is_prob = (
        len(set(i[0] for i in params)) == 1
        and len(set(i[2] for i in params)) == 1
    )

    _file = header
    for t, n, s, h in params:
        _set = (str(t) + str(n) + str(s), "OpenSSLSha{}".format(h), t, n, s)

        if is_prob and n > floor(s / 4):
            _file += template.format(_set[0] + "_CS", "WotsCS", *_set[1:])

        _file += template.format(_set[0] + "_DCS", "WotsDCS", *_set[1:])

        if not is_prob:
            _file += template.format(_set[0] + "_MDCS", "WotsMDCS", *_set[1:])

        _file += template.format(_set[0] + "_DBCS", "WotsDBCS", *_set[1:])

        if not is_prob:
            _file += template.format(
                _set[0] + "_MDBCS", "WotsMDBCS", *_set[1:]
            )
    _file += footer
    _file.replace("OpenSSLSha256", "OpenSSLSha{}".format(h))

    return _file


def parse_params(path: str) -> defaultdict:
    with open(path) as f:
        data = f.readlines()

    return [list(map(int, x)) for x in map(str.split, data)]


if __name__ == "__main__":
    assert len(argv) == 2
    print(create_bench_file(parse_params(argv[1])))
