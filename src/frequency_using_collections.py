#-
# Frequency using Collections
# The collections is built in
#-
from collections import Counter
# Initialize
ds = Counter()
# Add
ds[1] += 1
ds[2] += 1
ds[1] += 1

# Test
assert  ds[1] == 2 
assert  ds[2] == 1 
assert  ds[3] == 0
