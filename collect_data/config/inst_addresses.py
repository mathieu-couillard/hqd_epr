from dataclasses import dataclass

@dataclass
class InstrumentAddresses:
    vna: str = "TCPIP0::K-E5071C-33486.local::inst0::INSTR"
    mag_x: str = "TCPIP::192.168.0.113::7180::SOCKET"
    mag_y: str = "TCPIP::192.168.0.114::7180::SOCKET"
    mag_z: str = "TCPIP::192.168.0.115::7180::SOCKET"
    qm: str = "192.168.88.10"
    spa: str = "TCPIP0::K-N9010A-70675.local::inst0::INSTR"
    gs200_1: str = "TCPIP::192.168.0.125::INSTR"
    gs200_2: str = "TCPIP::192.168.0.126::INSTR"
    anti_helmholtz: str = "TCPIP::192.168.0.127::INSTR"
    mw_source: str = "192.168.0.12"
