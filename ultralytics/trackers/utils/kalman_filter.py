# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

from __future__ import annotations

import numpy as np


class KalmanFilterXYAH:
    """A KalmanFilterXYAH class for tracking bounding boxes in image space using a Kalman filter.

    Implements a simple Kalman filter for tracking bounding boxes in image space. The 8-dimensional state space (x, y,
    a, h, vx, vy, va, vh) contains the bounding box center position (x, y), aspect ratio a, height h, and their
    respective velocities. Object motion follows a constant velocity model, and bounding box location (x, y, a, h) is
    taken as a direct observation of the state space (linear observation model).

    Attributes:
        _motion_mat (np.ndarray): The motion matrix for the Kalman filter.
        _update_mat (np.ndarray): The update matrix for the Kalman filter.
        _std_weight_position (float): Standard deviation weight for position.
        _std_weight_velocity (float): Standard deviation weight for velocity.

    Methods:
        initiate: Create a track from an unassociated measurement.
        predict: Run the Kalman filter prediction step.
        project: Project the state distribution to measurement space.
        multi_predict: Run the Kalman filter prediction step (vectorized version).
        update: Run the Kalman filter correction step.
        gating_distance: Compute the gating distance between state distribution and measurements.

    Examples:
        Initialize the Kalman filter and create a track from a measurement
        >>> kf = KalmanFilterXYAH()
        >>> measurement = np.array([100, 200, 1.5, 50])
        >>> mean, covariance = kf.initiate(measurement)
    """

    def __init__(self):
        """Initialize Kalman filter model matrices with motion and observation uncertainty weights.

        The Kalman filter is initialized with an 8-dimensional state space (x, y, a, h, vx, vy, va, vh), where (x, y)
        represents the bounding box center position, 'a' is the aspect ratio, 'h' is the height, and their respective
        velocities are (vx, vy, va, vh). The filter uses a constant velocity model for object motion and a linear
        observation model for bounding box location.
        """
        ndim, dt = 4, 1.0

        # Create Kalman filter model matrices
        self._motion_mat = np.eye(2 * ndim, 2 * ndim)
        for i in range(ndim):
            self._motion_mat[i, ndim + i] = dt
        self._update_mat = np.eye(ndim, 2 * ndim)

        # Motion and observation uncertainty are chosen relative to the current state estimate
        self._std_weight_position = 1.0 / 20
        self._std_weight_velocity = 1.0 / 160

    def _box_std(self, box: np.ndarray, weight: float, fixed: float) -> list:
        """Return the noise standard deviation of the four box dimensions, scaled by box size.

        This is the only part of the filter that depends on the box parameterization; subclasses override it instead
        of re-implementing `initiate`, `predict`, `project` and `multi_predict`. For (x, y, a, h), x, y and h scale with
        the height and the aspect ratio uses a fixed standard deviation.

        Args:
            box (np.ndarray): State or measurement whose first four entries are the box, shape (4+,) or (N, 4+).
            weight (float): Multiplier applied to the size-dependent dimensions.
            fixed (float): Standard deviation for dimensions that do not scale with box size (the aspect ratio).

        Returns:
            (list): Four standard deviations, scalars for a single box or arrays of shape (N,) for N boxes.
        """
        h = box[..., 3]
        const = fixed * np.ones_like(h) if np.ndim(h) else fixed
        return [weight * h, weight * h, const, weight * h]

    def initiate(self, measurement: np.ndarray):
        """Create a track from an unassociated measurement.

        Args:
            measurement (np.ndarray): Bounding box coordinates (x, y, a, h) with center position (x, y), aspect ratio a,
                and height h.

        Returns:
            mean (np.ndarray): Float64 mean vector (8-dimensional) with zero-initialized velocities.
            covariance (np.ndarray): Float64 covariance matrix (8x8 dimensional).

        Examples:
            >>> kf = KalmanFilterXYAH()
            >>> measurement = np.array([100, 50, 1.5, 200])
            >>> mean, covariance = kf.initiate(measurement)
        """
        measurement = np.asarray(measurement, dtype=np.float64)
        mean_pos = measurement
        mean_vel = np.zeros_like(mean_pos)
        mean = np.r_[mean_pos, mean_vel]

        std = self._box_std(measurement, 2 * self._std_weight_position, 1e-2) + self._box_std(
            measurement, 10 * self._std_weight_velocity, 1e-5
        )
        covariance = np.diag(np.square(std))
        return mean, covariance

    def predict(self, mean: np.ndarray, covariance: np.ndarray):
        """Run Kalman filter prediction step.

        Args:
            mean (np.ndarray): The 8-dimensional mean vector of the object state at the previous time step.
            covariance (np.ndarray): The 8x8-dimensional covariance matrix of the object state at the previous time
                step.

        Returns:
            mean (np.ndarray): Mean vector of the predicted state.
            covariance (np.ndarray): Covariance matrix of the predicted state.

        Examples:
            >>> kf = KalmanFilterXYAH()
            >>> mean = np.array([0, 0, 1, 1, 0, 0, 0, 0])
            >>> covariance = np.eye(8)
            >>> predicted_mean, predicted_covariance = kf.predict(mean, covariance)
        """
        std_pos = self._box_std(mean, self._std_weight_position, 1e-2)
        std_vel = self._box_std(mean, self._std_weight_velocity, 1e-5)
        motion_cov = np.diag(np.square(np.r_[std_pos, std_vel]))

        mean = np.dot(mean, self._motion_mat.T)
        covariance = np.linalg.multi_dot((self._motion_mat, covariance, self._motion_mat.T)) + motion_cov

        return mean, covariance

    def project(self, mean: np.ndarray, covariance: np.ndarray, confidence: float | None = None):
        """Project state distribution to measurement space.

        Args:
            mean (np.ndarray): The state's mean vector (8 dimensional array).
            covariance (np.ndarray): The state's covariance matrix (8x8 dimensional).
            confidence (float, optional): Detection confidence; when set, scales measurement noise by max(1 -
                confidence, 0.05) (NSA-Kalman).

        Returns:
            mean (np.ndarray): Projected mean of the given state estimate.
            covariance (np.ndarray): Projected covariance matrix of the given state estimate.

        Examples:
            >>> kf = KalmanFilterXYAH()
            >>> mean = np.array([0, 0, 1, 1, 0, 0, 0, 0])
            >>> covariance = np.eye(8)
            >>> projected_mean, projected_covariance = kf.project(mean, covariance)
        """
        std = self._box_std(mean, self._std_weight_position, 1e-1)
        innovation_cov = np.diag(np.square(std))
        if confidence is not None:  # NSA-Kalman: scale measurement noise by detection confidence (StrongSORT)
            innovation_cov *= max(1.0 - float(confidence), 0.05)

        mean = mean[:4].copy()
        covariance = covariance[:4, :4]
        return mean, covariance + innovation_cov

    def multi_predict(self, mean: np.ndarray, covariance: np.ndarray):
        """Run Kalman filter prediction step for multiple object states (Vectorized version).

        Args:
            mean (np.ndarray): The Nx8 dimensional mean matrix of the object states at the previous time step.
            covariance (np.ndarray): The Nx8x8 covariance matrix of the object states at the previous time step.

        Returns:
            mean (np.ndarray): Mean matrix of the predicted states with shape (N, 8).
            covariance (np.ndarray): Covariance matrix of the predicted states with shape (N, 8, 8).

        Examples:
            >>> kf = KalmanFilterXYAH()
            >>> mean = np.random.rand(10, 8)  # 10 object states
            >>> covariance = np.random.rand(10, 8, 8)  # Covariance matrices for 10 object states
            >>> predicted_mean, predicted_covariance = kf.multi_predict(mean, covariance)
        """
        std_pos = self._box_std(mean, self._std_weight_position, 1e-2)
        std_vel = self._box_std(mean, self._std_weight_velocity, 1e-5)
        sqr = np.square(np.r_[std_pos, std_vel]).T

        motion_cov = np.zeros((sqr.shape[0], 8, 8))
        motion_cov[:, range(8), range(8)] = sqr

        mean = np.dot(mean, self._motion_mat.T)
        left = np.dot(self._motion_mat, covariance).transpose((1, 0, 2))
        covariance = np.dot(left, self._motion_mat.T) + motion_cov

        return mean, covariance

    def update(
        self, mean: np.ndarray, covariance: np.ndarray, measurement: np.ndarray, confidence: float | None = None
    ):
        """Run Kalman filter correction step.

        Args:
            mean (np.ndarray): The predicted state's mean vector (8 dimensional).
            covariance (np.ndarray): The state's covariance matrix (8x8 dimensional).
            measurement (np.ndarray): The 4 dimensional measurement vector (x, y, a, h), where (x, y) is the center
                position, a the aspect ratio, and h the height of the bounding box.
            confidence (float, optional): Detection confidence; when set, scales measurement noise by max(1 -
                confidence, 0.05) (NSA-Kalman).

        Returns:
            new_mean (np.ndarray): Measurement-corrected state mean.
            new_covariance (np.ndarray): Measurement-corrected state covariance.

        Examples:
            >>> kf = KalmanFilterXYAH()
            >>> mean = np.array([0, 0, 1, 1, 0, 0, 0, 0])
            >>> covariance = np.eye(8)
            >>> measurement = np.array([1, 1, 1, 1])
            >>> new_mean, new_covariance = kf.update(mean, covariance, measurement)
        """
        projected_mean, projected_cov = self.project(mean, covariance, confidence)

        kalman_gain = np.linalg.solve(projected_cov, covariance[:, :4].T).T
        innovation = measurement - projected_mean

        new_mean = mean + np.dot(innovation, kalman_gain.T)
        new_covariance = covariance - np.linalg.multi_dot((kalman_gain, projected_cov, kalman_gain.T))
        return new_mean, new_covariance

    def gating_distance(
        self,
        mean: np.ndarray,
        covariance: np.ndarray,
        measurements: np.ndarray,
        only_position: bool = False,
        metric: str = "maha",
    ) -> np.ndarray:
        """Compute gating distance between state distribution and measurements.

        A suitable threshold for the returned squared Mahalanobis distance is the 95th-percentile chi-square value:
        9.4877 for 4 degrees of freedom when `only_position` is False, and 5.9915 for 2 otherwise. The `"gaussian"`
        metric returns a squared Euclidean distance, for which this threshold does not apply.

        Args:
            mean (np.ndarray): Mean vector over the state distribution (8 dimensional).
            covariance (np.ndarray): Covariance of the state distribution (8x8 dimensional).
            measurements (np.ndarray): An (N, 4) matrix of N measurements, each in format (x, y, a, h) where (x, y) is
                the bounding box center position, a the aspect ratio, and h the height.
            only_position (bool, optional): If True, distance computation is done with respect to box center position
                only.
            metric (str, optional): The metric to use for calculating the distance. Options are 'gaussian' for the
                squared Euclidean distance and 'maha' for the squared Mahalanobis distance.

        Returns:
            (np.ndarray): Returns an array of length N, where the i-th element contains the squared distance between
                (mean, covariance) and `measurements[i]`.

        Raises:
            ValueError: If `metric` is not 'gaussian' or 'maha'.

        Examples:
            Compute gating distance using Mahalanobis metric:
            >>> kf = KalmanFilterXYAH()
            >>> mean = np.array([0, 0, 1, 1, 0, 0, 0, 0])
            >>> covariance = np.eye(8)
            >>> measurements = np.array([[1, 1, 1, 1], [2, 2, 1, 1]])
            >>> distances = kf.gating_distance(mean, covariance, measurements, only_position=False, metric="maha")
        """
        mean, covariance = self.project(mean, covariance)
        if only_position:
            mean, covariance = mean[:2], covariance[:2, :2]
            measurements = measurements[:, :2]

        d = measurements - mean
        if metric == "gaussian":
            return np.sum(d * d, axis=1)
        elif metric == "maha":
            cholesky_factor = np.linalg.cholesky(covariance)
            z = np.linalg.solve(cholesky_factor, d.T)
            return np.sum(z * z, axis=0)  # square maha
        else:
            raise ValueError("Invalid distance metric")


class KalmanFilterXYWH(KalmanFilterXYAH):
    """A KalmanFilterXYWH class for tracking bounding boxes in image space using a Kalman filter.

    Implements a Kalman filter for tracking bounding boxes with state space (x, y, w, h, vx, vy, vw, vh), where (x, y)
    is the center position, w is the width, h is the height, and vx, vy, vw, vh are their respective velocities. The
    object motion follows a constant velocity model, and the bounding box location (x, y, w, h) is taken as a direct
    observation of the state space (linear observation model).

    Attributes:
        _motion_mat (np.ndarray): The motion matrix for the Kalman filter.
        _update_mat (np.ndarray): The update matrix for the Kalman filter.
        _std_weight_position (float): Standard deviation weight for position.
        _std_weight_velocity (float): Standard deviation weight for velocity.

    Methods:
        initiate: Create a track from an unassociated measurement.
        predict: Run the Kalman filter prediction step.
        project: Project the state distribution to measurement space.
        multi_predict: Run the Kalman filter prediction step in a vectorized manner.
        update: Run the Kalman filter correction step.

    Examples:
        Create a Kalman filter and initialize a track
        >>> kf = KalmanFilterXYWH()
        >>> measurement = np.array([100, 50, 20, 40])
        >>> mean, covariance = kf.initiate(measurement)
    """

    def _box_std(self, box: np.ndarray, weight: float, fixed: float) -> list:
        """Return the noise standard deviation of the four box dimensions, scaled by box size.

        For (x, y, w, h) every dimension scales with the box: x and w with the width, y and h with the height, so the
        fixed standard deviation used by the aspect-ratio parameterization is not needed.

        Args:
            box (np.ndarray): State or measurement whose first four entries are the box, shape (4+,) or (N, 4+).
            weight (float): Multiplier applied to the size-dependent dimensions.
            fixed (float): Unused; kept for a uniform signature with `KalmanFilterXYAH._box_std`.

        Returns:
            (list): Four standard deviations, scalars for a single box or arrays of shape (N,) for N boxes.
        """
        w, h = box[..., 2], box[..., 3]
        return [weight * w, weight * h, weight * w, weight * h]
