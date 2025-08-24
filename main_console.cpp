#include <iostream>
#include <sstream>
#include <QCoreApplication>
#include <QMap>
#include <QString>
#include <QVector>

#include "tanksnshells.h"
#include "calculator.h"

int main(int argc, char* argv[]) {
    QCoreApplication app(argc, argv); // no GUI, but allows Qt containers

    if (argc != 7) {
        std::cerr << "Usage: " << argv[0]
                  << " <tankName> <weaponName> <armorFrac> <rangeBonus> <angleBonus> <velocity>\n";
        return 1;
    }

    QString tankName   = QString::fromUtf8(argv[1]).trimmed();
    QString weaponName = QString::fromUtf8(argv[2]).trimmed();
    bool ok = true;

    double armorFrac  = QString::fromUtf8(argv[3]).toDouble(&ok); if (!ok) { std::cerr << "Invalid armorFrac\n"; return 1; }
    double rangeBonus = QString::fromUtf8(argv[4]).toDouble(&ok); if (!ok) { std::cerr << "Invalid rangeBonus\n"; return 1; }
    double angleBonus = QString::fromUtf8(argv[5]).toDouble(&ok); if (!ok) { std::cerr << "Invalid angleBonus\n"; return 1; }
    double velocity   = QString::fromUtf8(argv[6]).toDouble(&ok); if (!ok) { std::cerr << "Invalid velocity\n"; return 1; }

    double bonus = rangeBonus + angleBonus;

    // ⚠️ IMPORTANT: load from *real files*, not Qt resources
    QVector<Tank> tanks   = loadTanks("tanks.txt");
    QVector<Weapon> weapons = loadWeapons("weapons.txt");

    if (tanks.isEmpty() || weapons.isEmpty()) {
        std::cerr << "Could not load tanks.txt or weapons.txt\n";
        return 1;
    }

    QMap<QString, Tank> tankMap;
    QMap<QString, Weapon> weaponMap;
    for (const Tank& t : tanks)   tankMap[t.name] = t;
    for (const Weapon& w : weapons) weaponMap[w.name] = w;

    if (!tankMap.contains(tankName)) {
        std::cerr << "Tank not found: " << tankName.toStdString() << "\n";
        return 1;
    }
    if (!weaponMap.contains(weaponName)) {
        std::cerr << "Weapon not found: " << weaponName.toStdString() << "\n";
        return 1;
    }

    const Tank& t = tankMap[tankName];
    const Weapon& w = weaponMap[weaponName];

    std::ostringstream oss;
    killProbability(t, w, bonus, armorFrac, velocity, oss);

    std::cout << oss.str();
    return 0;
}
