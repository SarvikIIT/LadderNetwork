#include "Polynomial.hpp"
#include <algorithm>
#include <stdexcept>

using std::max;
using std::invalid_argument;
using std::pair;
using std::string;
using std::vector;

Polynomial::Polynomial() {}

Polynomial::Polynomial(const vector<long long>& c) : coeffs(c) { normalize(); }

void Polynomial::normalize() {
	while (!coeffs.empty() && coeffs.back() == 0) coeffs.pop_back();
}

bool Polynomial::isZero() const { return coeffs.empty(); }

int Polynomial::degree() const { return (int)coeffs.size() - 1; }

Polynomial Polynomial::monomial(long long coeff, int degree) {
	if (coeff == 0) return Polynomial();
	vector<long long> c(degree + 1, 0);
	c[degree] = coeff;
	return Polynomial(c);
}

Polynomial Polynomial::operator+(const Polynomial& second) const {
	Polynomial result;
	int maxDegree = max(degree(), second.degree());
	result.coeffs.assign(maxDegree + 1, 0);
	for (int i = 0; i <= maxDegree; ++i) {
		long long a = i < (int)coeffs.size() ? coeffs[i] : 0;
		long long b = i < (int)second.coeffs.size() ? second.coeffs[i] : 0;
		result.coeffs[i] = a + b;
	}
	result.normalize();
	return result;
}

Polynomial Polynomial::operator-(const Polynomial& second) const {
	Polynomial result;
	int maxDegree = max(degree(), second.degree());
	result.coeffs.assign(maxDegree + 1, 0);
	for (int i = 0; i <= maxDegree; ++i) {
		long long a = i < (int)coeffs.size() ? coeffs[i] : 0;
		long long b = i < (int)second.coeffs.size() ? second.coeffs[i] : 0;
		result.coeffs[i] = a - b;
	}
	result.normalize();
	return result;
}

Polynomial Polynomial::operator*(const Polynomial& second) const {
	if (isZero() || second.isZero()) return Polynomial();
	Polynomial result;
	result.coeffs.assign(degree() + second.degree() + 2, 0);
	for (int i = 0; i < (int)coeffs.size(); ++i) {
		for (int j = 0; j < (int)second.coeffs.size(); ++j) {
			result.coeffs[i + j] += coeffs[i] * second.coeffs[j];
		}
	}
	result.normalize();
	return result;
}

pair<Polynomial, Polynomial> Polynomial::operator/(const Polynomial& divisor) const {
	if (divisor.isZero()) {
		throw invalid_argument("Division by zero polynomial");
	}
	if (degree() < divisor.degree()) {
		return { Polynomial(), *this };
	}
	Polynomial dividend = *this;
	Polynomial quotient;
	int d = divisor.degree();
	quotient.coeffs.assign(degree() - d + 1, 0);
	while (!dividend.isZero() && dividend.degree() >= d) {
		int degDiff = dividend.degree() - d;
		long long coeffQuotient = dividend.coeffs.back() / divisor.coeffs.back();
		Polynomial term = Polynomial::monomial(coeffQuotient, degDiff);
		quotient.coeffs[degDiff] += coeffQuotient;
		dividend = dividend - (divisor * term);
	}
	quotient.normalize();
	dividend.normalize();
	return { quotient, dividend };
}

void Polynomial::divmod(const Polynomial& divisor, Polynomial& quotient, Polynomial& remainder) const {
	if (divisor.isZero()) {
		throw invalid_argument("Division by zero polynomial");
	}
	if (degree() < divisor.degree()) {
		quotient = Polynomial();
		remainder = *this;
		return;
	}
	Polynomial dividend = *this;
	Polynomial q;
	int d = divisor.degree();
	q.coeffs.assign(degree() - d + 1, 0);
	while (!dividend.isZero() && dividend.degree() >= d) {
		int degDiff = dividend.degree() - d;
		long long coeffQuotient = dividend.coeffs.back() / divisor.coeffs.back();
		Polynomial term = Polynomial::monomial(coeffQuotient, degDiff);
		q.coeffs[degDiff] += coeffQuotient;
		dividend = dividend - (divisor * term);
	}
	q.normalize();
	dividend.normalize();
	quotient = q;
	remainder = dividend;
}

string Polynomial::toString() const {
	if (coeffs.empty()) return "0";
	string s;
	for (int i = degree(); i >= 0; --i) {
		long long c = coeffs[i];
		if (c == 0) continue;
		if (!s.empty()) s += (c > 0 ? "+" : "-");
		long long absC = c < 0 ? -c : c;
		if (i == 0) {
			s += std::to_string(absC);
		} else if (i == 1) {
			if (absC != 1) s += std::to_string(absC);
			s += "s";
		} else {
			if (absC != 1) s += std::to_string(absC);
			s += "s^" + std::to_string(i);
		}
	}
	return s;
}


