'''
Bloom Filter
    False positive matches are possible, but false negatives are not - in other words, a query returns either "possibly in set" or "definitely not in set".

False Positive 
    An error in data reporting in which a test result improperly indicates presence of a condition, such as a disease (the result is positive), when in reality it is not present.

False Negative 
    An error in which a test result improperly indicates no presence of a condition (the result is negative), when in reality it is present.
'''
import matplotlib.pyplot as plt
import random
import string
import sys
import time
import os
import psutil
import argparse


'''
add_and_check
'''

def add_and_check(myset, key2add, key2check, verbose):
    hit = False
    if verbose:
        print('Adding :'+key2add)

    myset.add(key2add)

    if(key2check is None):
        key2check = key2add

    hit = key2check in myset

    if verbose:
        if hit:
            print("Found :"+key2check)
        else:
            print("Not Found :"+key2check)

    return hit

'''
test
    We keep the unit testing under this method.
'''
def test():
    # instantiate BloomFilter with custom settings,
    # max_elements is how many elements you expect the filter to hold.
    # error_rate defines accuracy; You can use defaults with
    # `BloomFilter()` without any arguments. Following example
    # is same as defaults:
    prev_key = None
    myset = set([])

    for i in range(0, 10):
        key = str(i)
        if add_and_check(myset, key, prev_key, True):
            print ('Success')
        prev_key = key

'''
analyse
    We keep the analysis under this method.
'''
def analyse(max_elements, error_rate, iteration_count, population_count): 
    process = psutil.Process(os.getpid())
    m0 = process.memory_info().rss
    print('Initial Memory : '+str(m0))
    myset = set([])
    m0 = process.memory_info().rss
    print('Memory after Bloom Filter: '+str(m0))

    count_false_positive = 0
    count_false_negative = 0

    #-
    # Iterate and monitor the parameters in each iteration.
    # Measure the parameters at the begining and end of each iteration
    #-
    '''
    Iteration,   Count,    F +ve,    F -ve,       Time,   Memory
           1,    10000,   0.0000,   0.0000, 0.86896200,   360448
           1,    20000,   0.0000,   0.0000, 0.87001700,        0
           1,    30000,   0.0000,   0.0000, 0.87261100,    12288
           1,    40000,   0.0000,   0.0000, 0.87400500,        0
           1,    50000,   0.0020,   0.0000, 0.87497200,        0
           1,    60000,   0.0100,   0.0000, 0.87615900,        0
           1,    70000,   0.0270,   0.0000, 0.87717300,        0
           1,    80000,   0.0580,   0.0000, 0.88109100,        0

    '''
    print('Iteration,   Count,    F +ve,    F -ve,       Time,   Memory')
    iter = []
    false_positive = []
    false_negative = []
    time_measured = []
    memory_measured = []


    for i in range(0, iteration_count):
        #record the time stamp
        m0 = process.memory_info().rss
        t0 = time.clock()

        #add entries
        prev_key = None
        for j in range (0, population_count):
            #generate a random number and add it to the bloom filter
            key = str( random.randint(0, sys.maxint) )
            if prev_key is None:
                prev_key = key

            myset.add(key)

            #lets check whatever we just added is present or not
            if prev_key not in myset:
                count_false_negative += 1

            # We never generated any with 'x'. So shouldn't be there.
            if (key+'x') in myset:
                count_false_positive += 1


        #lets analyze the current hits and analyse the error, time and memory
        t_delta = time.clock() - t0
        #calculate the error
        actual_count = (i+1) * population_count
        err_false_positive = (count_false_positive)*100.0/(actual_count*1.0)
        err_false_negative = (count_false_negative)*100.0/(actual_count*1.0)
        #calculate memory growth
        m_delta = process.memory_info().rss - m0


        print('{:8d}'.format(i)+', '+ 
              '{:8d}'.format(actual_count)+', '+
              '{:8.4f}'.format(round(err_false_positive,3))+', '+
              '{:8.4f}'.format(round(err_false_negative,3))+', '+
              '{:10.8f}'.format(t_delta)+', '+
              '{:8d}'.format(m_delta))
        sys.stdout.flush()

        iter.append(i)
        false_positive.append(err_false_positive)
        false_negative.append(err_false_negative)
        time_measured.append(t_delta)
        memory_measured.append(m_delta)

    fig, ax = plt.subplots()
    ax.margins(0.02, 0.02)

    ax.set_xlabel('Population Count ( x'+'{:,}'.format(population_count)+' )')
    #ax.plot(iter, false_positive, label='False +ve(%)')
    #ax.plot(iter, false_negative, label='False -ve(%)')
    #ax.plot(iter, memory_measured, label='Memory')
    total_memory = 0;
    mem_accumulated = []
    for x in memory_measured:
        total_memory += x;
        mem_accumulated.append(total_memory/1024/1024)
    ax.plot(iter, mem_accumulated, label='Memory (MB)')
    #ax.plot(iter, [x/1024/1024 for x in memory_measured], label='Memory (MB)')
    #ax.plot(iter, time_measured, label='Time(Sec)')

    ax.grid(True, which='both')
    ax.set_title("Set")
    ax.legend(loc='best')
    plt.show()


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("--test", 
                    help="Test Run",
                    action="store_true")

    ap.add_argument("-i", "--iterations", 
                    help="Number of Iterations",
                    type=int,
                    default=10)

    ap.add_argument("-p", "--population", 
                    help="Population Count per Iteration",
                    type=int,
                    default=1000000)

    ap.add_argument("-m", "--max", 
                    help="Max Number",
                    type=int,
                    default=100000)


    ap.add_argument("-e", "--error", 
                    help="Error Tolerance",
                    type=float,
                    default=0.01)


    args = ap.parse_args()
    if(args.test):
        test()
    else:
        print('Capacity :'+str(args.max))
        print('Err Tolerance :'+str(args.error))
        print('#Iterations :'+str(args.iterations))
        print('Population per Iteration :'+str(args.population))
        analyse(args.max, args.error, args.iterations, args.population)
      
   
if __name__ == "__main__":
    main()
