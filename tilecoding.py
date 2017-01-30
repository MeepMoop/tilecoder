#!/usr/bin/env python
from __future__ import print_function
import numpy as np

class tilecoder:
  def __init__(self, dims, limits, tilings, step_size=0.1, offset_vec=None):
    self._n_dims = len(dims)
    self._tilings = tilings
    self._offset_vec = np.ones([1, self._n_dims]) if offset_vec is None else np.array([offset_vec])
    self._offsets = np.dot(np.diag(np.arange(float(self._tilings))), np.repeat(self._offset_vec, self._tilings, 0)) / self._tilings
    self._dims = np.array(dims) + self._offset_vec
    self._limits = np.array(limits)
    self._ranges = self._limits[:, 1] - self._limits[:, 0]
    self._alpha = step_size / self._tilings
    self._tiling_size = np.prod(self._dims)
    self._tiles = np.array([0.0] * (self._tilings * self._tiling_size))
    self._tile_ind = np.array([0] * self._tilings)
    self._hash_vec = np.array([1])
    for i in range(len(dims) - 1):
      self._hash_vec = np.hstack([self._hash_vec, dims[i] * self._hash_vec[-1]])

  def _get_tiles(self, x):
    coords = ((x - self._limits[:, 0]) * (self._dims - self._offset_vec) / self._ranges)[0]
    for i in range(self._tilings):
      self._tile_ind[i] = int(i * self._tiling_size + np.dot(self._hash_vec, np.floor(coords + self._offsets[i])))
      
  def set_step_size(self, step_size):
    self._alpha = step_size / self._tilings

  def __getitem__(self, x):
    self._get_tiles(x)
    return np.sum(self._tiles[self._tile_ind])

  def __setitem__(self, x, val):
    self._get_tiles(x)
    self._tiles[self._tile_ind] += self._alpha * (val - np.sum(self._tiles[self._tile_ind]))

def example():
  import matplotlib.pyplot as plt
  from mpl_toolkits.mplot3d import Axes3D

  # tile coder dimensions, limits, and tilings
  dims = [8, 8]
  lims = [(0, 2.0 * np.pi)] * 2
  tilings = 8
  alpha = 0.1
  offset_vec = [1, 3]

  # create tile coder
  T = tilecoder(dims, lims, tilings, alpha, offset_vec)

  # target function with gaussian noise
  def target_ftn(x, y, noise=True):
    return np.sin(x) + np.cos(y) + noise * np.random.randn() * 0.1

  # randomly sample target function until convergence
  batch_size = 50
  for iters in range(200):
    mse = 0.0
    for b in range(batch_size):
      xi = lims[0][0] + np.random.random() * (lims[0][1] - lims[0][0])
      yi = lims[1][0] + np.random.random() * (lims[1][1] - lims[1][0])
      zi = target_ftn(xi, yi)
      T[xi, yi] = zi
      mse += (T[xi, yi] - zi) ** 2
    mse /= batch_size
    print('samples:', (iters + 1) * batch_size, 'batch_mse:', mse)

  # get learned function
  print('mapping function...')
  res = 100
  x = np.arange(lims[0][0], lims[0][1], (lims[0][1] - lims[0][0]) / res)
  y = np.arange(lims[1][0], lims[1][1], (lims[1][1] - lims[1][0]) / res)
  z = np.zeros([len(y), len(x)])
  for i in range(len(x)):
    for j in range(len(y)):
      z[j, i] = T[x[i], y[j]]

  # plot
  fig = plt.figure()
  ax = fig.gca(projection='3d')
  X, Y = np.meshgrid(x, y)
  surf = ax.plot_surface(X, Y, z, cmap=plt.get_cmap('hot'))
  plt.show()

if __name__ == '__main__':
  example()
