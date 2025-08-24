#pragma once
#include <string>
#include <vector>

// Forward declarations only, no code bodies here!
struct Tank {
    std::string name;
    int baseHealth;
    double baseArmor;
    double basePenChance; // P0
    double preBonusCap;   // S0

    Tank() = default;
    Tank(const std::string& line); // Declaration only
};

struct Weapon {
    std::string name;
    int damageHealth;
    int damageArmor; // fraction of tank armor
    double penMod;

    Weapon() = default;
    Weapon(const std::string& line); // Declaration only
};

// Function declarations only
std::vector<Tank> loadTanks(const std::string& resourceFile);
std::vector<Weapon> loadWeapons(const std::string& resourceFile);

