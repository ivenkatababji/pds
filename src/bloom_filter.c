/*
Bloom filter with Murmur hash and Kirsch-Mitzenmacher Optimization.
VenkataBabji@gmail.com
*/
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <locale.h>
#include <ctype.h>

// call this function to start a nanosecond-resolution timer
struct timespec timer_start()
{
    struct timespec start_time;
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &start_time);
    return start_time;
}

// call this function to end a timer, returning nanoseconds elapsed as a long
long timer_end(struct timespec start_time)
{
    struct timespec end_time;
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &end_time);
    long diffInNanos = (end_time.tv_sec - start_time.tv_sec) * (long)1e9 + (end_time.tv_nsec - start_time.tv_nsec);
    return diffInNanos;
}

// MurmurHash3 implementation
void MurmurHash3_x86_32(const void *key, int len, uint32_t seed, void *out) {
    const uint8_t *data = (const uint8_t *)key;
    const int nblocks = len / 4;
    uint32_t h1 = seed;
    const uint32_t c1 = 0xcc9e2d51;
    const uint32_t c2 = 0x1b873593;

    for (int i = 0; i < nblocks; i++) {
        uint32_t k1 = *(uint32_t *)(data + i * 4);
        k1 *= c1;
        k1 = (k1 << 15) | (k1 >> (32 - 15));
        k1 *= c2;
        h1 ^= k1;
        h1 = (h1 << 13) | (h1 >> (32 - 13));
        h1 = h1 * 5 + 0xe6546b64;
    }

    const uint8_t *tail = data + nblocks * 4;
    uint32_t k1 = 0;
    switch (len & 3) {
        case 3: k1 ^= tail[2] << 16;
        case 2: k1 ^= tail[1] << 8;
        case 1: k1 ^= tail[0];
                k1 *= c1;
                k1 = (k1 << 15) | (k1 >> (32 - 15));
                k1 *= c2;
                h1 ^= k1;
    }

    h1 ^= len;
    h1 ^= h1 >> 16;
    h1 *= 0x85ebca6b;
    h1 ^= h1 >> 13;
    h1 *= 0xc2b2ae35;
    h1 ^= h1 >> 16;

    *(uint32_t *)out = h1;
}

// Bloom filter struct
typedef struct {
    uint8_t *bit_array;  // Bit array for the Bloom filter
    size_t size;         // Size of the bit array in bits
    int num_hashes;      // Number of hash functions
} BloomFilter;

// Create a new Bloom filter
BloomFilter *create_bloom_filter(size_t num_elements, double error_rate) {
    // Calculate optimal size of the Bloom filter (m) and number of hash functions (k)
    size_t m = (size_t)ceil(-(num_elements * log(error_rate)) / (log(2) * log(2)));
    int k = (int)round((double)m / num_elements * log(2));

    BloomFilter *bloom = malloc(sizeof(BloomFilter));
    bloom->size = m;
    bloom->num_hashes = k;
    bloom->bit_array = calloc((m + 7) / 8, sizeof(uint8_t)); // Allocate and zero-initialize bit array
    
    return bloom;
}

// Free the Bloom filter
void free_bloom_filter(BloomFilter *bloom) {
    free(bloom->bit_array);
    free(bloom);
}

// Add an item to the Bloom filter
void bloom_add(BloomFilter *bloom, const char *item) {
    uint32_t h1, h2;
    MurmurHash3_x86_32(item, strlen(item), 0x9747b28c, &h1); // First hash
    MurmurHash3_x86_32(item, strlen(item), 0x3c6ef372, &h2); // Second hash

    for (int i = 0; i < bloom->num_hashes; i++) {
        uint32_t index = (h1 + i * h2) % bloom->size; // Kirsch-Mitzenmacher optimization
        bloom->bit_array[index / 8] |= (1 << (index % 8)); // Set the bit
    }
}

// Check if an item is in the Bloom filter
int bloom_check(BloomFilter *bloom, const char *item) {
    uint32_t h1, h2;
    MurmurHash3_x86_32(item, strlen(item), 0x9747b28c, &h1); // First hash
    MurmurHash3_x86_32(item, strlen(item), 0x3c6ef372, &h2); // Second hash

    for (int i = 0; i < bloom->num_hashes; i++) {
        uint32_t index = (h1 + i * h2) % bloom->size; // Kirsch-Mitzenmacher optimization
        if (!(bloom->bit_array[index / 8] & (1 << (index % 8)))) {
            return 0; // If any bit is not set, the item is definitely not present
        }
    }
    return 1; // If all bits are set, the item might be present
}


void gen_rand_str(char* buf, uint32_t len)
{
    buf[len] = 0;
    for(uint32_t i=0; i<len; i++)
    {
        buf[i] = '0' + rand()%72;
    };
}

// Function to convert a string with commas to an integer
int atoi_ex(const char *str) {
    int result = 0;
    int sign = 1;

    // Skip whitespace
    while (*str == ' ') {
        str++;
    }

    // Check for optional sign
    if (*str == '-') {
        sign = -1;
        str++;
    } else if (*str == '+') {
        str++;
    }

    // Convert the number ignoring commas
    while (*str) {
        if (isdigit(*str)) {
            result = result * 10 + (*str - '0');
        } else if (*str != ',') {  // Skip commas, but error on any other non-digit character
            return 0;  // Return 0 or handle error if there's an invalid character
        }
        str++;
    }

    return result * sign;
}

void test(int argc, char** argv)
{
    if(argc <3)
    {
        printf("Arguments required.\n");
        return;
    }

    setlocale(LC_NUMERIC, "");
    size_t num_elements = atoi_ex(argv[1]);  // Expected number of elements
    double error_rate = atof(argv[2]);    // Desired false positive rate

    printf("Capacity : %'zu\nError : %f\n", num_elements, error_rate);
    
    BloomFilter *bloom = create_bloom_filter(num_elements, error_rate);
    printf("Bloom filter created with size: %'lu bits and %'d hash functions\n", bloom->size, bloom->num_hashes);

    const unsigned int count = num_elements*0.9;
    char str_buffer[] = {[42] = '\0'};
    
    uint32_t p_count = 0;//Pass
    uint32_t fp_count = 0; //False +Ve
    uint32_t fn_count = 0; //False -Ve

    struct timespec time_start = timer_start();
    for (uint32_t i=0; i< count; i++) 
    {
        gen_rand_str(str_buffer, 40);
        bloom_add(bloom, str_buffer);
        //Check the added entry ASIS
        if(bloom_check(bloom, str_buffer))
        {
           //Pass
           p_count += 1; 
        }
        else
        {
            //False -Ve.
            fn_count += 1; 
        }
        //Check for the Altered entry.
        str_buffer[40] = 'x';
        str_buffer[41] = 0;
        if(bloom_check(bloom, str_buffer))
        {
            //False +Ve.
           fp_count += 1; 
        }
    }
    
    free_bloom_filter(bloom);
    const long t = timer_end(time_start);
    printf("Number of entries added : %'u\n", count);
    printf("Time taken : %'ld ms\n", t/1000/1000);
    printf("Pass Count : %'u\n", p_count);
    printf("Fale -Ve Count : %'u\n", fn_count);
    printf("Fale +Ve Count : %'u\n", fp_count);

    return;
}

int main(int argc, char** argv) 
{
    test(argc, argv);
    return 0;
}
