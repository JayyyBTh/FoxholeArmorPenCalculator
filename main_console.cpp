#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>

#include "tanksnshells.h"
#include "calculator.h"

int main(int argc, char* argv[]) {
    QCoreApplication app(argc, argv); // no GUI, but allows Qt containers

    if (argc != 7) {
        std::cerr << "Usage: " << argv[0]
                  << " <tankName> <weaponName> <armorFrac> <rangeBonus> <angleBonus> <velocity>\n";
        return 1;
    }

    std::string tankName   = argv[1];
    std::string weaponName = argv[2];

    try {
        double armorFrac  = std::stod(argv[3]);
        double rangeBonus = std::stod(argv[4]);
        double angleBonus = std::stod(argv[5]);
        double velocity   = std::stod(argv[6]);
        double bonus = rangeBonus + angleBonus;

        // Load data files from the working directory
        std::vector<Tank>   tanks   = loadTanks("tanks.txt");
        std::vector<Weapon> weapons = loadWeapons("weapons.txt");
        if (tanks.empty() || weapons.empty()) {
            std::cerr << "Could not load tanks.txt or weapons.txt\n";
            return 1;
        }

    std::map<std::string, Tank>   tankMap;
        std::map<std::string, Weapon> weaponMap;
        for (const auto& t : tanks)   tankMap[t.name] = t;
        for (const auto& w : weapons) weaponMap[w.name] = w;
        
    if (!tankMap.count(tankName)) {
            std::cerr << "Tank not found: " << tankName << "\n";
            return 1;
        }
        if (!weaponMap.count(weaponName)) {
            std::cerr << "Weapon not found: " << weaponName << "\n";
            return 1;
        }

    const Tank& t = tankMap[tankName];
    const Weapon& w = weaponMap[weaponName];

    std::ostringstream oss;
    killProbability(t, w, bonus, armorFrac, velocity, oss);

    std::cout << oss.str();
    return 0;
    } catch (const std::exception& e) {
        std::cerr << "Invalid numeric argument: " << e.what() << "\n";
        return 1;
    }
}

