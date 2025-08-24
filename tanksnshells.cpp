#include <QString>
#include <QFile>
#include <QTextStream>
#include <QVector>
#include <QStringList>
#include <QDebug>
#include "tanksnshells.h"

// Constructor from a line in tanks.txt
    Tank::Tank(const QString& line) {
        // Assume CSV format: name,baseHealth,baseArmor,basePenChance,preBonusCap
        QStringList fields = line.split(',');
        if (fields.size() < 5) {
            qWarning() << "Invalid tank line:" << line;
            return;
        }
        name = fields[0].trimmed();
        baseHealth = fields[1].toInt();
        baseArmor = fields[2].toDouble();
        basePenChance = fields[3].toDouble();
        preBonusCap = fields[4].toDouble();
    }

Weapon::Weapon(const QString& line) {
        QStringList fields = line.split(',');
        if (fields.size() < 4) {
            qWarning() << "Invalid weapon line:" << line;
            return;
        }
        name = fields[0].trimmed();
        damageHealth = fields[1].toInt();
        damageArmor = fields[2].toInt();
        penMod = fields[3].toDouble();
    }


QVector<Tank> loadTanks(const QString& resourceFile) {
    QVector<Tank> tanks;
    QFile file(resourceFile);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        qWarning() << "Cannot open tank file:" << resourceFile;
        return tanks;
    }
    QTextStream in(&file);
    while (!in.atEnd()) {
        QString line = in.readLine();
        if (line.trimmed().isEmpty() || line.startsWith('#')) continue; // skip empty/comment lines
        tanks.append(Tank(line));
    }
    return tanks;
}

QVector<Weapon> loadWeapons(const QString& resourceFile) {
    QVector<Weapon> weapons;
    QFile file(resourceFile);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        qWarning() << "Cannot open weapon file:" << resourceFile;
        return weapons;
    }
    QTextStream in(&file);
    while (!in.atEnd()) {
        QString line = in.readLine();
        if (line.trimmed().isEmpty() || line.startsWith('#')) continue;
        weapons.append(Weapon(line));
    }
    return weapons;
}
