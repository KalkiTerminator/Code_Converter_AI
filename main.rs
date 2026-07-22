use std::time::Instant;

// LCG with modulus 2^32 using wrapping arithmetic
#[inline(always)]
fn lcg_next(state: &mut u32) -> u32 {
    // Constants: a = 1664525, c = 1013904223, m = 2^32
    let s = state.wrapping_mul(1664525).wrapping_add(1013904223);
    *state = s;
    s
}

#[inline(always)]
fn max_subarray_sum_kadane(n: usize, seed: u32, min_val: i64, max_val: i64) -> i128 {
    let mut state = seed;

    // Range length as u128 to safely handle very large ranges
    let range_len_u128: u128 = (max_val as i128 - min_val as i128 + 1) as u128;
    let min_i128: i128 = min_val as i128;

    // Generate first value
    let first = (lcg_next(&mut state) as u128 % range_len_u128) as i128 + min_i128;
    let mut max_ending_here: i128 = first;
    let mut max_so_far: i128 = first;

    // Process remaining values
    let mut i = 1usize;
    while i < n {
        let x = (lcg_next(&mut state) as u128 % range_len_u128) as i128 + min_i128;
        let sum = max_ending_here + x;
        // max between starting new subarray at x or extending previous
        if sum > x {
            max_ending_here = sum;
        } else {
            max_ending_here = x;
        }
        if max_ending_here > max_so_far {
            max_so_far = max_ending_here;
        }
        i += 1;
    }
    max_so_far
}

#[inline(always)]
fn total_max_subarray_sum(n: usize, initial_seed: u64, min_val: i64, max_val: i64) -> i128 {
    let mut total: i128 = 0;
    // Seed generator for the 20 runs
    let mut seed_state: u32 = initial_seed as u32; // truncation == mod 2^32
    let mut i = 0;
    while i < 20 {
        let run_seed = lcg_next(&mut seed_state);
        total += max_subarray_sum_kadane(n, run_seed, min_val, max_val);
        i += 1;
    }
    total
}

fn main() {
    // Parameters
    let n: usize = 10000;
    let initial_seed: u64 = 42;
    let min_val: i64 = -10;
    let max_val: i64 = 10;

    // Timing
    let start_time = Instant::now();
    let result = total_max_subarray_sum(n, initial_seed, min_val, max_val);
    let elapsed = start_time.elapsed().as_secs_f64();

    println!("Total Maximum Subarray Sum (20 runs): {}", result);
    println!("Execution Time: {:.6} seconds", elapsed);
}