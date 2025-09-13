#pragma once

#include <vector>
#include "Polynomial.hpp"

class ContinuedFraction {
	private:
		std::vector<Polynomial> parts;

	public:
		ContinuedFraction() = default;
		ContinuedFraction(const Polynomial& num, const Polynomial& den);

		void compute(const Polynomial& num, const Polynomial& den);
		const std::vector<Polynomial>& get() const { return parts; }
};


