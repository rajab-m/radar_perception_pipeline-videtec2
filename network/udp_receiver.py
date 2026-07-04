import socket
import crcmod.predefined
import msgpack

from utils.sync import find_sync_word


class UDPReceiver:

    def __init__(self):

        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        self.sock.bind(
            ("0.0.0.0",65432)
        )

        self.magic_word=b"MAGICWORD"

        self.buffer=b""

        self.BUFFER_SIZE=65500

        self.HEADERSIZE=30
        self.PACKET=30
        self.CRC=10
        self.STAMP=20


    def receive(self):

        while True:

            chunk,_=self.sock.recvfrom(
                self.BUFFER_SIZE
            )

            self.buffer+=chunk

            idx=find_sync_word(
                self.buffer,
                self.magic_word
            )

            if idx==-1:
                continue

            self.buffer=self.buffer[
                idx+len(self.magic_word):
            ]

            header_size=(
                self.HEADERSIZE
                +self.PACKET
                +self.CRC
                +self.STAMP
            )

            if len(self.buffer)<header_size:
                continue

            header=self.buffer[:header_size]

            self.buffer=\
                self.buffer[header_size:]

            msg_len=int(
                header[
                :self.HEADERSIZE
                ].decode().strip()
            )

            crc=int(
                header[
                self.HEADERSIZE
                +self.PACKET:
                self.HEADERSIZE
                +self.PACKET
                +self.CRC
                ].decode().strip()
            )

            while len(self.buffer)<msg_len:

                chunk,_=self.sock.recvfrom(
                    self.BUFFER_SIZE
                )

                self.buffer+=chunk

            msg=self.buffer[:msg_len]

            self.buffer=self.buffer[msg_len:]

            crc16=crcmod.predefined\
                .mkPredefinedCrcFun(
                    "crc-16"
                )

            if crc16(msg)!=crc:
                continue

            return msgpack.unpackb(
                msg,
                strict_map_key=False
            )