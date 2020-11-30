#!/usr/bin/env awk -f

BEGIN {
    getline;
    while ($0 ~ !/^\./) {
        getline;
    }
    split($0, header, "; ")
}

/Generating/ {
    if (!(i % 19)) {
        i = 1
    }
    name = header[i++]; gc = $8;
    getline; getline; getline; sc = $3;
    getline; getline; getline; getline; sce = $3;
    getline; getline; getline; getline; vc = $3;
    getline; getline; getline; getline; vce = $3;

    values[name][0] += gc
    values[name][1] += sc
    values[name][2] += sce
    values[name][3] += sce / sc * 100
    values[name][4] += vc
    values[name][5] += vce
    values[name][6] += vce / vc * 100
}

END {
    for (type in header) {
        printf "%s ", header[type]
        for (column in values[header[type]]) {
            printf "%4E ", values[header[type]][column] / (ARGC - 1)
        }
        printf "\n"
    }
}
