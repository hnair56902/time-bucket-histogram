"""Core implementation for grouping timestamped events into fixed-size buckets."""


class TimeBucketHistogram:
    """Groups timestamped events into fixed-size chronological buckets and reports counts.

    Buckets are aligned to the epoch (timestamp 0). For a bucket size of S, a
    given timestamp T falls into the bucket whose start is
    ``floor(T / S) * S``. This keeps bucket boundaries deterministic across
    instances and independent of when events arrive — a property essential
    when merging or comparing histograms from different sources.

    Negative timestamps (e.g. pre-epoch dates in seconds) are handled
    consistently: ``floor`` division and modulo are used so that a timestamp
    like -1 with bucket size 60 lands in the bucket [-60, 0), not [0, 60).
    """

    def __init__(self, bucket_size):
        """Initialise the histogram.

        Args:
            bucket_size: Width of each bucket in the same units as the
                timestamps passed to :meth:`add`. Must be a positive number.

        Raises:
            ValueError: If ``bucket_size`` is not positive.
        """
        if bucket_size <= 0:
            raise ValueError("bucket_size must be positive")
        self._bucket_size = bucket_size
        self._counts = {}

    @property
    def bucket_size(self):
        """Return the configured bucket width."""
        return self._bucket_size

    def _bucket_start(self, timestamp):
        """Return the start of the bucket that ``timestamp`` falls into.

        Uses ``math.floor`` semantics via Python's floor division so that
        negative timestamps produce bucket starts that are multiples of
        ``bucket_size`` and strictly less than or equal to the timestamp.
        """
        return (timestamp // self._bucket_size) * self._bucket_size

    def add(self, timestamp, count=1):
        """Record ``count`` events occurring at ``timestamp``.

        ``count`` may be any non-negative number to support weighted events,
        but it must not be negative — a negative count would silently corrupt
        the histogram in ways the caller would not expect.

        Args:
            timestamp: The event time, in the same units as ``bucket_size``.
            count: How many events (or what weight) to add. Defaults to 1.

        Raises:
            ValueError: If ``count`` is negative.
        """
        if count < 0:
            raise ValueError("count must not be negative")
        if count == 0:
            return
        start = self._bucket_start(timestamp)
        self._counts[start] = self._counts.get(start, 0) + count

    def bucket_counts(self):
        """Return a dictionary mapping bucket start to total count.

        Only buckets with a non-zero count are included. The returned dict is
        a shallow copy; mutating it does not affect the histogram. Iterating
        over a dict is insertion-ordered, so results are chronological by
        first-seen bucket, but callers needing strict chronological order
        should sort the keys themselves.
        """
        return dict(self._counts)

    def total(self):
        """Return the sum of counts across all buckets."""
        return sum(self._counts.values())
