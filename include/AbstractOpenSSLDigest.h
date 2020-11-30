#pragma once
#include "AbstractDigest.h"
#include <openssl/evp.h>

class AbstractOpenSSLDigest : public AbstractDigest {
public:
  ByteArray digest(ByteArray &data) const noexcept {
    return evp_chain(data, 1);
  }

  ByteArray digest_chain(ByteArray &data, const unsigned int n) const noexcept {
    return evp_chain(data, n);
  }

protected:
  virtual const EVP_MD *algorithm() const noexcept = 0;

  ByteArray evp_chain(ByteArray &data, const unsigned int n) const noexcept {
    if (n <= 0) {
      return data;
    }

    const EVP_MD *md = this->algorithm();
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    ByteArray ret(this->len());

    unsigned char *in_data = reinterpret_cast<unsigned char *>(data.data());
    unsigned char *out_data = reinterpret_cast<unsigned char *>(ret.data());

    EVP_DigestInit_ex(ctx, md, NULL);
    EVP_DigestUpdate(ctx, in_data, data.size());
    EVP_DigestFinal_ex(ctx, out_data, NULL);

    for (unsigned int i = 1; i < n; i++) {
      EVP_DigestInit_ex(ctx, md, NULL);
      EVP_MD_CTX_reset(ctx);
      EVP_DigestInit_ex(ctx, md, NULL);
      EVP_DigestUpdate(ctx, out_data, ret.size());
      EVP_DigestFinal_ex(ctx, out_data, NULL);
    }

    EVP_MD_CTX_free(ctx);

    return ret;
  }
};
