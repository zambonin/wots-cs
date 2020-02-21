#pragma once
#include "AbstractOpenSSLDigest.h"

class OpenSSLSha512 : public AbstractOpenSSLDigest {
public:
  const unsigned int bit_length() const noexcept { return 512; }
  const unsigned int len() const noexcept { return 64; }

protected:
  const EVP_MD *algorithm() const noexcept { return EVP_sha512(); }
};
