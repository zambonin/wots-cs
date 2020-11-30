#pragma once
#include "AbstractDigest.h"
#include <math.h>

using uint_vec = std::vector<unsigned int>;

// prevent SFINAE failure
template <class D, int W, class Enable = void> class Wots;
template <class D, int W>
class Wots<
    D, W,
    typename std::enable_if<std::is_base_of<AbstractDigest, D>::value>::type>
    : protected std::decay<D>::type {

public:
  Wots() { this->block_size = std::ceil(log2(W)); }

  Wots(const ByteArray &seed) : Wots() { this->private_seed = seed; }

  virtual ~Wots() {}

  const unsigned int t() const noexcept {
    return this->t1() + this->t2();
  }

  virtual const unsigned int t1() const noexcept {
    return std::ceil((float)this->bit_length() / (float)this->block_size);
  }

  virtual const unsigned int t2() const noexcept {
    float u = (log2(this->t1() * (W - 1))) / (float)this->block_size;
    return (const unsigned int)std::floor(u) + 1;
  }

  const unsigned int n() const noexcept { return this->len(); }

  virtual uint_vec gen_fingerprint(ByteArray &data) {
    ByteArray fingerprint = this->digest(data);
    return this->base_w(fingerprint);
  }

  virtual const uint_vec gen_checksum(uint_vec &blocks) {
    int sum = 0;
    for (unsigned int &block : blocks) {
      sum += W - 1 - block;
    }

    std::stringstream ss;
    ss << std::hex << sum;
    ByteArray aux = hstoba(ss.str());
    uint_vec ret = this->base_w(aux);
    int rm = ret.size() - this->t2();

    if (rm > 0) {
      ret.erase(ret.begin(), ret.begin() + rm);
    }

    if (rm < 0) {
      uint_vec aux(abs(rm), 0);
      ret.insert(ret.begin(), aux.begin(), aux.end());
    }

    return ret;
  }

  const std::vector<ByteArray> sign(ByteArray &data) {
    uint_vec blocks = this->gen_fingerprint(data);
    uint_vec cs = this->gen_checksum(blocks);
    blocks.insert(blocks.end(), cs.begin(), cs.end());

    std::vector<ByteArray> signature(blocks.size() + cs.size());
    for (long unsigned int i = 0; i < blocks.size(); i++) {
      signature[i] =
          this->digest_chain(this->private_key[i], W - 1 - blocks[i]);
    }

    return signature;
  }

  bool verify(ByteArray &data, std::vector<ByteArray> &signature) {
    uint_vec blocks = this->gen_fingerprint(data);
    uint_vec cs = this->gen_checksum(blocks);
    blocks.insert(blocks.end(), cs.begin(), cs.end());

    ByteArray check;
    for (long unsigned int i = 0; i < blocks.size(); i++) {
      check += this->digest_chain(signature[i], blocks[i]);
    }

    check = this->digest(check);
    return std::to_string(this->public_key).compare(std::to_string(check)) == 0;
  }

protected:
  void gen_private_key() {
    std::stringstream ss;
    for (unsigned int i = 0; i < this->t(); i++) {
      ss.str(std::string());
      ss << std::hex << i;
      ByteArray aux = hstoba(ss.str());
      aux += this->private_seed;
      this->private_key.push_back(this->digest(aux));
    }
  }

  virtual void gen_public_key() {
    this->gen_private_key();

    ByteArray pub;
    for (long unsigned int i = 0; i < this->private_key.size(); i++) {
      pub += this->digest_chain(this->private_key[i], W - 1);
    }

    this->public_key = this->digest(pub);
  }

  // works for W up until 256
  uint_vec base_w(ByteArray &data) {
    unsigned int in = 0;
    unsigned int total = 0;
    unsigned int bits = 0;
    unsigned int out_len = data.size() * 8 / block_size;

    uint_vec ret;
    for (unsigned int consumed = 0; consumed < out_len; consumed++) {
      if (bits == 0) {
        total = std::to_integer<unsigned int>(data[in]);
        in++;
        bits += 8;
      }

      bits -= block_size;
      ret.push_back((total >> bits) & ((1 << (block_size)) - 1));
    }

    return ret;
  }

  ByteArray public_key;
  std::vector<ByteArray> private_key;
  unsigned int block_size;
  ByteArray private_seed = hstoba("01020304FFFF");
};
