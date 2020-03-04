#!/usr/bin/env awk -f

BEGIN {
    getline
    split($0, h, "; ")
    i = 1
}

/Generating/ {
    split(h[i++], v, ";")
    name = v[1]; printf "%s ", name
    gc = $8; printf "%.2e ", gc
    getline; getline; sc = $3; printf "%.2e ", sc
    getline; getline; getline; sce = $3; printf "%.2e ", sce
    printf "%.3lf ", sce / sc * 100
    getline; getline; getline; vc = $3; printf "%.2e ", vc
    getline; getline; getline; vce = $3; printf "%.2e ", vce
    printf "%.3lf\n", vce / vc * 100
}
