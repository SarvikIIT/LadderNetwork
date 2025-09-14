#include "ContinuedFraction.hpp"

using std::pair;
using std::vector;

ContinuedFraction::ContinuedFraction(const Polynomial& num, const Polynomial& den) {
	compute(num, den);
}

void ContinuedFraction::compute(const Polynomial& num, const Polynomial& den) {
	parts.clear();
	Polynomial N = num;
	Polynomial D = den;
	while (!D.isZero()) {
		Polynomial q, r;
		N.divmod(D, q, r);
		// If division made no progress (q is 0), stop without pushing q.
		if (q.isZero()) break;
		// Keep quotient leading coefficient positive by flipping signs consistently
		if (!q.isZero() && !q.coeffs.empty() && q.coeffs.back() < 0) {
			for (auto &c : q.coeffs) c = -c;
			for (auto &c : D.coeffs) c = -c;
			for (auto &c : r.coeffs) c = -c;
		}
		// Ensure next divisor (remainder) has positive leading coefficient
		if (!r.isZero() && !r.coeffs.empty() && r.coeffs.back() < 0) {
			for (auto &c : r.coeffs) c = -c;
			for (auto &c : D.coeffs) c = -c;
		}
		parts.push_back(q);
		N = D;
		D = r;
	}
}


