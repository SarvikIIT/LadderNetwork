#include "Polynomial.hpp"
#include <algorithm>
#include <stdexcept>
#include <cmath>

using std::max;
using std::invalid_argument;
using std::pair;
using std::string;
using std::vector;

Polynomial::Polynomial() {}

Polynomial::Polynomial(const vector<double>& c) : coeffs(c) { normalize(); }

void Polynomial::normalize() {
	while (!coeffs.empty() && std::fabs(coeffs.back()) < 1e-12) coeffs.pop_back();
}

bool Polynomial::isZero() const { return coeffs.empty(); }

int Polynomial::degree() const { return (int)coeffs.size() - 1; }

Polynomial Polynomial::monomial(double coeff, int degree) {
	if (std::fabs(coeff) < 1e-12) return Polynomial();
	vector<double> c(degree + 1, 0.0);
	c[degree] = coeff;
	return Polynomial(c);
}

Polynomial Polynomial::operator+(const Polynomial& second) const {
	Polynomial result;
	int maxDegree = max(degree(), second.degree());
	result.coeffs.assign(maxDegree + 1, 0.0);
	for (int i = 0; i <= maxDegree; ++i) {
		double a = i < (int)coeffs.size() ? coeffs[i] : 0.0;
		double b = i < (int)second.coeffs.size() ? second.coeffs[i] : 0.0;
		result.coeffs[i] = a + b;
	}
	result.normalize();
	return result;
}

Polynomial Polynomial::operator-(const Polynomial& second) const {
	Polynomial result;
	int maxDegree = max(degree(), second.degree());
	result.coeffs.assign(maxDegree + 1, 0.0);
	for (int i = 0; i <= maxDegree; ++i) {
		double a = i < (int)coeffs.size() ? coeffs[i] : 0.0;
		double b = i < (int)second.coeffs.size() ? second.coeffs[i] : 0.0;
		result.coeffs[i] = a - b;
	}
	result.normalize();
	return result;
}

Polynomial Polynomial::operator*(const Polynomial& second) const {
	if (isZero() || second.isZero()) return Polynomial();
	Polynomial result;
	result.coeffs.assign(degree() + second.degree() + 2, 0.0);
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
	quotient.coeffs.assign(degree() - d + 1, 0.0);
	while (!dividend.isZero() && dividend.degree() >= d) {
		int degDiff = dividend.degree() - d;
		double coeffQuotient = dividend.coeffs.back() / divisor.coeffs.back();
		if (std::fabs(coeffQuotient) < 1e-18) break; // avoid infinite loop
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
	q.coeffs.assign(degree() - d + 1, 0.0);
	while (!dividend.isZero() && dividend.degree() >= d) {
		int degDiff = dividend.degree() - d;
		double coeffQuotient = dividend.coeffs.back() / divisor.coeffs.back();
		if (std::fabs(coeffQuotient) < 1e-18) break; // avoid infinite loop
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
	auto dec = [](double x){
		char buf[64];
		if (std::fabs(x - std::round(x)) < 1e-12) {
			std::snprintf(buf, sizeof(buf), "%g", std::round(x));
		} else {
			std::snprintf(buf, sizeof(buf), "%g", x);
		}
		return std::string(buf);
	};
	string s;
	for (int i = degree(); i >= 0; --i) {
		double c = coeffs[i];
		if (std::fabs(c) < 1e-12) continue;
		if (!s.empty()) s += (c > 0 ? "+" : "-");
		double absC = c < 0 ? -c : c;
		if (i == 0) {
			s += dec(absC);
		} else if (i == 1) {
			if (std::fabs(absC - 1.0) > 1e-12) s += dec(absC);
			s += "s";
		} else {
			if (std::fabs(absC - 1.0) > 1e-12) s += dec(absC);
			s += "s^" + std::to_string(i);
		}
	}
	return s;
}


