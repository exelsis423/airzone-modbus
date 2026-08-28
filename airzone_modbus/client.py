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

    def read_input_registers(
        self,
        address: int,
        count: int,
        slave: int = 1,
    ) -> list[int]:
        """Lit des registres Input."""
        response = self.client.read_input_registers(
            address=address,
            count=count,
            device_id=slave,
        )

        if response.isError():
            raise RuntimeError(
                f"Erreur Modbus : {response}"
            )

        return response.registers

    # ============================================================
    # ZONE - REGISTRE R00
    # ============================================================

    def read_zone_local_ventilation(
        self,
        base: int,
        slave: int = 1,
    ):
        """Lit le bit 0 : ventilation locale."""
        value = self.read_registers(
            address=base,
            count=1,
            slave=slave,
        )[0]

        return bool(value & (1 << 0))

    def read_zone_schedule_disabled(
        self,
        base: int,
        slave: int = 1,
    ):
        """Lit le bit 1 : programmation désactivée."""
        value = self.read_registers(
            address=base,
            count=1,
            slave=slave,
        )[0]

        return bool(value & (1 << 1))

    def read_zone_state(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Lit le bit 2 : état de la zone."""
        registers = self.read_registers(
            address=base_address,
            count=1,
            slave=slave,
        )

        return bool(registers[0] & (1 << 2))

    def read_zone_speed(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Lit les bits 4-5 : vitesse."""
        registers = self.read_registers(
            address=base_address,
            count=1,
            slave=slave,
        )

        return (registers[0] >> 4) & 0b11

    def read_zone_speed_name(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Retourne le nom de la vitesse."""
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

        return names.get(
            speed,
            f"Inconnue ({speed})",
        )

    def read_zone_sleep_mode(
        self,
        base: int,
        slave: int = 1,
    ):
        """Lit les bits 6-7 : mode veille."""
        value = self.read_registers(
            address=base,
            count=1,
            slave=slave,
        )[0]

        return (value >> 6) & 0x03

    def read_zone_sleep_mode_name(
        self,
        base: int,
        slave: int = 1,
    ):
        """Retourne le nom du mode veille."""
        modes = {
            0: "Veille Off",
            1: "Veille 30",
            2: "Veille 60",
            3: "Veille 90",
        }

        return modes.get(
            self.read_zone_sleep_mode(
                base,
                slave,
            ),
            "Inconnu",
        )

    def read_zone_mode(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Lit les bits 8-11 : mode de la zone."""
        registers = self.read_registers(
            address=base_address,
            count=1,
            slave=slave,
        )

        return (registers[0] >> 8) & 0x0F

    def read_zone_mode_name(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Retourne le nom du mode."""
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

        return names.get(
            mode,
            f"Inconnu ({mode})",
        )

    def read_zone_automatic_mode(
        self,
        base: int,
        slave: int = 1,
    ):
        """Lit le bit 12 : mode automatique."""
        value = self.read_registers(
            address=base,
            count=1,
            slave=slave,
        )[0]

        return bool(value & (1 << 12))

    def read_zone_bit15(
        self,
        base: int,
        slave: int = 1,
    ):
        """Lit le bit 15."""
        value = self.read_registers(
            address=base,
            count=1,
            slave=slave,
        )[0]

        return bool(value & (1 << 15))

    # ============================================================
    # ZONE - REGISTRE R03
    # ============================================================

    def read_zone_setpoint(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Lit la consigne en dixièmes de degré Celsius."""
        registers = self.read_registers(
            address=base_address,
            count=4,
            slave=slave,
        )

        return registers[3] / 10.0
        
    def write_zone_setpoint(
            self,
            base_address: int,
            setpoint: float,
            slave: int = 1,
        ) -> None:
            """Écrit la consigne dans le registre R03."""
    
            if setpoint < 18 or setpoint > 30:
                raise ValueError(
                    f"Consigne invalide : {setpoint}"
                )
    
            if (setpoint * 2) % 1 != 0:
                raise ValueError(
                    f"Consigne invalide : {setpoint}"
                )
    
            value = int(setpoint * 10)
    
            response = self.client.write_register(
                address=base_address + 3,
                value=value,
                device_id=slave,
            )
    
            if response.isError():
                raise RuntimeError(
                    f"Erreur Modbus écriture consigne : {response}"
                )
    
        def write_zone_setpoint(
            self,
            base_address: int,
            setpoint: float,
            slave: int = 1,
        ) -> None:
            """Écrit la consigne dans le registre R03."""
    
            if setpoint < 18 or setpoint > 30:
                raise ValueError(
                    f"Consigne invalide : {setpoint}"
                )
    
            if (setpoint * 2) % 1 != 0:
                raise ValueError(
                    f"Consigne invalide : {setpoint}"
                )
    
            value = int(setpoint * 10)
    
            response = self.client.write_register(
                address=base_address + 3,
                value=value,
                device_id=slave,
            )
    
            if response.isError():
                raise RuntimeError(
                    f"Erreur Modbus écriture consigne : {response}"
                )
                
    # ============================================================
    # ZONE - REGISTRE R08
    # ============================================================

    def read_zone_temperature(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Lit la température de la sonde à distance."""
        registers = self.read_registers(
            address=base_address,
            count=9,
            slave=slave,
        )

        return registers[8] / 10.0

    # ============================================================
    # ZONE - REGISTRE R10
    # ============================================================

    def read_zone_thermostat_temperature(
        self,
        base: int,
        slave: int = 1,
    ):
        """Lit la température locale du thermostat."""
        registers = self.read_input_registers(
            address=base + 10,
            count=1,
            slave=slave,
        )

        return registers[0] / 10.0

    # ============================================================
    # ZONE - REGISTRE R14-R19
    # ============================================================

    def read_zone_name(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Lit le nom de la zone."""
        registers = self.read_registers(
            address=base_address,
            count=20,
            slave=slave,
        )

        data = bytearray()

        for value in registers[14:20]:
            data.append((value >> 8) & 0xFF)
            data.append(value & 0xFF)

        return data.split(
            b"\x00"
        )[0].decode(
            "ascii",
            errors="replace",
        )

    # ============================================================
    # ZONE - REGISTRE R26
    # ============================================================

    def read_zone_r26(
        self,
        base_address: int,
        slave: int = 1,
    ) -> int:
        """Lit le registre R26."""
        registers = self.read_registers(
            address=base_address,
            count=27,
            slave=slave,
        )

        return registers[26]

    def read_thermostat_lite_setpoint_offset(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Lit les bits 0-2 : offset thermostat Lite."""
        value = self.read_zone_r26(
            base_address,
            slave=slave,
        )

        offsets = {
            0: -3,
            1: -2,
            2: -1,
            3: 0,
            4: 1,
            5: 2,
            6: 3,
        }

        return offsets.get(value & 0b111)

    def read_thermostat_lite_status_led(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Lit le bit 3 : LED thermostat."""
        value = self.read_zone_r26(
            base_address,
            slave=slave,
        )

        return bool(value & (1 << 3))

    def read_thermostat_lite_present(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Lit le bit 5 : présence thermostat Lite."""
        value = self.read_zone_r26(
            base_address,
            slave=slave,
        )

        return bool(value & (1 << 5))

    def _modify_zone_r26(
        self,
        base_address: int,
        mask: int,
        value: int,
        slave: int = 1,
    ) -> None:
        """Modifie certains bits de R26 sans toucher aux autres."""

        current = self.read_zone_r26(
            base_address,
            slave=slave,
        )

        new_value = (
            (current & ~mask)
            | (value & mask)
        )

        response = self.client.write_register(
            address=base_address + 26,
            value=new_value,
            device_id=slave,
        )

        if response.isError():
            raise RuntimeError(
                f"Erreur Modbus écriture zone R26 : {response}"
            )

    def write_thermostat_lite_setpoint_offset(
        self,
        base_address: int,
        offset: int,
        slave: int = 1,
    ) -> None:
        """Modifie les bits 0-2 de R26 pour l'offset thermostat Lite."""

        if offset not in (-3, -2, -1, 0, 1, 2, 3):
            raise ValueError(
                f"Offset thermostat invalide : {offset}"
            )

        offset_values = {
            -3: 0,
            -2: 1,
            -1: 2,
            0: 3,
            1: 4,
            2: 5,
            3: 6,
        }

        self._modify_zone_r26(
            base_address,
            mask=0b111,
            value=offset_values[offset],
            slave=slave,
        )

    def write_thermostat_lite_status_led(
        self,
        base_address: int,
        enabled: bool,
        slave: int = 1,
    ) -> None:
        """Active ou désactive le bit 3 de R26."""

        self._modify_zone_r26(
            base_address,
            mask=(1 << 3),
            value=(1 << 3) if enabled else 0,
            slave=slave,
        )

    # ============================================================
    # ZONE - REGISTRE R31
    # ============================================================

    def read_zone_humidity(
        self,
        base_address: int,
        slave: int = 1,
    ):
        """Lit l'humidité."""
        registers = self.read_registers(
            address=base_address,
            count=32,
            slave=slave,
        )

        return registers[31]

    # ============================================================
    # MACHINE - REGISTRE R00
    # ============================================================

    def read_machine_register_0(
        self,
        slave: int = 1,
    ):
        """Lit le registre R00 de la machine."""
        registers = self.read_registers(
            address=0,
            count=1,
            slave=slave,
        )

        return registers[0]

    def read_machine_mode(
        self,
        slave: int = 1,
    ):
        """Lit le mode de fonctionnement de la machine."""
        value = self.read_machine_register_0(slave)
        return value & 0x01FF

    def read_machine_mode_name(
        self,
        slave: int = 1,
    ):
        """Retourne le nom du mode machine."""
        modes = {
            0: "Arrêt",
            1: "Refroidissement",
            2: "Chauffage rayonnant",
            3: "Ventilation",
            4: "Chauffage air",
            5: "Chauffage",
            6: "Sec",
            7: "Chaud auxiliaire",
            8: "Refroidissement rayonnant",
            9: "Refroidissement",
            258: "Chauffage",
        }

        value = self.read_machine_mode(slave)

        return modes.get(
            value,
            f"Inconnu ({value})",
        )

    def read_machine_speed(
        self,
        slave: int = 1,
    ):
        """Lit les bits 9-10 : vitesse machine."""
        value = self.read_machine_register_0(slave)
        return (value >> 9) & 0b11

    def read_machine_speed_name(
        self,
        slave: int = 1,
    ):
        """Retourne le nom de la vitesse machine."""
        speeds = {
            0: "Automatique",
            1: "Faible",
            2: "Moyenne",
            3: "Élevée",
        }

        value = self.read_machine_speed(slave)

        return speeds.get(
            value,
            f"Inconnu ({value})",
        )

    # ============================================================
    # MACHINE - REGISTRE R09
    # ============================================================

    def read_machine_zones(
        self,
        slave: int = 1,
    ):
        """Lit les zones présentes."""
        registers = self.read_registers(
            address=9,
            count=1,
            slave=slave,
        )

        value = registers[0]

        return [
            zone
            for zone in range(1, 17)
            if value & (1 << (zone - 1))
        ]

    def read_machine_zone_bases(
        self,
        slave: int = 1,
    ):
        """Retourne les adresses de base des zones."""
        zones = self.read_machine_zones(slave)

        return [
            zone * 256
            for zone in zones
        ]

    # ============================================================
    # MACHINE - ÉCRITURE R00
    # ============================================================

    def write_machine_mode(
        self,
        mode,
        slave: int = 1,
    ):
        """Modifie le mode de fonctionnement de la machine."""
        current = self.read_machine_register_0(slave)

        new_value = (
            (current & ~0x01FF)
            | (mode & 0x01FF)
        )

        response = self.client.write_register(
            address=0,
            value=new_value,
            device_id=slave,
        )

        if response.isError():
            raise RuntimeError(
                "Erreur Modbus écriture machine mode : "
                f"{response}"
            )

    def write_machine_speed(
        self,
        speed,
        slave: int = 1,
    ):
        """Modifie la vitesse de ventilation de la machine."""
        current = self.read_machine_register_0(slave)

        new_value = (
            (current & ~(0b11 << 9))
            | ((speed & 0b11) << 9)
        )

        response = self.client.write_register(
            address=0,
            value=new_value,
            device_id=slave,
        )

        if response.isError():
            raise RuntimeError(
                "Erreur Modbus écriture machine vitesse : "
                f"{response}"
            )

    # ============================================================
    # ZONE - ÉCRITURE R00
    # ============================================================

    def write_zone_r00(
        self,
        base_address: int,
        value: int,
        slave: int = 1,
    ) -> None:
        """Écrit le registre R00 complet d'une zone."""

        response = self.client.write_register(
            address=base_address,
            value=value,
            device_id=slave,
        )

        if response.isError():
            raise RuntimeError(
                f"Erreur Modbus écriture zone R00 : {response}"
            )

    def _modify_zone_r00(
        self,
        base_address: int,
        mask: int,
        value: int,
        slave: int = 1,
    ) -> None:
        """Modifie certains bits de R00 sans toucher aux autres."""

        current = self.read_registers(
            address=base_address,
            count=1,
            slave=slave,
        )[0]

        new_value = (
            (current & ~mask)
            | (value & mask)
        )

        self.write_zone_r00(
            base_address,
            new_value,
            slave=slave,
        )

    def write_zone_schedule_disabled(
        self,
        base_address: int,
        enabled: bool,
        slave: int = 1,
    ) -> None:
        """Active ou désactive les programmations horaires."""

        self._modify_zone_r00(
            base_address,
            mask=(1 << 1),
            value=(1 << 1) if enabled else 0,
            slave=slave,
        )

    def write_zone_state(
        self,
        base_address: int,
        state: bool,
        slave: int = 1,
    ) -> None:
        """Active ou désactive la zone."""

        self._modify_zone_r00(
            base_address,
            mask=(1 << 2),
            value=(1 << 2) if state else 0,
            slave=slave,
        )

    def write_zone_speed(
        self,
        base_address: int,
        speed: int,
        slave: int = 1,
    ) -> None:
        """Modifie la vitesse de ventilation de la zone."""

        if speed not in (0, 1, 2, 3):
            raise ValueError(
                f"Vitesse de zone invalide : {speed}"
            )

        self._modify_zone_r00(
            base_address,
            mask=(0b11 << 4),
            value=(speed << 4),
            slave=slave,
        )

    def write_zone_sleep_mode(
        self,
        base_address: int,
        sleep_mode: int,
        slave: int = 1,
    ) -> None:
        """Modifie le mode veille de la zone."""

        if sleep_mode not in (0, 1, 2, 3):
            raise ValueError(
                f"Mode veille de zone invalide : {sleep_mode}"
            )

        self._modify_zone_r00(
            base_address,
            mask=(0b11 << 6),
            value=(sleep_mode << 6),
            slave=slave,
        )

    def write_zone_mode(
        self,
        base_address: int,
        mode: int,
        slave: int = 1,
    ) -> None:
        """Modifie le mode de fonctionnement de la zone."""

        if mode not in (0, 1, 3, 5, 6):
            raise ValueError(
                f"Mode de zone invalide : {mode}"
            )

        self._modify_zone_r00(
            base_address,
            mask=(0x0F << 8),
            value=(mode << 8),
            slave=slave,
        )

    def write_zone_automatic_mode(
        self,
        base_address: int,
        enabled: bool,
        slave: int = 1,
    ) -> None:
        """Active ou désactive le mode automatique."""

        self._modify_zone_r00(
            base_address,
            mask=(1 << 12),
            value=(1 << 12) if enabled else 0,
            slave=slave,
        )

