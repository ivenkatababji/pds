from bloom_filter import BloomFilter
def test(ds):
    ds.add(1)
    ds.add(2)
    ds.add(6)

    if 1 in ds :# True
        print 'test 1 : +ve'
    else:
        print 'test 1 : -ve'

    if 3 in ds :# False
        print 'test 3 : +ve'
    else:
        print 'test 3 : -ve'

print 'Using Set'
myset = set([])
test(myset)

print 'Using Bloom filter'
mybloom = BloomFilter(max_elements=10000, error_rate=0.1)
test(mybloom)
