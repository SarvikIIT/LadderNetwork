#include "NetworkUtils.hpp"
#include <stdexcept>

using std::runtime_error;
using std::string;
using std::vector;

// Forward declaration for use in mapAndValidateTokens
static bool parseAsPlusB(const string& token, int& a, int& b);

string polynomialToToken(const Polynomial& p) {
	if (p.isZero()) return "0"; // will be mapped to 1/s if trailing
	return p.toString(); // print general polynomial like "2s+3", "s", "1", etc.
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
	
	// Process Z parts (accept general polynomial tokens)
	for (size_t i = 0; i < zParts.size(); ++i) {
		string tok = polynomialToToken(zParts[i]);
		if (tok == "0" && i == zParts.size() - 1) tok = "1/s";
		Z.push_back(tok);
	}
	
	// Process Y parts
	for (size_t i = 0; i < yParts.size(); ++i) {
		string tok = polynomialToToken(yParts[i]);
		if (tok == "0" && i == yParts.size() - 1) tok = "1/s";
		Y.push_back(tok);
	}

	// Normalize first CF stage: if Z[0] == "s" and Y[0] is linear a*s + b,
	// rewrite to Z = ["1", "s/a", ...], Y = ["s/a", ...]
	if (!Z.empty() && !Y.empty()) {
		if (Z[0] == "s") {
			int a = -1, b = -1;
			if (parseAsPlusB(Y[0], a, b) && a > 0) {
				Z[0] = "1";
				Z.insert(Z.begin() + 1, string("s/") + std::to_string(a));
				Y[0] = string("s/") + std::to_string(a);
			}
		}
	}
}

static bool parseAsPlusB(const string& token, int& a, int& b) {
	string t;
	for (char c : token) if (c != ' ') t.push_back(c);
	// Patterns: a*s+b, as+b, s+b, b+a*s, b+as, b+s
	// Try s-first
	{
		int plus = (int)t.find('+');
		string left = plus == string::npos ? t : t.substr(0, plus);
		string right = plus == string::npos ? string() : t.substr(plus + 1);
		if (!left.empty()) {
			if (left == "s") { a = 1; }
			else {
				string ls = left; size_t pos = ls.find("s");
				if (pos != string::npos) {
					string coef = ls.substr(0, pos);
					if (coef == "") a = 1; else a = stoi(coef);
				} else a = -1;
			}
			if (a != -1) { b = right.empty() ? 0 : stoi(right); return true; }
		}
	}
	// Try b-first
	{
		int plus = (int)t.find('+');
		if (plus != (int)string::npos) {
			string left = t.substr(0, plus);
			string right = t.substr(plus + 1);
			try { b = stoi(left); } catch (...) { b = -1; }
			if (b != -1) {
				if (right == "s") { a = 1; return true; }
				size_t pos = right.find("s");
				if (pos != string::npos) {
					string coef = right.substr(0, pos);
					if (coef == "") a = 1; else a = stoi(coef);
					return true;
				}
			}
		}
	}
	return false;
}

bool expandToBaseTokens(const string& token, vector<string>& out) {
	out.clear();
	string t;
	for (char c : token) if (c != ' ') t.push_back(c);
	if (t == "s") { out.push_back("s"); return true; }
	if (t == "1") { out.push_back("1"); return true; }
	if (t == "1/s") { out.push_back("1/s"); return true; }
	// a*s + b
	int a = -1, b = -1;
	if (parseAsPlusB(t, a, b)) {
		for (int i = 0; i < a; ++i) out.push_back("s");
		for (int i = 0; i < b; ++i) out.push_back("1");
		return true;
	}
	return false;
}


