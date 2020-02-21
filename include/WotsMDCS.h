#pragma once
#include "WotsDCS.h"
#include <array>

template <class D, int T, int N, int S>
class WotsMDCS : public virtual WotsDCS<D, T, N, S> {
public:
  WotsMDCS() noexcept { this->memoize(); }

  WotsMDCS(const ByteArray &seed) noexcept : WotsDCS<D, T, N, S>(seed) {
    this->memoize();
  }

  virtual mpz_class tau(int t, int n, int s) { return this->cache[t - 1][s]; }

protected:
  void memoize() {
    for (unsigned int t = 1; t < T; t++) {
      for (unsigned int s = 0; s <= S; s++) {
        this->cache[t - 1][s] = WotsDCS<D, T, N, S>::tau(t, N, s);
      }
    }
  }

  std::array<std::array<mpz_class, S + 1>, T - 1> cache;
};
