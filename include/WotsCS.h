#pragma once
#include "Wots.h"
#include <gmpxx.h>

template <class D, int T, int N, int S>
class WotsCS : public Wots<D, N> {
public:
  const unsigned int t1() const noexcept final { return T; }

  const unsigned int t2() const noexcept final { return 0; }

  // algorithm 1
  virtual uint_vec constant_sum(int t, int n, int s, mpz_class &I) {
    if (t == 1) {
      return {(unsigned)s};
    }

    int b = 0;
    mpz_class left = 0;
    mpz_class right = 1;
    mpz_class a = 1;

    while (!(I >= left && I < right)) {
      b++;
      a = a * (b + t - 2);
      mpz_divexact_ui(a.get_mpz_t(), a.get_mpz_t(), b);
      left = right;
      right += a;
    }

    if (s - b > n) {
      return {};
    }

    uint_vec encoding = {(unsigned int)s - b};
    I -= left;

    uint_vec next = constant_sum(t - 1, n, b, I);
    encoding.insert(encoding.end(), next.begin(), next.end());

    return encoding;
  }

  // TODO can run indefinitely
  virtual uint_vec gen_fingerprint(ByteArray &data) {
    ByteArray aux = this->digest(data);
    mpz_class i;
    i.set_str(std::to_string(aux), 16);

    uint_vec ret;
    do {
      aux = this->digest(aux);
      i.set_str(std::to_string(aux), 16);
      ret = this->constant_sum(T, N, S, i);
    } while (ret.size() < T);

    return ret;
  }

  const uint_vec gen_checksum(uint_vec &blocks) { return {}; }

protected:
  void gen_public_key() {
    this->gen_private_key();

    ByteArray pub;
    for (long unsigned int i = 0; i < this->private_key.size(); i++) {
      pub += this->digest_chain(this->private_key[i], N);
    }

    this->public_key = this->digest(pub);
  }
};
