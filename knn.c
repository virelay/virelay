#include <stdio.h>
#include <string.h>

const ftype vec[64] = {1., 1., 1., 1., 1., 1., 1., 1.,
                       1., 1., 1., 1., 1., 1., 1., 1.,
                       1., 1., 1., 1., 1., 1., 1., 1.,
                       1., 1., 1., 1., 1., 1., 1., 1.,
                       1., 1., 1., 1., 1., 1., 1., 1.,
                       1., 1., 1., 1., 1., 1., 1., 1.,
                       1., 1., 1., 1., 1., 1., 1., 1.,
                       1., 1., 1., 1., 1., 1., 1., 1.};

typedef ftype float;

struct segment {
    unsigned int index;
    ftype dist;
    struct segment next;
};

void segment_init(struct segment *this) {
    this->index = 0;
    this->dist = -1;
    this->next = NULL;
}

void segment_put(struct segment *this, const unsigned int index, const ftype dist, const unsigned int max_nei){
    unsigned int i;
    struct segment *cur = this;
    unsigned int cindex = index;
    ftype cdist = dist;
    for (i=0;i<max_nei;i++){
        if (cur->dist < 0){
            cur->dist = cdist;
            cur->index = cindex;
            break;
        } else if (cur->dist > dist){
        }
        if (cur->next == NULL){

        } else {
            cur = cur->next;
        }
    }
}

struct segment *segmented_knn(const ftype *vec, const unsigned int len, const unsigned int dim, const unsigned int max_nei) {
    unsigned int i, j;
    struct segment neigh = (struct segment *)malloc(len*sizeof(struct segment));
    for (i=0;i<len;i++)
        segment_init(neigh[i]);
    for (i=0;i<len;i++){
        for (j=i+1;j<len;j++){
            ftype dist = dist_func(vec[i*dim], vec[j*dim], dim);
            segment_put(neigh[i], j, dist);
            segment_put(neigh[j], i, dist);
        }
    }
}
