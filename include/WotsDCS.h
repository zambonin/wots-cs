#pragma once
#include "WotsCS.h"

template <class D, int T, int N, int S>
class WotsDCS : public WotsCS<D, T, N, S> {
public:
  // must be signed to consider negative cases
  mpz_class binomial(int n, int k) {
    if (n < k || n < 0 || k < 0) {
      return 0;
    }

    mpz_class ret = 0;
    mpz_bin_uiui(ret.get_mpz_t(), n, k);
    return ret;
  }

  // theorem 1
  virtual mpz_class tau(int t, int n, int s) {
    int k = std::min(t, (int)std::floor(float(s) / float(n + 1)));

    mpz_class result = 0;
    for (int i = 0; i <= k; i++) {
      result += this->binomial(t, i) *
                this->binomial(s - (n + 1) * i + t - 1, t - 1) *
                ((i % 2 == 0) ? 1 : -1);
    }

    return result;
  }

  // algorithm 2
  // asserting that i <= tau(t, n, s) would ruin benchmark results
  virtual uint_vec constant_sum(int t, int n, int s, mpz_class &I) {
    if (t == 1) {
      return {(unsigned int)s};
    }

    unsigned int b = 0;
    mpz_class left = 0;
    mpz_class right = tau(t - 1, n, s);

    while (!(I >= left && I < right)) {
      b++;
      left = right;
      right += tau(t - 1, n, s - b);
    }

    uint_vec encoding = {b};
    I -= left;
    uint_vec next = constant_sum(t - 1, n, s - b, I);
    encoding.insert(encoding.end(), next.begin(), next.end());

    return encoding;
  }

  uint_vec gen_fingerprint(ByteArray &data) {
    ByteArray aux = this->digest(data);
    mpz_class i;
    i.set_str(std::to_string(aux), 16);
    return this->constant_sum(T, N, S, i);
  }

protected:
  // algorithm 4 (not covered in the benchmarks due to its simplicity)
  bool fast_verify(ByteArray &data, std::vector<ByteArray> &signature,
                           uint_vec &encoding) {
    ByteArray check;
    for (long unsigned int i = 0; i < encoding.size(); i++) {
      check += this->digest_chain(signature[i], encoding[i]);
    }

    check = this->digest(check);
    return std::to_string(this->public_key).compare(std::to_string(check)) == 0;
  }
};
