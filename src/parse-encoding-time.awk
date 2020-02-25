#!/usr/bin/env awk -f

BEGIN {
    FS = "[><]"
}

"/OTSFixture/" {
    if ($2) !variants[$2]++
    if ($3) {
        split($5, v, " ")
        values[substr($3, 16)][$2] = v[2]
    }
}

END {
    for (param in values) {
        printf "%s ", param
        for (variant in variants) {
            n = values[param][variant]
            if (!n) n = "inf"
            printf "%s ", n
        }
        printf "\n"
    }
}
