#pragma once

#include <string>
#include <vector>
#include "Polynomial.hpp"

// Returns the printable polynomial token (e.g., "2s+3") or "0" (for trailing 1/s)
std::string polynomialToToken(const Polynomial& p);

// Map Z and Y parts into tokens; allow trailing 1/s represented by final "0"
void mapAndValidateTokens(
	const std::vector<Polynomial>& zParts,
	const std::vector<Polynomial>& yParts,
	std::vector<std::string>& Z,
	std::vector<std::string>& Y
);

// Expand a compact token like "2s+3", "2s", or "3" into a sequence of
// base tokens {"s","1"} repeated. Returns false if unrecognized (e.g. s^2).
bool expandToBaseTokens(const std::string& token, std::vector<std::string>& out);


