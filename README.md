# **Sp**ectral **R**elevance **In**vestigating **Cl**usters

There are two command-line interfaces:

#### sprincl for analysis
```sh
sprincl \
    embed \
        --eigvals 32 \
        --knn 8 \
        --pass \
        "/path/to/attribution.h5" \
        "/path/to/analysis.h5" \
    cluster \
        --eigvals 8 \
        --clusters 2,3,4,5,6,7,8,9,10,11,12 \
        --overwrite \
        "/path/to/source/analysis.h5" \
        "/path/to/output/analysis.h5" \
    tsne \
        --eigvals 8 \
        "/path/to/source/analysis.h5" \
        "/path/to/output/analysis.h5"
```

#### vispr for visualization
```sh
vispr \
    --address 0.0.0.0 \
    --port 5096 \
    "/path/to/input/image/folder" \
    "/path/to/attribution.h5" \
    "/path/to/analysis.h5" \
    "/path/to/wordmapping.json"
```

