#pragma once
#include "../c/nabla_fraction.h"
#include <optional>
#include <string>

namespace nabla {
inline std::optional<nm_fraction> parse_fraction(const std::string &text) {
    nm_fraction value{};
    if (nm_parse_fraction(text.c_str(), &value) != 0) return std::nullopt;
    return value;
}
}
