#-
# Membership using bloom filter
#-
from bloom_filter import BloomFilter
# Initialize
ds = BloomFilter(max_elements=10000, error_rate=0.1)
# Add
ds.add(1)
ds.add(2)
ds.add(6)

# Test
assert 1 in ds 
assert 3 not in ds 
