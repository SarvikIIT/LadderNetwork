#pragma once

#include <vector>
#include <string>
#include <utility>

class Polynomial {
	public:
		std::vector<long long> coeffs;

		Polynomial();
		explicit Polynomial(const std::vector<long long>& c);

		void normalize();
		bool isZero() const;
		int degree() const;

		static Polynomial monomial(long long coeff, int degree);

		Polynomial operator+(const Polynomial& second) const;
		Polynomial operator-(const Polynomial& second) const;
		Polynomial operator*(const Polynomial& second) const;
		std::pair<Polynomial, Polynomial> operator/(const Polynomial& divisor) const;

		// Explicit divmod to avoid operator overloading ambiguity
		void divmod(const Polynomial& divisor, Polynomial& quotient, Polynomial& remainder) const;

		std::string toString() const;
};


