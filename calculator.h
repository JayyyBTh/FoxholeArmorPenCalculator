#pragma once
#include "tanksnshells.h"  // for Tank, Weapon
#include <map>

// Flat pen bonus (fraction, e.g. 0.3274) from engagement range in metres:
//   0.40 * max(0, 1 - (d + 5) / 40)^1.5   -> +32.74% at 0 m, 0 from 35 m.
double rangeBonus(double rangeMeters);

// Flat pen bonus (fraction) from hit angle in degrees:
//   0.40 * cos(angle), angle clamped to [0, 90].
// 0 deg = shot square to the target's SIDE (+40%), 90 deg = head-on (+0%).
// NB: the wiki's vehicle pen-chance table labels these the other way round.
double angleBonus(double angleDeg);

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
