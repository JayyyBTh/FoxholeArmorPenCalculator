#include <iostream>
#include "calculator.h"
#include <iomanip>
#include <algorithm>
#include <cmath>

double rangeBonus(double rangeMeters) {
    double x = std::max(0.0, 1.0 - (std::max(0.0, rangeMeters) + 5.0) / 40.0);
    return 0.40 * std::pow(x, 1.5);
}

double angleBonus(double angleDeg) {
    const double pi = 3.14159265358979323846;
    double a = std::clamp(angleDeg, 0.0, 90.0);
    return 0.40 * std::cos(a * pi / 180.0);
}

double computePenChance(const Tank& t, const Weapon& s, double armorFrac, double bonus) {

    double S = 1.0 - armorFrac;                       // stripped fraction
    double pre = std::max(t.basePenChance, S);        // base effective
    double capped = std::min(t.preBonusCap, pre);    // pre-bonus cap
    double P = s.penMod * capped + bonus;             // apply ammo + bonuses
    return std::clamp(P, 0.0, 1.0);

}

bool State::operator<(const State& o) const {
    if (health != o.health) return health < o.health;
    return armorFrac < o.armorFrac;
}

void killProbability(const Tank& t, const Weapon& s, const double& bonus, const double& initialArmorFrac, const double& velocityMod, std::ostream& out) {

    out << "Calculating shots to kill full health and " << initialArmorFrac*100 << "% armor " << t.name << " with " 
        << (100*velocityMod)-100 << "% velocity modifier " << s.name << ". Angle and range bonuses sum up to "
        << std::fixed << std::setprecision(2) << bonus * 100.0 << " percentage points" << std::endl;
    
    using Dist = std::map<State, double>;

    //printDebugInputs(t,s,initialArmorFrac,bonus);

    Dist current;
    current[{initialArmorFrac, t.baseHealth}] = 1.0;

    double deadProbPrev = 0.0;

    int minShots = (t.baseHealth + s.damageHealth - 1) / s.damageHealth;

    for (int shot = 1; ; ++shot) {
        Dist next;
        double deadProb = deadProbPrev;

        for (auto& kv : current) {
            State st = kv.first;
            double w = kv.second;

            if (st.health <= 0) {
                deadProb += w;
                continue;
            }

            double p = computePenChance(t, s, st.armorFrac, bonus);



            //State Debugger

            /*    out << "Shot: " << shot
                << " | Current State: Health=" << st.health
                << ", ArmorFrac=" << st.armorFrac
                << ", Weight=" << w
                << ", PenChance=" << p << "\n"; */



            // Penetration branch
            {
                State sp = st;
                double armorFracLoss = (s.damageArmor * velocityMod) / t.baseArmor;
                sp.armorFrac = std::max(0.0, st.armorFrac - armorFracLoss);
                sp.health = std::max(0, st.health - static_cast<int>(s.damageHealth * velocityMod));

                if (sp.health <= 0) deadProb += w * p;
                else next[sp] += w * p;
            }

            // No-penetration branch (no damage)
            next[st] += w * (1.0 - p);
        }

        double cumulative = deadProb;

        if (shot >= minShots) {
            out << "Shots: " << shot
                      << " -> Kill chance = "
                      << std::fixed << std::setprecision(2)
                      << cumulative * 100.0 << "%\n";
        }

        if (cumulative >= 0.95) break;

        current = std::move(next);
        deadProbPrev = deadProb;
    }
}

void printDebugInputs(const Tank& t, const Weapon& s, double armorFrac, double bonus) {
    std::cerr << "=== KillProbability Inputs ===";
    std::cerr << "Tank:" << t.name
             << "| Health:" << t.baseHealth
             << "| Armor:" << t.baseArmor
             << "| BasePenChance:" << t.basePenChance
             << "| PreBonusCap:" << t.preBonusCap;
    std::cerr << "Weapon:" << s.name
             << "| DamageHealth:" << s.damageHealth
             << "| DamageArmor:" << s.damageArmor
             << "| PenMod:" << s.penMod;
    std::cerr << "Initial ArmorFrac:" << armorFrac
             << "| Bonus:" << bonus;
    std::cerr << "==============================";
}




