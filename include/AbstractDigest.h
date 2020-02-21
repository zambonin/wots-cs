#pragma once
#include "ByteArray.hpp"

class AbstractDigest {
public:
  virtual ByteArray digest(ByteArray &data) const noexcept = 0;
  virtual ByteArray digest_chain(ByteArray &data,
                                 const unsigned int n) const noexcept = 0;
  virtual const unsigned int bit_length() const noexcept = 0;
  virtual const unsigned int len() const noexcept = 0;
};
