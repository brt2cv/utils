# encoding: utf-8

###############################################################################
# Name:         protocal-base
# Usage:
# Author:       Bright Li
# Modified by:
# Created:      2019/11/11
# Version:      [0.1.1]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import json

def byte2int(bytes_data):
    value = int.from_bytes(bytes_data, byteorder='big', signed=False)
    return value

def int2bytes(nInt, length):
    byte = nInt.to_bytes(length, byteorder='big', signed=False)
    return byte

class Header:
    """ 包头共计8byte，前4位为类型，后4位表示数据长度 """
    BYTE_HEART = bytes([0xa0, 0x3f, 0x3f, 0xa0])  # \xa0??\xa0
    UINT_HEART = byte2int(BYTE_HEART)
    BYTE_ERROR = bytes([0xb0, 0x3f, 0x3f, 0xb0])  # \xb0??\xb0
    UINT_ERROR = byte2int(BYTE_ERROR)

    BYTE_CMD   = bytes([0xa1, 0x3d, 0x3d, 0xa1])  # \xa1==\xa1
    UINT_CMD   = byte2int(BYTE_CMD)
    BYTE_DATA  = bytes([0xa2, 0x3d, 0x3d, 0xa2])  # \xa2==\xa2
    UINT_DATA  = byte2int(BYTE_DATA)


def dict2json(msg: dict):
    """ return a bytes-like data """
    json_msg = json.dumps(msg)
    bytes_msg = json_msg.encode()
    return bytes_msg

def json2dict(msg: bytes):
    """ return a dict-like data """
    str_msg = msg.decode()
    dict_msg = json.loads(str_msg)
    return dict_msg

#####################################################################

class IProtocal:
    def load_proxy(self, sock_proxy):
        self.sock = sock_proxy

    def send_heart(self, sock1addr=None):pass
    def send_error(self, reason, sock1addr=None):pass
    def check_error(self, data):pass
    def check_heart(self, data):pass
    def reply(self, msg: bytes, sock1addr=None):pass
    def parse_reply(self, msg: bytes):pass
    def reply_conn_break(self, socket1addr):
        """ 当客户端断开连接时的响应函数
            用于执行Protocal实例中的清理工作
            socket1addr:
                - UDP: raw_socket
                - TCP: addr like ("127.0.0.1", 55331)
        """
        pass


class TransBase(IProtocal):
    """ 简单通讯协议Demo
    """
    def __init__(self):
        super().__init__()

    def _send(self, msg_type, msg_body, sock1addr=None):
        """ 由于TcpFrame与UdpFrame的send函数并不相同，
            而Trans本身并不区分Tcp/Udp，故需要提供兼容的send/recv接口
        """
        if sock1addr is None:
            self.sock.send(msg_type, msg_body)
        elif isinstance(sock1addr, tuple):
            addr = sock1addr
            self.sock.send(msg_type, msg_body, addr)
        else:
            sock = sock1addr
            sock.send(msg_type, msg_body)

    def send_cmd(self, json_msg, sock1addr=None):
        if isinstance(json_msg, dict):
            json_msg = dict2json(json_msg)
        self._send(Header.UINT_CMD, json_msg, sock1addr)

    def send_data(self, data, sock1addr=None):
        self._send(Header.UINT_DATA, data, sock1addr)

    def send_heart(self, sock1addr=None):
        self._send(Header.UINT_HEART, b"", sock1addr)

    def send_error(self, reason, sock1addr=None):
        self._send(Header.UINT_ERROR, reason, sock1addr)

    def _check(self, data, check_type):
        msg_type, _ = self.sock.msg_split(data)
        return msg_type == check_type

    def check_error(self, data):
        return self._check(data, Header.BYTE_ERROR)

    def check_heart(self, data):
        return self._check(data, Header.BYTE_HEART)

    def check_cmd(self, data):
        return self._check(data, Header.BYTE_CMD)

    def check_data(self, data):
        return self._check(data, Header.BYTE_DATA)
