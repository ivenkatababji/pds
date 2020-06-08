#-
# Cardinalityusing estimation HLL
# The set is a built in data structure
#-
import hyperloglog
# Initialize
# accept 1% counting error
ds = hyperloglog.HyperLogLog(0.01)
# Add
ds.add(1)
ds.add(1)
ds.add(2)
ds.add(6)

# Test
assert len(ds) == 3
