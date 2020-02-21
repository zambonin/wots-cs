#pragma once
#include "WotsDCS.h"

template <class D, int T, int N, int S>
class WotsDBCS : public virtual WotsDCS<D, T, N, S> {
public:
  // proposition 3
  virtual mpz_class rank(int t, int n, int s, int l) {
    int k = std::min(t, (int)std::floor(float(s) / float(n + 1)));

    mpz_class result = 0;
    for (int i = 0; i <= k; i++) {
      result += std::pow(-1, i) * this->binomial(t - 1, i) *
                (this->binomial(s - (n + 1) * i + t - 1, t - 1) -
                 this->binomial(s - (n + 1) * i + t - 2 - l, t - 1));
    }

    return result;
  }

  // algorithm 3 (example implementation from std::upper_bound)
  virtual uint_vec constant_sum(int t, int n, int s, mpz_class &I) {
    uint_vec p;

    for (int i = 0; i < t; i++) {
      int c = std::min(n, s);
      int b = 0;

      while (c > 0) {
        int step = std::floor(c / 2);
        int j = b + step;

        if (I >= this->rank(t - i, n, s, j)) {
          b = ++j;
          c -= step + 1;
        } else {
          c = step;
        }
      }

      p.push_back((unsigned int)b);
      if (b > 0) {
        I -= this->rank(t - i, n, s, b - 1);
        s -= b;
      }
    }

    return p;
  }
};
