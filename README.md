# Airzone Modbus Client

Client Python minimal permettant de communiquer avec un système **Airzone** via Modbus TCP.

Cette bibliothèque a été développée pour permettre la lecture et l'écriture des principaux paramètres d'un système Airzone : état des zones, température, humidité, consigne, thermostat Lite, mode de fonctionnement, vitesse de ventilation, etc.

> ⚠️ **Important**
>
> Cette bibliothèque repose sur des observations et des tests réalisés sur un système Airzone réel.
>
> La documentation Modbus Airzone disponible publiquement n'étant pas toujours suffisamment détaillée pour tous les registres utilisés ici, certaines informations ont été déterminées expérimentalement.
>
> Les valeurs et registres documentés dans ce README correspondent donc aux informations actuellement vérifiées avec ce client.

---

## Installation

La bibliothèque utilise [`pymodbus`](https://pypi.org/project/pymodbus/) pour la communication Modbus TCP.

```bash
pip install pymodbus
```

---

## Utilisation

Création du client :

```python
from airzone_modbus import AirzoneClient

client = AirzoneClient(
    host="192.168.1.7",
    port=8899,
)
```

Connexion :

```python
if client.connect():
    print("Connecté")
```

Lecture d'un registre :

```python
value = client.read_registers(
    address=0,
    count=1,
)

print(value)
```

Fermeture :

```python
client.close()
```

---

# Architecture Modbus

Le système Airzone utilise plusieurs espaces de registres.

Les registres utilisés par cette bibliothèque sont principalement :

* les **Holding Registers** pour les paramètres de configuration et de fonctionnement ;
* les **Input Registers** pour certaines informations provenant directement du thermostat.

Les zones sont organisées par blocs de registres.

Pour une zone donnée, son adresse de base est utilisée comme référence :

```text
Zone 1 → 0x0100 → 256
Zone 2 → 0x0200 → 512
Zone 3 → 0x0300 → 768
...
Zone 16 → 0x1000 → 4096
```

Autrement dit :

```text
adresse de base = numéro de zone × 256
```

La méthode :

```python
read_machine_zone_bases()
```

permet de récupérer automatiquement les adresses de base des zones présentes.

---

# Registres des zones

Chaque zone possède plusieurs registres.

Les registres actuellement exploités sont :

| Registre | Fonction                                        |
| -------- | ----------------------------------------------- |
| R00      | État et paramètres de fonctionnement de la zone |
| R03      | Consigne                                        |
| R08      | Température de la sonde                         |
| R10      | Température locale du thermostat                |
| R14-R19  | Nom de la zone                                  |
| R26      | Paramètres du thermostat Lite                   |
| R31      | Humidité                                        |

---

# R00 — État et paramètres de la zone

Le registre **R00** est un registre 16 bits.

Plusieurs paramètres de la zone sont stockés sous forme de bits.

```text
Bit     Fonction
────────────────────────────────
0       Ventilation locale
1       Programmation désactivée
2       État de la zone
3-5     Non utilisés par cette bibliothèque
6-7     Mode veille
8-11    Mode de fonctionnement
12      Mode automatique
13-14   Non utilisés par cette bibliothèque
15      Bit non identifié
```

## Bit 0 — Ventilation locale

Indique si la ventilation locale est active.

Méthode :

```python
read_zone_local_ventilation()
```

Retour :

```python
True
False
```

---

## Bit 1 — Programmation désactivée

Indique si la programmation horaire de la zone est désactivée.

Méthode de lecture :

```python
read_zone_schedule_disabled()
```

Écriture :

```python
write_zone_schedule_disabled()
```

---

## Bit 2 — État de la zone

Indique si la zone est active.

Méthode de lecture :

```python
read_zone_state()
```

Méthode d'écriture :

```python
write_zone_state()
```

Exemple :

```python
client.write_zone_state(
    base_address=1024,
    state=True,
)
```

La méthode modifie uniquement le bit 2 et conserve les autres paramètres du registre R00.

---

## Bits 6-7 — Mode veille

Deux bits permettent de sélectionner le mode veille :

```text
Valeur    Mode
────────────────
0         Veille Off
1         Veille 30
2         Veille 60
3         Veille 90
```

Lecture numérique :

```python
read_zone_sleep_mode()
```

Lecture avec nom :

```python
read_zone_sleep_mode_name()
```

Écriture :

```python
write_zone_sleep_mode()
```

Exemple :

```python
client.write_zone_sleep_mode(
    base_address=1024,
    sleep_mode=2,
)
```

---

## Bits 8-11 — Mode de fonctionnement de la zone

Le mode de fonctionnement est stocké sur 4 bits.

```text
Valeur    Mode
────────────────────────
0         Arrêt
1         Refroidissement
3         Ventilation
5         Chauffage
6         Sec
```

Lecture numérique :

```python
read_zone_mode()
```

Lecture avec nom :

```python
read_zone_mode_name()
```

Écriture :

```python
write_zone_mode()
```

Exemple :

```python
client.write_zone_mode(
    base_address=1024,
    mode=1,
)
```

---

## Bit 12 — Mode automatique

Indique si le mode automatique de la zone est activé.

Lecture :

```python
read_zone_automatic_mode()
```

Écriture :

```python
write_zone_automatic_mode()
```

---

## Bit 15

Le bit 15 est actuellement exposé uniquement à des fins d'analyse :

```python
read_zone_bit15()
```

Sa fonction exacte n'est pas encore identifiée.

---

# R03 — Consigne

Le registre **R03** contient la consigne de température.

La valeur est exprimée en **dixièmes de degré Celsius**.

Par exemple :

```text
205 → 20,5 °C
215 → 21,5 °C
230 → 23,0 °C
```

La méthode :

```python
read_zone_setpoint()
```

retourne directement une valeur en degrés Celsius.

Exemple :

```python
setpoint = client.read_zone_setpoint(
    base_address=1024,
)

print(setpoint)
```

Résultat :

```text
21.5
```

## Écriture de la consigne

La méthode :

```python
write_zone_setpoint()
```

permet de modifier la consigne.

La plage actuellement autorisée est :

```text
18,0 °C → 30,0 °C
```

La résolution est de :

```text
0,5 °C
```

Exemple :

```python
client.write_zone_setpoint(
    base_address=1024,
    setpoint=22.5,
)
```

La méthode vérifie automatiquement que la valeur est valide avant de l'écrire.

---

# R08 — Température de la sonde

Le registre **R08** contient la température provenant de la sonde de la zone.

La valeur est exprimée en dixièmes de degré Celsius.

Exemple :

```text
215 → 21,5 °C
```

Lecture :

```python
read_zone_temperature()
```

Exemple :

```python
temperature = client.read_zone_temperature(
    base_address=1024,
)
```

---

# R10 — Température du thermostat

La température locale du thermostat est disponible dans les **Input Registers**.

La bibliothèque utilise l'adresse :

```text
base_address + 10
```

Lecture :

```python
read_zone_thermostat_temperature()
```

Exemple :

```python
temperature = client.read_zone_thermostat_temperature(
    base_address=1024,
)
```

La valeur est également exprimée en dixièmes de degré Celsius.

Cette température correspond à la mesure effectuée directement par le thermostat.

---

# R14-R19 — Nom de la zone

Le nom de la zone est stocké sur six registres :

```text
R14
R15
R16
R17
R18
R19
```

Soit 12 octets.

Les caractères sont stockés deux par deux dans les registres.

La méthode :

```python
read_zone_name()
```

reconstitue automatiquement la chaîne de caractères.

Exemple :

```python
name = client.read_zone_name(
    base_address=1024,
)

print(name)
```

Résultat possible :

```text
Salon
```

---

# R26 — Paramètres du thermostat Lite

Le registre **R26** contient plusieurs paramètres associés au thermostat Lite.

```text
Bit       Fonction
────────────────────────────
0-2       Offset de température
3         LED du thermostat
4         Non utilisé
5         Présence thermostat Lite
6-15      Non utilisés par cette bibliothèque
```

---

## Bits 0-2 — Offset du thermostat Lite

Les trois premiers bits correspondent à l'offset appliqué au thermostat Lite.

Correspondance :

```text
Valeur    Offset
────────────────
0         -3 °C
1         -2 °C
2         -1 °C
3          0 °C
4         +1 °C
5         +2 °C
6         +3 °C
```

Lecture :

```python
read_thermostat_lite_setpoint_offset()
```

Exemple :

```python
offset = client.read_thermostat_lite_setpoint_offset(
    base_address=1024,
)
```

Écriture :

```python
write_thermostat_lite_setpoint_offset()
```

Exemple :

```python
client.write_thermostat_lite_setpoint_offset(
    base_address=1024,
    offset=-1,
)
```

La méthode accepte uniquement :

```text
-3
-2
-1
 0
+1
+2
+3
```

---

## Bit 3 — LED du thermostat Lite

Le bit 3 contrôle la LED du thermostat Lite.

Lecture :

```python
read_thermostat_lite_status_led()
```

Écriture :

```python
write_thermostat_lite_status_led()
```

Exemple :

```python
client.write_thermostat_lite_status_led(
    base_address=1024,
    enabled=True,
)
```

---

## Bit 5 — Présence du thermostat Lite

Le bit 5 indique la présence d'un thermostat Lite.

Lecture :

```python
read_thermostat_lite_present()
```

---

# R31 — Humidité

Le registre **R31** contient l'humidité de la zone.

La valeur est exprimée directement en pourcentage.

Exemple :

```text
45 → 45 %
```

Lecture :

```python
read_zone_humidity()
```

Exemple :

```python
humidity = client.read_zone_humidity(
    base_address=1024,
)
```

---

# Registres de la machine

Contrairement aux zones, les registres de la machine sont adressés directement à partir de `0`.

Les registres actuellement utilisés sont :

| Registre | Fonction                      |
| -------- | ----------------------------- |
| R00      | Mode et vitesse de la machine |
| R09      | Zones présentes               |

---

# Machine R00 — Mode et vitesse

Le registre **R00** de la machine contient notamment le mode de fonctionnement et la vitesse de ventilation.

```text
Bits       Fonction
────────────────────────────
0-8        Mode machine
9-10       Vitesse de ventilation
11-15      Non utilisés par cette bibliothèque
```

---

## Bits 0-8 — Mode machine

Le mode machine est codé sur 9 bits.

Les valeurs observées sont :

```text
Valeur    Mode
────────────────────────────────
0         Arrêt
1         Refroidissement
2         Chauffage rayonnant
3         Ventilation
4         Chauffage air
5         Chauffage
6         Sec
7         Chaud auxiliaire
8         Refroidissement rayonnant
9         Refroidissement
258       Chauffage
```

Lecture numérique :

```python
read_machine_mode()
```

Lecture avec nom :

```python
read_machine_mode_name()
```

---

## Bits 9-10 — Vitesse de ventilation

La vitesse est codée sur deux bits.

```text
Valeur    Vitesse
────────────────
0         Automatique
1         Faible
2         Moyenne
3         Élevée
```

Lecture :

```python
read_machine_speed()
```

Lecture avec nom :

```python
read_machine_speed_name()
```

---

# Écriture du mode machine

La méthode :

```python
write_machine_mode()
```

permet de modifier le mode de fonctionnement de la machine.

Exemple :

```python
client.write_machine_mode(
    mode=1,
)
```

La méthode effectue une lecture préalable du registre afin de conserver les bits qui ne sont pas modifiés.

---

# Écriture de la vitesse machine

La méthode :

```python
write_machine_speed()
```

modifie uniquement les bits 9-10 du registre R00.

Exemple :

```python
client.write_machine_speed(
    speed=2,
)
```

Les autres bits du registre sont conservés.

---

# Machine R09 — Zones présentes

Le registre **R09** indique quelles zones sont présentes dans le système.

Chaque bit correspond à une zone :

```text
Bit 0  → Zone 1
Bit 1  → Zone 2
Bit 2  → Zone 3
...
Bit 15 → Zone 16
```

La méthode :

```python
read_machine_zones()
```

retourne directement la liste des zones détectées.

Exemple :

```python
zones = client.read_machine_zones()

print(zones)
```

Résultat possible :

```python
[1, 2, 4, 5]
```

---

# Adresses de base des zones

À partir des zones détectées, la méthode :

```python
read_machine_zone_bases()
```

retourne leurs adresses de base.

Exemple :

```python
bases = client.read_machine_zone_bases()

print(bases)
```

Résultat :

```python
[256, 512, 1024, 1280]
```

Ce qui correspond à :

```text
Zone 1 → 256
Zone 2 → 512
Zone 4 → 1024
Zone 5 → 1280
```

---

# Écriture des registres de zone

Certaines opérations nécessitent de modifier seulement quelques bits d'un registre.

Pour éviter d'écraser les autres paramètres, la bibliothèque utilise une opération de type **read-modify-write**.

Par exemple, pour modifier l'état de la zone :

1. lecture de R00 ;
2. modification du bit 2 ;
3. conservation de tous les autres bits ;
4. écriture du nouveau R00.

Cette logique est utilisée notamment par :

```python
_modify_zone_r00()
```

et :

```python
_modify_zone_r26()
```

Elle permet de modifier individuellement certains paramètres sans perturber les autres.

---

# Écriture directe d'un R00 de zone

La méthode :

```python
write_zone_r00()
```

permet également d'écrire directement la totalité du registre R00.

Exemple :

```python
client.write_zone_r00(
    base_address=1024,
    value=0x0504,
)
```

> ⚠️ Cette méthode écrit l'intégralité du registre. Elle doit donc être utilisée avec précaution.
>
> Pour modifier un seul paramètre, il est préférable d'utiliser les méthodes spécialisées comme `write_zone_state()`, `write_zone_mode()` ou `write_zone_sleep_mode()`.

---

# Référence rapide des méthodes

## Connexion

```python
connect()
close()
```

## Lecture Modbus générique

```python
read_registers()
read_input_registers()
```

## Zones — R00

```python
read_zone_local_ventilation()
read_zone_schedule_disabled()
read_zone_state()
read_zone_sleep_mode()
read_zone_sleep_mode_name()
read_zone_mode()
read_zone_mode_name()
read_zone_automatic_mode()
read_zone_bit15()

write_zone_r00()
write_zone_schedule_disabled()
write_zone_state()
write_zone_sleep_mode()
write_zone_mode()
write_zone_automatic_mode()
```

## Zone — température / consigne

```python
read_zone_setpoint()
write_zone_setpoint()

read_zone_temperature()
read_zone_thermostat_temperature()
```

## Zone — informations

```python
read_zone_name()
read_zone_humidity()
```

## Thermostat Lite — R26

```python
read_zone_r26()

read_thermostat_lite_setpoint_offset()
write_thermostat_lite_setpoint_offset()

read_thermostat_lite_status_led()
write_thermostat_lite_status_led()

read_thermostat_lite_present()
```

## Machine — R00

```python
read_machine_register_0()

read_machine_mode()
read_machine_mode_name()

read_machine_speed()
read_machine_speed_name()

write_machine_mode()
write_machine_speed()
```

## Machine — R09

```python
read_machine_zones()
read_machine_zone_bases()
```

---

# Exemple complet

```python
from airzone_modbus import AirzoneClient


client = AirzoneClient(
    host="192.168.1.7",
    port=8899,
)

if not client.connect():
    raise RuntimeError("Impossible de se connecter à Airzone")


try:

    # --------------------------------------------------------
    # Machine
    # --------------------------------------------------------

    print(
        "Mode machine :",
        client.read_machine_mode_name(),
    )

    print(
        "Vitesse machine :",
        client.read_machine_speed_name(),
    )

    print(
        "Zones présentes :",
        client.read_machine_zones(),
    )


    # --------------------------------------------------------
    # Zone 4
    # --------------------------------------------------------

    base = 4 * 256

    print(
        "Nom :",
        client.read_zone_name(base),
    )

    print(
        "État :",
        client.read_zone_state(base),
    )

    print(
        "Mode :",
        client.read_zone_mode_name(base),
    )

    print(
        "Consigne :",
        client.read_zone_setpoint(base),
        "°C",
    )

    print(
        "Température sonde :",
        client.read_zone_temperature(base),
        "°C",
    )

    print(
        "Température thermostat :",
        client.read_zone_thermostat_temperature(base),
        "°C",
    )

    print(
        "Humidité :",
        client.read_zone_humidity(base),
        "%",
    )

    print(
        "Offset thermostat Lite :",
        client.read_thermostat_lite_setpoint_offset(base),
        "°C",
    )

    print(
        "LED thermostat Lite :",
        client.read_thermostat_lite_status_led(base),
    )

finally:

    client.close()
```

---

# Limites actuelles

Cette bibliothèque ne cherche volontairement pas à implémenter l'intégralité du protocole Modbus Airzone.

Elle se concentre sur les registres et fonctions qui ont été identifiés et testés.

Certains bits ou registres restent volontairement non documentés lorsqu'ils n'ont pas encore été identifiés avec suffisamment de certitude.

Les fonctions suivantes sont notamment conservées comme outils d'analyse :

```python
read_zone_r26()
read_zone_bit15()
read_machine_register_0()
read_zone_r00()
```

Elles permettent de travailler directement avec les valeurs brutes lorsque cela est nécessaire.

---

# Remarques sur les écritures

Les écritures Modbus modifient directement le système Airzone.

Il est recommandé de tester les écritures avec prudence, particulièrement :

```python
write_zone_r00()
write_machine_mode()
write_machine_speed()
```

Les méthodes spécialisées utilisant une logique de lecture-modification-écriture sont préférables lorsqu'elles existent.

---

# État du projet

Fonctionnalités actuellement implémentées :

* [x] Connexion Modbus TCP
* [x] Lecture des Holding Registers
* [x] Lecture des Input Registers
* [x] Détection des zones
* [x] Lecture de l'état des zones
* [x] Lecture/écriture du mode des zones
* [x] Lecture/écriture du mode veille
* [x] Lecture/écriture de la consigne
* [x] Lecture de la température de zone
* [x] Lecture de la température du thermostat
* [x] Lecture du nom des zones
* [x] Lecture de l'humidité
* [x] Lecture/écriture de l'offset du thermostat Lite
* [x] Lecture/écriture de la LED du thermostat Lite
* [x] Détection de la présence du thermostat Lite
* [x] Lecture du mode machine
* [x] Écriture du mode machine
* [x] Lecture de la vitesse machine
* [x] Écriture de la vitesse machine
* [x] Détection des zones présentes

---

## Licence

À compléter selon la licence choisie pour le projet.
