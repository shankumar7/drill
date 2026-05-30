import math
import time
import numpy as np

class OneEuroFilter:
    def __init__(self, freq, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.freq = freq
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = None
        self.dx_prev = None

    def __call__(self, x, dt=None):
        if dt is None:
            dt = 1.0 / self.freq
        
        if self.x_prev is None:
            self.x_prev = x
            self.dx_prev = np.zeros_like(x)
            return x

        # Calculate derivative
        dx = (x - self.x_prev) / dt
        edx = self._low_pass_filter(dx, self.dx_prev, self._alpha(dt, self.d_cutoff))
        self.dx_prev = edx

        # Calculate cutoff
        cutoff = self.min_cutoff + self.beta * np.abs(edx)
        
        # Filter x
        ex = self._low_pass_filter(x, self.x_prev, self._alpha(dt, cutoff))
        self.x_prev = ex
        return ex

    def _alpha(self, dt, cutoff):
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def _low_pass_filter(self, x, x_prev, alpha):
        return alpha * x + (1.0 - alpha) * x_prev

class PoseSmoother:
    def __init__(self, num_keypoints=17, freq=30):
        # We filter each keypoint (x, y) independently
        self.filters = [OneEuroFilter(freq, min_cutoff=0.5, beta=0.01) for _ in range(num_keypoints)]

    def smooth(self, keypoints):
        """
        keypoints: [17, 3] (x, y, conf)
        """
        smoothed_kp = np.copy(keypoints)
        for i in range(len(self.filters)):
            # Filter x, y
            xy = keypoints[i, :2]
            smoothed_xy = self.filters[i](xy)
            smoothed_kp[i, :2] = smoothed_xy
        return smoothed_kp
