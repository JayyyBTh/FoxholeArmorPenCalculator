#pragma once
#include <QString>
#include <QVector>

// Forward declarations only, no code bodies here!
struct Tank {
    QString name;
    int baseHealth;
    double baseArmor;
    double basePenChance; // P0
    double preBonusCap;   // S0

    Tank() = default;
    Tank(const QString& line); // Declaration only
};

struct Weapon {
    QString name;
    int damageHealth;
    int damageArmor; // fraction of tank armor
    double penMod;

    Weapon() = default;
    Weapon(const QString& line); // Declaration only
};

// Function declarations only
QVector<Tank> loadTanks(const QString& resourceFile);
QVector<Weapon> loadWeapons(const QString& resourceFile);
