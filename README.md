# **Sp**ectral **R**elevance **In**vestigating **Cl**usters

There are two command-line interfaces:

## Sprincl for Analysis

```sh
sprincl \
        --modify \
        --overwrite \
        --exname n38194990 \
        "/path/to/analysis/output.h5" \
    embed \
        --eigvals 32 \
        --knn 8 \
        --no-modify
        --label-filter 382 \
        "/path/to/attribution.h5" \
    cluster \
        --eigvals 8 \
        --clusters 2,3,4,5,6,7,8,9,10,11,12 \
    tsne \
        --eigvals 8
```

## Vispr for Visualization

```sh
vispr \
    --address 0.0.0.0 \
    --port 5096 \
    "/path/to/input/image/folder" \
    "/path/to/attribution.h5" \
    "/path/to/analysis.h5" \
    "/path/to/wordmap.json" \
    "/path/to/label_wnids.txt"
```
