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
	if (!(cin >> n)) return 0;
	vector<long long> a(n + 1);
	for (int i = 0; i <= n; ++i) cin >> a[i];
	if (!(cin >> m)) return 0;
	vector<long long> b(m + 1);
	for (int i = 0; i <= m; ++i) cin >> b[i];

	Polynomial N(a), D(b);
	try {
		cerr << "Input N(s)=" << N.toString() << ", D(s)=" << D.toString() << "\n";
		ContinuedFraction CF(N, D);
		const vector<Polynomial>& parts = CF.get();
		vector<Polynomial> zParts, yParts;
		for (size_t i = 0; i < parts.size(); ++i) {
			if ((i % 2) == 0) zParts.push_back(parts[i]);
			else yParts.push_back(parts[i]);
		}

		// Debug prints to inspect parts for validation issue
		cerr << "CF parts:" << "\n";
		for (size_t i = 0; i < parts.size(); ++i) cerr << i << ": " << parts[i].toString() << "\n";
		cerr << "Z parts:" << " ";
		for (auto &p : zParts) cerr << p.toString() << " ";
		cerr << "\nY parts:" << " ";
		for (auto &p : yParts) cerr << p.toString() << " ";
		cerr << "\n";

		// Map and validate using NetworkUtils
		vector<string> Z, Y;
		try {
			mapAndValidateTokens(zParts, yParts, Z, Y);
		} catch (const std::exception&) {
			cerr << "Invalid network" << "\n";
			return 1;
		}

		// Write CSVs for network.py
		writeArrayCSV(Z, "Z.csv");
		writeArrayCSV(Y, "Y.csv");

		// Echo to console
		cout << "Z = [";
		for (size_t i = 0; i < Z.size(); ++i) { cout << Z[i]; if (i + 1 < Z.size()) cout << ", "; }
		cout << "]\n";
		cout << "Y = [";
		for (size_t i = 0; i < Y.size(); ++i) { cout << Y[i]; if (i + 1 < Y.size()) cout << ", "; }
		cout << "]\n";

		// Invoke network.py to generate the image
		int rc = system("python \"network.py\"");
		if (rc != 0) { cerr << "Python network generation failed (code " << rc << ")\n"; }
	} catch (const exception& e) {
		cerr << "Error: " << e.what() << "\n";
		return 1;
	}
	return 0;
}
