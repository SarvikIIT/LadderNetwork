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
		parts.push_back(q);
		N = D;
		D = r;
	}
}


