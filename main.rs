use std::time::Instant;

/// Kadane's algorithm to find the maximum subarray sum in O(n) time.
/// This implementation is mathematically equivalent to the O(n^2) 
/// implementation in the Python code but significantly faster.
fn max_subarray_sum(seed: u32, n: usize, min_val: i32, max_val: i32) -> i64 {
    let mut lcg_val = seed;
    let range = (max_val - min_val + 1) as u32;

    // Kadane's algorithm requires tracking the maximum sum ending at the current position
    // and the global maximum sum found so far across all positions.
    let mut max_sum = i64::MIN;
    let mut current_sum = i64::MIN;

    for _ in 0..n {
        // LCG update: value = (a * value + c) % m
        // u32 wrapping multiplication and addition are equivalent to modulo 2^32.
        lcg_val = lcg_val.wrapping_mul(1664525).wrapping_add(1013904223);
        
        // Random number generation matching the Python logic
        let val = (lcg_val % range) as i32 + min_val;
        let val_i64 = val as i64;

        // Kadane's step: either start a new subarray at the current element
        // or extend the existing subarray sum.
        if current_sum < 0 {
            current_sum = val_i64;
        } else {
            current_sum += val_i64;
        }

        if current_sum > max_sum {
            max_sum = current_sum;
        }
    }
    max_sum
}

fn main() {
    // Parameters exactly as specified in the Python code
    let n: usize = 10000;
    let initial_seed: u32 = 42;
    let min_val: i32 = -10;
    let max_val: i32 = 10;
    let run_count: usize = 20;

    let start_time = Instant::now();

    let mut total_sum: i64 = 0;
    let mut lcg_gen_value: u32 = initial_seed;

    // Perform 20 runs, updating the seed for each run using the outer LCG.
    for _ in 0..run_count {
        lcg_gen_value = lcg_gen_value.wrapping_mul(1664525).wrapping_add(1013904223);
        let current_run_seed = lcg_gen_value;
        total_sum += max_subarray_sum(current_run_seed, n, min_val, max_val);
    }

    let elapsed = start_time.elapsed().as_secs_f64();

    // Identical output strings to the Python version.
    println!("Total Maximum Subarray Sum (20 runs): {}", total_sum);
    println!("Execution Time: {:.6} seconds", elapsed);
}