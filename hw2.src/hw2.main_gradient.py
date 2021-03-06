# !/bin/env python3

from lz import *
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(16)
# generate double moon data

distance, radius, width = -5, 10, 6
sample = 500

minx, maxx = -(radius + width / 2), (2 * radius + width / 2)
miny, maxy = -(radius + width / 2 + distance), (radius + width / 2)
x = np.random.uniform(minx, maxx, size=sample)
y = np.random.uniform(miny, maxy, size=sample)


def cal_distance(x, y, x0, y0):
    dist = (x - x0) ** 2 + (y - y0) ** 2
    dist = np.sqrt(dist)
    return dist


# 计算距离的平方和


dist_a = cal_distance(x, y, 0, 0)
dist_b = cal_distance(x, y, radius, -distance)

is_a = (dist_a <= radius + width / 2) * \
       (dist_a >= radius - width / 2) * (y >= 0)
is_b = (dist_b <= radius + width / 2) * \
       (dist_b >= radius - width / 2) * (y <= -distance)

train_pnts = np.vstack((x, y)).transpose()
train_a = train_pnts[is_a, :]
train_b = train_pnts[is_b, :]

train_pnts = np.vstack((train_a, train_b))
train_targets = np.hstack(
    (np.ones(train_a.shape[0]), np.zeros(train_b.shape[0]))
)
npnts = train_pnts.shape[0]
shuffle_ind = np.random.permutation(npnts)

train_pnts = train_pnts[shuffle_ind]
train_targets = train_targets[shuffle_ind]


def moon_plot(X, y):
    y = np.asarray(y, dtype=float).reshape(-1)
    X_a = X[y == 1]
    X_b = X[y == 0]
    plt.figure()
    plt.plot(X_a[:, 0], X_a[:, 1], '.')
    plt.plot(X_b[:, 0], X_b[:, 1], '.')


moon_plot(train_pnts, train_targets)

# k-means

from sklearn.cluster import KMeans

n_clusters = 2
kmeans = KMeans(n_clusters=n_clusters).fit(train_pnts)
moon_plot(train_pnts, kmeans.labels_)

centers = kmeans.cluster_centers_


def cal_distmat(X, Y=None):
    if Y is None:
        Y = X
    distmat = (X ** 2).sum(axis=1).reshape(-1, 1) + \
              (Y ** 2).sum(axis=1).reshape(1, -1) - 2 * np.dot(X, Y.T)
    distmat = np.sqrt(distmat)
    return distmat


distmat = cal_distmat(centers)
d_max = np.max(distmat)

sigma = d_max / np.sqrt(2 * n_clusters)


class RBF(object):
    def __init__(self, centers, sigma, std=1e-3, alpha=0.001, steps=500):
        self.n_clusters = centers.shape[0]
        self.input_dim = centers.shape[1]
        self.out_dim = 1
        self.sigma = sigma
        self.centers = centers
        self.weight = np.random.normal(loc=0.0, scale=std,
                                       size=(self.n_clusters, self.out_dim))
        self.bias = np.zeros((1, self.out_dim))
        self.alpha = alpha
        self.steps = steps

    def gaussian(self, dist):
        return np.exp(- np.square(dist) / (2. * self.sigma ** 2))

    def fit(self, X, y):
        batch_size = X.shape[0]
        hidden = self.cal_hidden(X)
        # datamat = np.concatenate((hidden, np.ones((batch_size, 1))), axis=1)
        alpha = 1e-4
        for k in range(self.steps):
            # param = np.dot(np.dot(np.linalg.inv(np.dot(datamat.T, datamat)), datamat.T), y)
            output = np.dot(X, self.weight)  + self.bias
            output = output.reshape(-1)
            self.weight = self.weight + alpha * (y - output).dot(X).reshape(-1,1)
            self.bias = self.bias + alpha * (y - output).mean()

            # param = param.reshape(self.n_clusters + 1, self.out_dim)
            # self.weight = param[:self.n_clusters, :self.out_dim]
            # self.bias = param[self.n_clusters:, :self.out_dim]

    def cal_hidden(self, X):
        distmat = cal_distmat(X, self.centers)
        return self.gaussian(distmat)

    @staticmethod
    def sigmoid(x):
        return 1. / (1. + np.exp(-x))

    def pred(self, X):
        hidden = self.cal_hidden(X)
        y = np.dot(hidden, self.weight) + self.bias
        return y


rbf = RBF(centers, sigma)
rbf.fit(train_pnts, train_targets)
sample = 999
x = np.linspace(minx, maxx, num=sample)
y = np.linspace(miny, maxy, num=sample)
x, y = np.meshgrid(x, y)
x, y = x.ravel(), y.ravel()

# sample = 9999
# x = np.random.uniform(minx, maxx, size=sample)
# y = np.random.uniform(miny, maxy, size=sample)

test_pnts = np.vstack((x, y)).transpose()

pred = rbf.pred(test_pnts)
pred = pred > 0.5
print(pred)
moon_plot(test_pnts, pred)
plt.show()
