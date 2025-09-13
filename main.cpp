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
	vector<long long> a(n + 1);
	cout << "Enter " << (n + 1) << " numerator coefficients a0..a" << n << " (ascending powers): " << endl;
	for (int i = 0; i <= n; ++i) cin >> a[i];
	cout << "Enter denominator degree: " << endl;
	if (!(cin >> m)) return 0;
	vector<long long> b(m + 1);
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

		// Special-case fallback: if only constant first quotient and nonzero remainder exists,
		// reinterpret as Z = s and Y = first remainder
		Polynomial q1, r1;
		N.divmod(D, q1, r1);
		if (parts.size() == 1 && r1.isZero() == false) {
			zParts.clear();
			yParts.clear();
			zParts.push_back(Polynomial(vector<long long>{0, 1})); // s
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
