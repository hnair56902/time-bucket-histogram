# time-bucket-histogram

Groups timestamped events into fixed-size chronological buckets and reports counts per bucket.

```python
from time_bucket_histogram import TimeBucketHistogram

hist = TimeBucketHistogram(bucket_size=60)
hist.add(timestamp=45)
hist.add(timestamp=50)
hist.add(timestamp=120)
print(hist.bucket_counts())  # {0: 2, 120: 1}
print(hist.total())          # 3
```

The library exists for the common need to summarise a stream of timestamped events into fixed-width time intervals — request rates, error counts, sensor readings — without pulling in a metrics framework or a plotting library. The trade-off is simplicity over features: there is no merging, no percentile estimation, and no retention window. If you need those, reach for something larger.

Buckets are aligned to the Unix epoch (timestamp 0), not to the first event. This means two histograms built independently with the same `bucket_size` will always have matching bucket keys, which matters if you later compare or combine their output dictionaries by hand.

The edge you will hit: timestamps must be numeric and share the same unit as `bucket_size`. If your timestamps are in milliseconds and you pass a `bucket_size` of 60 expecting one-minute buckets, you will get buckets spanning 60 milliseconds instead. There is no unit detection — the library treats both values as plain numbers.

Negative timestamps (pre-epoch) are supported and use floor division, so a timestamp of `-1` with a bucket size of `60` lands in the bucket `[-60, 0)`, not `[0, 60)`.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

