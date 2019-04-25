#!/usr/bin/env python
import numpy as np
from scipy.linalg import eigh
from matplotlib import pyplot as plt

k = 4
data = np.concatenate([np.random.normal(c, 1, size=100) for c in range(0, 40, 10)])
sim = np.exp(-np.abs(data[None] - data[:, None])/(2))
deg = np.diag(sim.sum(1))
#lap = np.eye(len(deg)) - (np.linalg.inv(deg)) @ sim
lap = np.eye(len(deg)) - (lambda D: D @ sim @ D)(np.linalg.inv(deg)**.5)
ew, ev = eigh(lap, eigvals=(0, 9))
#T = ev[:k]
#T /= np.linalg.norm(T, axis=1, keepdims=True)

fig = plt.figure()
ax1 = plt.subplot(121)
ax1.hist(data, bins=50)
ax2 = plt.subplot(122)
ax2.scatter(range(len(ew)), ew)
fig.show()
