#pragma once
#include "tanksnshells.h"  // for Tank, Weapon
#include <map>

// Compute penetration chance for a given state
double computePenChance(const Tank& t, const Weapon& s, double armorFrac, double bonus);

// State of a tank during combat
struct State {
    double armorFrac; // 1.0 = full armor, 0.0 = none
    int health;
    bool operator<(const State& o) const;
};

// Simulate probability of kill after successive shots
void killProbability(const Tank& t, const Weapon& s, const double& bonus, const double& initialArmorFrac, const double& velocityMod, std::ostream& out);

void printDebugInputs(const Tank& t, const Weapon& s, double armorFrac, double bonus);
