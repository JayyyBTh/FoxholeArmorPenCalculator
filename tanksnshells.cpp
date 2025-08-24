#include "tanksnshells.h"

#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <iostream>
#include <algorithm>
#include <cctype>

// --- helpers ---------------------------------------------------------------

static inline void trim_inplace(std::string& s) {
    auto not_space = [](unsigned char ch){ return !std::isspace(ch); };
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), not_space));
    s.erase(std::find_if(s.rbegin(), s.rend(), not_space).base(), s.end());
}

static std::vector<std::string> split_csv_simple(const std::string& line) {
    // Simple CSV split on ',' (no quoted fields needed based on your files)
    std::vector<std::string> out;
    std::string cur;
    std::istringstream ss(line);
    while (std::getline(ss, cur, ',')) {
        trim_inplace(cur);
        out.push_back(cur);
    }
    return out;
}

// Constructor from a line in tanks.txt
Tank::Tank(const std::string& line) {
    // Expected: name,baseHealth,baseArmor,basePenChance,preBonusCap
    auto fields = split_csv_simple(line);
    if (fields.size() < 5) {
        std::cerr << "Invalid tank line: " << line << "\n";
        return;
    }
    name          = fields[0];
    baseHealth    = std::stoi(fields[1]);
    baseArmor     = std::stod(fields[2]);
    basePenChance = std::stod(fields[3]);
    preBonusCap   = std::stod(fields[4]);
}
Weapon::Weapon(const std::string& line) {
    // Expected: name,damageHealth,damageArmor,penMod
    auto fields = split_csv_simple(line);
    if (fields.size() < 4) {
        std::cerr << "Invalid weapon line: " << line << "\n";
        return;
    }
    name         = fields[0];
    damageHealth = std::stoi(fields[1]);
    damageArmor  = std::stoi(fields[2]);
    penMod       = std::stod(fields[3]);
}


std::vector<Tank> loadTanks(const std::string& filePath) {
    std::vector<Tank> tanks;
    std::ifstream file(filePath);
    if (!file) {
        std::cerr << "Cannot open tank file: " << filePath << "\n";
        return tanks;
    }
    std::string line;
    while (std::getline(file, line)) {
        trim_inplace(line);
        if (line.empty() || (!line.empty() && line[0] == '#')) continue;
        tanks.emplace_back(line);
    }
    return tanks;
}

std::vector<Weapon> loadWeapons(const std::string& filePath) {
    std::vector<Weapon> weapons;
    std::ifstream file(filePath);
    if (!file) {
        std::cerr << "Cannot open weapon file: " << filePath << "\n";
        return weapons;
    }
    std::string line;
    while (std::getline(file, line)) {
        trim_inplace(line);
        if (line.empty() || (!line.empty() && line[0] == '#')) continue;
        weapons.emplace_back(line);
    }
    return weapons;
}
