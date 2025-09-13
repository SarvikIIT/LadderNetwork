#include "NetworkUtils.hpp"
#include <stdexcept>

using std::runtime_error;
using std::string;
using std::vector;

bool isAllowedMonomial(const Polynomial& p) {
	if (p.isZero()) return false;
	int nonzero = 0;
	int idx = -1;
	for (int i = 0; i < (int)p.coeffs.size(); ++i) {
		if (p.coeffs[i] != 0) {
			++nonzero;
			idx = i;
			if (nonzero > 1) break;
		}
	}
	if (nonzero != 1) return false;
	if (idx == 0) return p.coeffs[0] == 1;
	if (idx == 1) return p.coeffs[1] == 1 && (p.coeffs.size() == 2 || p.coeffs[0] == 0);
	return false;
}

string polynomialToToken(const Polynomial& p) {
	if (p.isZero()) return "0";
	if (p.coeffs.size() == 1 && p.coeffs[0] == 1) return "1";
	if (p.coeffs.size() == 2 && p.coeffs[1] == 1 && (p.coeffs[0] == 0)) return "s";
	return "INVALID";
}

void mapAndValidateTokens(
	const vector<Polynomial>& zParts,
	const vector<Polynomial>& yParts,
	vector<string>& Z,
	vector<string>& Y
) {
	Z.clear(); Y.clear();
	Z.reserve(zParts.size());
	Y.reserve(yParts.size());
	
	// Process Z parts
	for (size_t i = 0; i < zParts.size(); ++i) {
		string tok = polynomialToToken(zParts[i]);
		if (tok == "0" && i == zParts.size() - 1) tok = "1/s";
		if (!(tok == "1" || tok == "s" || tok == "1/s")) throw runtime_error("Invalid network");
		Z.push_back(tok);
	}
	
	// Process Y parts
	for (size_t i = 0; i < yParts.size(); ++i) {
		string tok = polynomialToToken(yParts[i]);
		if (tok == "0" && i == yParts.size() - 1) tok = "1/s";
		if (!(tok == "1" || tok == "s" || tok == "1/s")) throw runtime_error("Invalid network");
		Y.push_back(tok);
	}
}


