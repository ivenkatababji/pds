#-
# Frequency using CSK
#-
from countminsketch import CountMinSketch
# Initialize
# table size=1000, hash functions=10
ds = CountMinSketch(1000, 10)
# Add
ds.add(1)
ds.add(2)
ds.add(1)

# Test
assert  ds[1] == 2 
assert  ds[2] == 1 
assert  ds[3] == 0
