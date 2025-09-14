#include <iostream>
#include <vector>
#include <string>
#include <cstdlib>
#include "Polynomial.hpp"
#include "ContinuedFraction.hpp"
#include "CSVMaker.hpp"
#include "NetworkUtils.hpp"

using namespace std;

int main() {
	ios::sync_with_stdio(false);
	cin.tie(nullptr);

	int n, m;
	cout << "Enter numerator degree: " << endl;
	if (!(cin >> n)) return 0;
	vector<double> a(n + 1);
	cout << "Enter " << (n + 1) << " numerator coefficients a0..a" << n << " (ascending powers): " << endl;
	for (int i = 0; i <= n; ++i) cin >> a[i];
	cout << "Enter denominator degree: " << endl;
	if (!(cin >> m)) return 0;
	vector<double> b(m + 1);
	cout << "Enter " << (m + 1) << " denominator coefficients b0..b" << m << " (ascending powers): " << endl;
	for (int i = 0; i <= m; ++i) cin >> b[i];

	Polynomial N(a), D(b);
	try {
		ContinuedFraction CF(N, D);
		const vector<Polynomial>& parts = CF.get();
		vector<Polynomial> zParts, yParts;
		for (size_t i = 0; i < parts.size(); ++i) {
			if ((i % 2) == 0) zParts.push_back(parts[i]);
			else yParts.push_back(parts[i]);
		}

		// Validate physical non-negativity of coefficients in all quotient parts
		auto isPhysicallyNonnegative = [](const vector<Polynomial>& zs, const vector<Polynomial>& ys){
			auto okPoly = [](const Polynomial& p){
				if (p.isZero()) return true;
				int deg = p.degree();
				if (deg > 1) return false;
				if (deg == 1) {
					double a = p.coeffs.size() > 1 ? p.coeffs[1] : 0.0;
					double b = p.coeffs.size() > 0 ? p.coeffs[0] : 0.0;
					return (a >= -1e-12) && (b >= -1e-12);
				}
				double b = p.coeffs.size() > 0 ? p.coeffs[0] : 0.0;
				return (b >= -1e-12);
			};
			for (const auto& p : zs) { if (!okPoly(p)) return false; }
			for (const auto& p : ys) { if (!okPoly(p)) return false; }
			return true;
		};

		bool cauerIValid = isPhysicallyNonnegative(zParts, yParts);
		if (!cauerIValid) {
			// Try Cauer-II (admittance-first): expand D/N
			ContinuedFraction CF2(D, N);
			const vector<Polynomial>& parts2 = CF2.get();
			vector<Polynomial> z2, y2;
			for (size_t i = 0; i < parts2.size(); ++i) {
				if ((i % 2) == 0) y2.push_back(parts2[i]); // even -> Y
				else z2.push_back(parts2[i]);              // odd  -> Z
			}
			if (isPhysicallyNonnegative(z2, y2)) {
				zParts.swap(z2);
				yParts.swap(y2);
			}
		}

		// Special-case normalization (Cauer-I around infinity):
		// If the initial Euclidean division yields a constant quotient and nonzero remainder,
		// reinterpret the first section as a series inductor 's' with shunt admittance equal to that remainder.
		Polynomial q1, r1;
		N.divmod(D, q1, r1);
		if (!r1.isZero() && q1.degree() == 0) {
			zParts.clear();
			yParts.clear();
			zParts.push_back(Polynomial(vector<double>{0.0, 1.0})); // s
			yParts.push_back(r1);
		}

		// Map and validate using NetworkUtils
		vector<string> Z, Y;
		try {
			mapAndValidateTokens(zParts, yParts, Z, Y);
		} catch (const std::exception&) {
			cerr << "Invalid network" << "\n";
			return 1;
		}

		// Write CSVs for network.py (compact tokens, e.g., "2s+3")
		writeArrayCSV(Z, "Z.csv");
		writeArrayCSV(Y, "Y.csv");

		// Echo to console
		cout << "Z = [";
		for (size_t i = 0; i < Z.size(); ++i) { cout << Z[i]; if (i + 1 < Z.size()) cout << ", "; }
		cout << "]\n";
		cout << "Y = [";
		for (size_t i = 0; i < Y.size(); ++i) { cout << Y[i]; if (i + 1 < Y.size()) cout << ", "; }
		cout << "]\n";

		// Invoke network.py to generate the image (may fail if python deps missing)
		int rc = system("python \"network.py\"");
		if (rc != 0) { cerr << "Python network generation failed (code " << rc << ")\n"; }
	} catch (const exception& e) {
		cerr << "Error: " << e.what() << "\n";
		return 1;
	}
	return 0;
}
