#pragma once
#include "WotsDBCS.h"
#include <array>

template <class D, int T, int N, int S>
class WotsMDBCS : public virtual WotsDBCS<D, T, N, S> {
public:
  WotsMDBCS() noexcept { this->memoize(); }

  WotsMDBCS(const ByteArray &seed) noexcept : WotsDBCS<D, T, N, S>(seed) {
    this->memoize();
  }

  virtual mpz_class rank(int t, int n, int s, int j) {
    return this->cache[t - 1][s][j];
  }

protected:
  void memoize() {
    for (unsigned int t = 0; t < T; t++) {
      for (unsigned int s = 0; s <= S; s++) {
#pragma omp parallel for
        for (unsigned int j = 0; j <= N; j++) {
          if (j <= s) {
            this->cache[t][s][j] = WotsDBCS<D, T, N, S>::rank(t + 1, N, s, j);
          }
        }
      }
    }
  }

  std::array<std::array<std::array<mpz_class, N + 1>, S + 1>, T> cache;
};
