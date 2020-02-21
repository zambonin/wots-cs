#pragma once
#include "AbstractOpenSSLDigest.h"

class OpenSSLSha256 : public AbstractOpenSSLDigest {
public:
  const unsigned int bit_length() const noexcept { return 256; }
  const unsigned int len() const noexcept { return 32; }

protected:
  const EVP_MD *algorithm() const noexcept { return EVP_sha256(); }
};
