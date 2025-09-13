#include "CSVMaker.hpp"
#include <fstream>
#include <iostream>

using namespace std;

void writeArrayCSV(const vector<string>& arr, const string& filename) {
    ofstream fout(filename);
    if (!fout.is_open()) {
        cerr << "Cannot open file: " << filename << endl;
        return;
    }

    for (size_t i = 0; i < arr.size(); i++) {
        fout << arr[i];
        if (i + 1 < arr.size()) fout << ",";
    }
    fout << "\n";
    fout.close();

    cout << "CSV files written successfully!" << endl;
}

