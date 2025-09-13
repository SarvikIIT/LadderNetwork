#pragma once

#include <string>
#include <vector>
#include "Polynomial.hpp"

// Returns true if p is exactly 1 or s
bool isAllowedMonomial(const Polynomial& p);

// Returns "1", "s", "0" (interpretable as trailing 1/s), or "INVALID"
std::string polynomialToToken(const Polynomial& p);

// Map and validate Z and Y parts into tokens; allow trailing 1/s
// Throws std::runtime_error on invalid network
void mapAndValidateTokens(
	const std::vector<Polynomial>& zParts,
	const std::vector<Polynomial>& yParts,
	std::vector<std::string>& Z,
	std::vector<std::string>& Y
);


