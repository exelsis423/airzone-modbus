"""Client Modbus pour les systèmes Airzone."""

from pymodbus.client import ModbusTcpClient


class AirzoneClient:
    """Client minimal de communication avec Airzone."""

    def __init__(self, host: str, port: int = 8899):
        self.host = host
        self.port = port
        self.client = ModbusTcpClient(
            host=self.host,
            port=self.port,
        )

    def connect(self) -> bool:
        """Établit la connexion Modbus."""
        return self.client.connect()

    def close(self) -> None:
        """Ferme la connexion."""
        self.client.close()

    def read_registers(
        self,
        address: int,
        count: int,
        slave: int = 1,
    ) -> list[int]:
        """Lit des registres Holding."""
        response = self.client.read_holding_registers(
            address=address,
            count=count,
            device_id=slave,
        )

        if response.isError():
            raise RuntimeError(
                f"Erreur Modbus : {response}"
            )

        return response.registers
        
    def read_input_registers(self, address, count, slave=1):
        response = self.client.read_input_registers(
            address=address,
            count=count,
            device_id=slave,
        )
    
        if response.isError():
            raise RuntimeError(f"Erreur Modbus : {response}")
    
        return response.registers

    """ REGISTRE R00 """
    """ BIT 0 : Ventilation locale """
    def read_zone_local_ventilation(self, base, slave=1):
        value = self.read_registers(
            address=base,
            count=1,
            slave=slave,
        )[0]
    
        return bool(value & (1 << 0))
        
    """ BIT 1 : Désactivation des programmations horaires de la zone """
    def read_zone_schedule_disabled(self, base, slave=1):
        value = self.read_registers(
            address=base,
            count=1,
            slave=slave,
        )[0]
    
        return bool(value & (1 << 1))
    
    """ BIT 2 : État de la zone """
    def read_zone_state(self, base_address, slave=1):
        registers = self.read_registers(
            address=base_address,
            count=1,
            slave=slave,
        )
    
        return bool(registers[0] & (1 << 2))

    """ BIT 4-5 : Sélection de la vitesse """
    def read_zone_speed(self, base_address, slave=1):
        registers = self.read_registers(
            address=base_address,
            count=1,
            slave=slave,
        )
    
        return (registers[0] >> 4) & 0b11
    def read_zone_speed_name(self, base_address, slave=1):
        speed = self.read_zone_speed(
            base_address,
            slave=slave,
        )
    
        names = {
            0: "Automatique",
            1: "Faible",
            2: "Moyenne",
            3: "Élevée",
        }
    
        return names.get(speed, f"Inconnue ({speed})")

    """ BIT 6-7 : Mode Veille """
    def read_zone_sleep_mode(self, base, slave=1):
        value = self.read_registers(
            address=base,
            count=1,
            slave=slave,
        )[0]
    
        return (value >> 6) & 0x03
    def read_zone_sleep_mode_name(self, base, slave=1):
        """Retourne le nom du mode veille."""
        modes = {
            0: "Veille Off",
            1: "Veille 30",
            2: "Veille 60",
            3: "Veille 90",
        }
    
        return modes.get(
            self.read_zone_sleep_mode(base, slave),
            "Inconnu",
        )
    
    """ BIT 8-11 : Mode de la zone """
    def read_zone_mode(self, base_address, slave=1):
        registers = self.read_registers(
            address=base_address,
            count=1,
            slave=slave,
        )
    
        return (registers[0] >> 8) & 0x0F
    def read_zone_mode_name(self, base_address, slave=1):
        mode = self.read_zone_mode(
            base_address,
            slave=slave,
        )
    
        names = {
            0: "Arrêt",
            1: "Refroidissement",
            3: "Ventilation",
            5: "Chauffage",
            6: "Sec",
        }
    
        return names.get(mode, f"Inconnu ({mode})")

    """ BIT 12 : Mode automatique """
    def read_zone_automatic_mode(self, base, slave=1):
        value = self.read_registers(
            address=base,
            count=1,
            slave=slave,
        )[0]
    
        return bool(value & (1 << 12))    
    
    """ BIT 15 : Fonction dépendante du système :
        - Désactivation des programmations horaires de la zone
        - Mode d'utilisation basique sur VAF / ZBS
        """
    def read_zone_bit15(self, base, slave=1):
        value = self.read_registers(
            address=base,
            count=1,
            slave=slave,
        )[0]
    
        return bool(value & (1 << 15))
        

    
    
    """ REGISTRE R03 """
    """ consigne en dixièmes de degré Celsius. """
    def read_zone_setpoint(self, base_address, slave=1):
        registers = self.read_registers(
            address=base_address,
            count=4,
            slave=slave,
        )
    
        return registers[3] / 10.0


        
    
    
    
    """ REGISTRE R08 """
    """ T. sonde à distance """
    def read_zone_temperature(self, base_address, slave=1):
        """
        Lit la température actuelle d'une zone.

        R08 = température en dixièmes de degré Celsius.
        Exemple : 231 -> 23.1 °C
        """
        registers = self.read_registers(
            address=base_address,
            count=9,
            slave=slave,
        )

        return registers[8] / 10.0
    
    
    
    """ REGISTRE R10 """
    """ T. locale du thermostat """
    def read_zone_thermostat_temperature(self, base, slave=1):
        registers = self.read_input_registers(
            address=base + 10,
            count=1,
            slave=slave,
        )
        return registers[0] / 10.0

    
    """ REGISTRE R14 - R19 """
    """ Le nom est stocké dans R14 à R19, avec deux caractères ASCII par registre. """
    def read_zone_name(self, base_address, slave=1):
        registers = self.read_registers(
            address=base_address,
            count=20,
            slave=slave,
        )
    
        data = bytearray()
    
        for value in registers[14:20]:
            data.append((value >> 8) & 0xFF)
            data.append(value & 0xFF)
    
        return data.split(b"\x00")[0].decode("ascii", errors="replace")

    """ REGISTRE R26 """
    """ BIT 1-2 : Offset de consigne du thermostat Lite """
    def read_thermostat_lite_setpoint_offset(self, base_address, slave=1):
        registers = self.read_registers(
            address=base_address,
            count=27,
            slave=slave,
        )
    
        value = registers[26] & 0b111
    
        offsets = {
            0: -3,
            1: -2,
            2: -1,
            3: 0,
            4: 1,
            5: 2,
            6: 3,
        }
    
        return offsets.get(value)

    """ BIT 3 : (Uniquement Lite filaire) LED d'état allumée """
    def read_thermostat_lite_status_led(self, base_address, slave=1):
        registers = self.read_registers(
            address=base_address,
            count=27,
            slave=slave,
        )
    
        return bool(registers[26] & (1 << 3))

    """ BIT 5 : Présence ou non d’un thermostat Lite dans la zone """
    def read_thermostat_lite_present(self, base_address, slave=1):
        """Lit R26 bit 5 : présence d'un thermostat Lite dans la zone."""
        registers = self.read_registers(
            address=base_address,
            count=27,
            slave=slave,
        )
    
        return bool(registers[26] & (1 << 5))
