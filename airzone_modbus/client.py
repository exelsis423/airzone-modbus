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
            slave=slave,
        )

        if response.isError():
            raise RuntimeError(
                f"Erreur Modbus : {response}"
            )

        return response.registers
