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

    def read_zone_name(self, base_address, slave=1):
        """
        Lit le nom d'une zone.
    
        Le nom est stocké dans R14 à R17,
        avec deux caractères ASCII par registre.
        """
        registers = self.read_registers(
            address=base_address,
            count=18,
            slave=slave,
        )
    
        data = bytearray()
    
        for value in registers[14:18]:
            data.append((value >> 8) & 0xFF)
            data.append(value & 0xFF)
    
        return data.split(b"\x00")[0].decode("ascii", errors="replace")

    def read_zone_setpoint(self, base_address, slave=1):
        """
        Lit la consigne d'une zone.
    
        R03 = consigne en dixièmes de degré Celsius.
        """
        registers = self.read_registers(
            address=base_address,
            count=4,
            slave=slave,
        )
    
        return registers[3] / 10.0
