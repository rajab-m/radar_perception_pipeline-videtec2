import socket
import time
import msgpack
import crcmod.predefined
import numpy as np


class RadarSimulator:
    def __init__(
        self,
        host="127.0.0.1",
        port=65432,
        range_bins=128,
        doppler_bins=256,
        chunk_size=1400
    ):

        self.host = host
        self.port = port
        self.chunk_size = chunk_size

        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        self.magic_word = b"MAGICWORD"
        self.sequence = 1

        self.range_bins = range_bins
        self.doppler_bins = doppler_bins

        self.HEADERSIZE = 30
        self.PACKET = 30
        self.CRC = 10
        self.STAMP = 20

        self.crc16 = crcmod.predefined.mkPredefinedCrcFun("crc-16")

    # -------------------------------------------------
    # Synthetic radar data
    # -------------------------------------------------
    def create_rd_map(self):

        return np.random.randint(
            0,
            4000,
            size=(self.range_bins, self.doppler_bins),
            dtype=np.uint16
        )

    def create_detections(self, n=5):

        dets = []

        for _ in range(n):

            dets.append([
                np.random.randint(5, self.range_bins - 5),     # range
                np.random.randint(-100, 100),                  # doppler
                np.random.randint(100, 3000),                  # magnitude
                np.random.randint(-45, 45),                    # azimuth
                np.random.randint(-10, 10)                     # elevation
            ])

        return dets

    # -------------------------------------------------
    # Build payload (matches receiver expectation)
    # -------------------------------------------------
    def build_measurements(self):

        rd_map = self.create_rd_map()
        detections = self.create_detections()

        payload = b""

        # RD map
        payload += rd_map.astype(">u2").tobytes()

        # number of detections
        payload += len(detections).to_bytes(2, "big")

        # detections
        for d in detections:
            payload += np.array(d, dtype=">h").tobytes()

        return payload

    # -------------------------------------------------
    # Build full packet (magic + header + msgpack)
    # -------------------------------------------------
    def build_packet(self):

        timestamp = int(time.time() * 1000)

        measurements = self.build_measurements()

        body = {
            "measurements": measurements,
            "data sending time": time.time()
        }

        packed = msgpack.packb(body, use_bin_type=True)

        crc = self.crc16(packed)

        header = (
            str(len(packed)).ljust(self.HEADERSIZE).encode()
            + str(self.sequence).ljust(self.PACKET).encode()
            + str(crc).ljust(self.CRC).encode()
            + str(timestamp).ljust(self.STAMP).encode()
        )

        self.sequence += 1

        return self.magic_word + header + packed

    # -------------------------------------------------
    # CRITICAL FIX: chunked UDP sending
    # -------------------------------------------------
    def send_chunked(self, packet: bytes):

        total = len(packet)
        offset = 0

        while offset < total:

            chunk = packet[offset:offset + self.chunk_size]

            self.sock.sendto(chunk, (self.host, self.port))

            offset += self.chunk_size

    # -------------------------------------------------
    # main loop
    # -------------------------------------------------
    def run(self, rate_hz=5):

        period = 1.0 / rate_hz

        print(f"Sending to {self.host}:{self.port}")

        try:

            while True:

                packet = self.build_packet()

                self.send_chunked(packet)

                print(f"Sent packet {self.sequence - 1}")

                time.sleep(period)

        except KeyboardInterrupt:

            print("\nStopped simulator")
            self.sock.close()


if __name__ == "__main__":

    sim = RadarSimulator(
        host="127.0.0.1",
        port=65432
    )

    sim.run(rate_hz=5)