import math
import unittest

from time_bucket_histogram import TimeBucketHistogram


class TestTimeBucketHistogram(unittest.TestCase):

    def test_single_event_lands_in_correct_bucket(self):
        hist = TimeBucketHistogram(60)
        hist.add(0)
        self.assertEqual(hist.bucket_counts(), {0: 1})

    def test_event_within_bucket_stays_in_that_bucket(self):
        hist = TimeBucketHistogram(60)
        hist.add(45)
        self.assertEqual(hist.bucket_counts(), {0: 1})

    def test_events_in_same_bucket_accumulate(self):
        hist = TimeBucketHistogram(60)
        hist.add(10)
        hist.add(20)
        hist.add(59)
        self.assertEqual(hist.bucket_counts(), {0: 3})

    def test_events_spanning_multiple_buckets(self):
        hist = TimeBucketHistogram(60)
        hist.add(0)
        hist.add(60)
        hist.add(120)
        self.assertEqual(hist.bucket_counts(), {0: 1, 60: 1, 120: 1})

    def test_total_sums_all_buckets(self):
        hist = TimeBucketHistogram(60)
        hist.add(0, 2)
        hist.add(60, 3)
        self.assertEqual(hist.total(), 5)

    def test_default_count_is_one(self):
        hist = TimeBucketHistogram(60)
        hist.add(30)
        self.assertEqual(hist.total(), 1)

    def test_weighted_counts(self):
        hist = TimeBucketHistogram(60)
        hist.add(10, 5)
        hist.add(20, 7)
        self.assertEqual(hist.bucket_counts(), {0: 12})

    def test_zero_count_is_noop(self):
        hist = TimeBucketHistogram(60)
        hist.add(10, 0)
        self.assertEqual(hist.bucket_counts(), {})
        self.assertEqual(hist.total(), 0)

    def test_returned_dict_is_a_copy(self):
        hist = TimeBucketHistogram(60)
        hist.add(0)
        counts = hist.bucket_counts()
        counts[0] = 999
        self.assertEqual(hist.bucket_counts(), {0: 1})

    def test_bucket_size_property(self):
        hist = TimeBucketHistogram(100)
        self.assertEqual(hist.bucket_size, 100)

    def test_non_positive_bucket_size_raises(self):
        with self.assertRaises(ValueError):
            TimeBucketHistogram(0)
        with self.assertRaises(ValueError):
            TimeBucketHistogram(-10)

    def test_negative_count_raises(self):
        hist = TimeBucketHistogram(60)
        with self.assertRaises(ValueError):
            hist.add(10, -1)

    def test_negative_timestamp_uses_floor_division(self):
        """A timestamp of -1 with bucket size 60 must fall in [-60, 0).

        Python's floor division gives -1 // 60 == -1, so the bucket start is
        -60. This is the natural choice for chronological alignment and keeps
        negative timestamps consistent with positive ones.
        """
        hist = TimeBucketHistogram(60)
        hist.add(-1)
        self.assertEqual(hist.bucket_counts(), {-60: 1})

    def test_negative_timestamp_at_boundary(self):
        """Timestamp -60 starts its own bucket rather than belonging to [-120, -60)."""
        hist = TimeBucketHistogram(60)
        hist.add(-60)
        self.assertEqual(hist.bucket_counts(), {-60: 1})

    def test_empty_histogram(self):
        hist = TimeBucketHistogram(60)
        self.assertEqual(hist.bucket_counts(), {})
        self.assertEqual(hist.total(), 0)

    def test_float_bucket_size_and_timestamp(self):
        """Floats work as long as bucket_size and timestamps share units."""
        hist = TimeBucketHistogram(0.5)
        hist.add(0.1)
        hist.add(0.6)
        # 0.1 // 0.5 == 0.0  -> bucket start 0.0
        # 0.6 // 0.5 == 1.0  -> bucket start 0.5
        self.assertEqual(hist.bucket_counts(), {0.0: 1, 0.5: 1})

    def test_mixed_positive_and_negative_timestamps(self):
        hist = TimeBucketHistogram(60)
        hist.add(-61)   # bucket -120
        hist.add(-60)   # bucket -60
        hist.add(-1)    # bucket -60
        hist.add(0)     # bucket 0
        hist.add(59)    # bucket 0
        self.assertEqual(
            hist.bucket_counts(),
            {-120: 1, -60: 2, 0: 2},
        )


if __name__ == "__main__":
    unittest.main()
