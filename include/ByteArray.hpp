#pragma once
#include "bytearray/include/bytearray.hpp"

// requires that parent class does not inherit privately from std::vector
template <typename Allocator = std::allocator<std::byte>>
class bytearray_ext : public bytearray<Allocator> {
public:
  using bytearray<Allocator>::bytearray;
  using std::vector<std::byte, Allocator>::data;
  using std::vector<std::byte, Allocator>::insert;

  bytearray_ext &operator+=(const bytearray_ext &rhs) noexcept {
    insert(this->end(), rhs.begin(), rhs.end());
    return (*this);
  }
};

typedef bytearray_ext<> ByteArray;

template <typename ValueType, typename Allocator>
std::string
to_string(const bytearray_processor<ValueType, Allocator> &processor) {
  std::stringstream ss;

  for (auto &&b : processor.container()) {
    ss << std::uppercase << std::setfill('0') << std::setw(2) << std::hex
       << int(b);
  }

  return ss.str();
}

static inline ByteArray hstoba(const std::string str) {
  ByteArray array{};
  array.load_from_hex(std::string_view{str});
  return array;
}
