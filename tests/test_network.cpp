#include <gtest/gtest.h>
#include <vector>
#include <string>
#include "Polynomial.hpp"
#include "ContinuedFraction.hpp"
#include "NetworkUtils.hpp"

using std::string;
using std::vector;

static void cfToZY(const Polynomial& N, const Polynomial& D,
                   vector<string>& Z, vector<string>& Y) {
    ContinuedFraction CF(N, D);
    const auto& parts = CF.get();
    vector<Polynomial> zParts, yParts;
    for (size_t i = 0; i < parts.size(); ++i) {
        if ((i % 2) == 0) zParts.push_back(parts[i]); else yParts.push_back(parts[i]);
    }
    // Special-case fallback mirroring main.cpp
    Polynomial q1, r1;
    N.divmod(D, q1, r1);
    if (parts.size() == 1 && !r1.isZero()) {
        zParts.clear(); yParts.clear();
        zParts.push_back(Polynomial(vector<double>{0.0, 1.0})); // s
        yParts.push_back(r1);
    }
    mapAndValidateTokens(zParts, yParts, Z, Y);
}

TEST(NetworkCF, DivisionByZeroDenominatorThrows) {
    Polynomial N(vector<double>{1.0});
    Polynomial D; // zero
    EXPECT_THROW({ ContinuedFraction CF(N, D); }, std::exception);
}

TEST(NetworkCF, Monomial_Z_is_s_only) {
    // N(s) = s, D(s) = 1 → Z=[s], Y=[]
    Polynomial N(vector<double>{0.0, 1.0});
    Polynomial D(vector<double>{1.0});
    vector<string> Z, Y;
    cfToZY(N, D, Z, Y);
    ASSERT_EQ(Z.size(), 1u);
    EXPECT_EQ(Z[0], "s");
    EXPECT_TRUE(Y.empty());
}

TEST(NetworkCF, SP1_over_S_maps_Zs_Y1) {
    // (s+1)/s → Z=[s], Y=[1]
    Polynomial N(vector<double>{1.0, 1.0});
    Polynomial D(vector<double>{0.0, 1.0});
    vector<string> Z, Y;
    cfToZY(N, D, Z, Y);
    ASSERT_EQ(Z.size(), 1u);
    EXPECT_EQ(Z[0], "s");
    ASSERT_EQ(Y.size(), 1u);
    EXPECT_EQ(Y[0], "1");
}

TEST(NetworkCF, QuadraticOverQuadratic_Zs_YLinear) {
    // (s^2+4s+3)/(s^2+2s) → Z=[s], Y=[2s+3]
    Polynomial N(vector<double>{3.0, 4.0, 1.0});
    Polynomial D(vector<double>{0.0, 2.0, 1.0});
    vector<string> Z, Y;
    cfToZY(N, D, Z, Y);
    ASSERT_EQ(Z.size(), 1u);
    EXPECT_EQ(Z[0], "s");
    ASSERT_EQ(Y.size(), 1u);
    EXPECT_EQ(Y[0], "2s+3");
}

TEST(NetworkCF, TerminalsNotShorted_nonEmptyZorY) {
    // Ensure we do not get both Z and Y empty (which would imply a short between terminals)
    Polynomial N(vector<double>{1.0, 0.0, 3.0, 0.0, 1.0}); // s^4+3s^2+1
    Polynomial D(vector<double>{0.0, 2.0, 0.0, 1.0});    // s^3+2s
    vector<string> Z, Y;
    cfToZY(N, D, Z, Y);
    // At least one element must exist
    EXPECT_TRUE(!Z.empty() || !Y.empty());
}


