
###############################################################################
# Name:         Poller & SockFrame
# Usage:
# Author:       Bright Li
# Modified by:
# Created:      2019/11/04
# Version:      [0.4.3]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import socket

import struct
import math
from random import randint

from .log import getLogger
logger = getLogger()
isDebugging = False

try:
    import selectors
except ImportError:
    # print("无法载入selectors模块（当前Python版本 < v3.4），使用select版本Poller.")
    import select

    class Poller:
        POLLIN, POLLOUT, POLLERR = range(1,4)

        def __init__(self):
            self.list_read = []
            self.list_write = []
            self.list_error = []

        def close(self):
            pass

        def register(self, sock, mask):
            assert isinstance(sock, socket.socket), "Poller注册对象必须为socket，而非【{}】".format(type(sock))
            assert mask in range(1,4), "不支持的Mask取值：【{}】".format(mask)
            if mask == self.POLLIN:
                events = self.list_read
            elif mask == self.POLLOUT:
                events = self.list_write
            else:
                events = self.list_error
            events.append(sock)

        def unregister(self, sock, mask=None):
            assert isinstance(sock, socket.socket), "Poller注册对象必须为socket，而非【{}】".format(type(sock))
            assert mask in range(1,4), "不支持的Mask取值：【{}】".format(mask)

            if mask is None:
                for events in [self.list_read, self.list_write, self.list_error]:
                    if sock in events:
                        events.remove(sock)
                return
            elif mask == self.POLLIN:
                events = self.list_read
            elif mask == self.POLLOUT:
                events = self.list_write
            else:
                events = self.list_error
            events.remove(sock)

        def poll(self, timeout=None):
            tuple_events = select.select(self.list_read, self.list_write, self.list_error, timeout)
            # rlist, wlist, xlist = tuple_events
            dict_ = {}
            for index, list_event in enumerate(tuple_events):
                mask = index +1
                for event in list_event:
                    dict_[event] = mask

            if not dict_:
                raise socket.timeout
            return dict_

else:
    class Poller:
        POLLIN = selectors.EVENT_READ    # 1
        POLLOUT = selectors.EVENT_WRITE  # 2

        def __init__(self):
            self.selector = selectors.DefaultSelector()

        def close(self):
            self.selector.close()

        def register(self, sock, mask, callback=None):
            """ 这里注意params匹配关系 """
            assert isinstance(sock, socket.socket), "Poller注册对象必须为socket，而非【{}】".format(type(sock))
            self.selector.register(fileobj=sock, events=mask, data=callback)

        def unregister(self, sock):
            assert isinstance(sock, socket.socket), "Poller注册对象必须为socket，而非【{}】".format(type(sock))
            self.selector.unregister(sock)

        def modify(self, sock, mask, callback=None):
            assert isinstance(sock, socket.socket), "Poller注册对象必须为socket，而非【{}】".format(type(sock))
            self.selector.modify(fileobj=sock, events=mask, data=callback)

        # def poll(self):
        #     events = self.selector.select()
        #     for key, mask in events:
        #         callback = key.data
        #         sock = key.fileobj
        #         callback(sock, mask)

        def poll(self, timeout=None):
            """ 模拟 zmq.Poller.poll() 的返回值 """
            events = self.selector.select(timeout)
            if timeout and not events:
                raise socket.timeout  # 超时
            dict_ = {}
            for key, mask in events:
                dict_[key.fileobj] = mask
            # callback = key.data
            return dict_


from abc import ABCMeta
class SocketProxy(metaclass=ABCMeta):
    def close(self):  pass
    def bind(self, ipaddr):  pass
    def connect(self, ipaddr):  pass
    def send(self, type, data):  pass
    def recv(self):  pass
    def msg_split(self, msg):
        """ return (type, data) """
        pass

class UdpFrame(SocketProxy):  # developing
    """ 数据包结构：
        [ MsgType(4) + uuid(4) + PackIdx(2) + PackNum(2) + Data(...) ]
        最大可表示 CAPACITY * 2^^16 = 94M 的数据长度
    """
    BUFFER_SIZE = 1464
    HEADER_SIZE = struct.calcsize("!IIHH")  # 12
    CAPACITY  = BUFFER_SIZE - HEADER_SIZE

    def __init__(self, socket_=None, buf_num=5):
        if socket_ is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.socket = socket_

        # 当接收数据不足预收数据长度时，数据暂存缓冲区
        self.buffer = {}  # {uuid: {pack_idx: data} }
        self.buf_seq = []  # uuid顺序 -> 最久未更新的项，先行剔除
        self.buf_num = buf_num  # self.buffer能够存储的最大数量

    def close(self):
        self.socket.close()

    def settimeout(self, value):
        self.socket.settimeout(value)

    def connect(self, ipaddr):
        return self.socket.connect(ipaddr)

    def bind(self, ipaddr):
        self.socket.bind(ipaddr)

    def send(self, int_type, bytes_data, dest_addr=None):
        if isinstance(bytes_data, str):
            bytes_data = bytes_data.encode()

        nPack = math.ceil(len(bytes_data) / self.CAPACITY)
        if nPack == 0:  # bytes_data == b""
            nPack = 1

        # if nPack > 1:
        #     logger.debug("UdpFrame分包【{}】".format(nPack))

        pack_id = randint(0, 0xFFFFFFFF)  # 2**(8*4)

        bit_from = 0
        for pack_idx in range(nPack):
            bit_to = bit_from + self.CAPACITY
            pack_data = bytes_data[bit_from: bit_to]
            bit_from = bit_to

            data = struct.pack("!IIHH", int_type, pack_id, pack_idx, nPack)
            data += pack_data

            if dest_addr:
                self.socket.sendto(data, dest_addr)
            else:
                self.socket.send(data)
            # logger.debug("发送【{}】bytes, [{}]".format(len(data), data))

    def recv(self):
        """ return (data, addr) or None, for unfinished message """
        data_recv, addr = self.socket.recvfrom(self.BUFFER_SIZE)  # 可能丢包、重包、乱序
        # logger.debug("接收【{}】bytes".format(len(data_recv)))

        if not data_recv:
            raise ConnectionError
        if len(data_recv) < self.HEADER_SIZE:
            # raise Exception("非法的数据【{}】".format(data_recv))
            logger.debug("数据长度不足HEADER_SIZE，舍弃数据帧....")
            return
        msg_type, pack_id, pack_idx, nPack = struct.unpack("!IIHH", data_recv[:self.HEADER_SIZE])

        # 对nPack=1的直接处理（不再入栈self.buffer）
        if nPack == 1:
            return data_recv, addr

        if pack_id not in self.buf_seq:
            # 添加新的节点
            if len(self.buf_seq) >= self.buf_num:
                pop_id = self.buf_seq.pop(0)
                if isDebugging:
                    buf_item = self.buffer[pop_id]
                    logger.debug("剔除一个不完整的数据包：【{}/{}】".format(
                        len(buf_item) -3, buf_item["nPack"] ))
                del self.buffer[pop_id]

            buf_item = {}
            buf_item["addr"] = addr
            buf_item["type"] = msg_type
            buf_item["nPack"] = nPack
            self.buffer[pack_id] = buf_item
            self.buf_seq.append(pack_id)

            # logger.info("缓冲栈占用：【{}/{}】".format(len(self.buf_seq), self.buf_num))

        # 更新self.buf_seq顺序
        elif pack_id != self.buf_seq[-1]:
            self.buf_seq.remove(pack_id)
            self.buf_seq.append(pack_id)

        self.buffer[pack_id][pack_idx] = data_recv[self.HEADER_SIZE:]

        if len(self.buffer[pack_id]) == nPack +3:  # 接收完整
            # logger.debug("rebuild the UdpPack: [{}]".format(nPack))
            return self._rebuild(pack_id)
        # else:
        #     logger.debug("剩余【{}/{}】包数据未接收".format(nPack - len(self.buffer[pack_id]) +3, nPack))

    def _rebuild(self, pack_id):
        """ 重新组包 """
        buffer = self.buffer[pack_id]
        self.buf_seq.remove(pack_id)
        del self.buffer[pack_id]

        addr = buffer["addr"]
        msg_type = buffer["type"]
        nPack = buffer["nPack"]

        data = msg_type.to_bytes(4, byteorder='big') + bytes(8)
        for pack_idx in range(nPack):
            data += buffer[pack_idx]

        return data, addr

    def msg_split(self, msg):
        msg_type = msg[:4]
        msg_body = msg[self.HEADER_SIZE:]
        return msg_type, msg_body


class TcpFrame(SocketProxy):
    """ 数据包结构：
        [ MsgType(4) + LenData(4) + Data(...) ]
        最大可表示4GB的数据长度
    """
    HEADER_SIZE = struct.calcsize("!II")  # 8

    def __init__(self, socket_=None):
        if socket_ is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.socket = socket_

        # 当接收数据不足预收数据长度时，数据暂存缓冲区
        self.buffer = b""
        self.remain_size = 0

    def close(self):
        self.socket.close()

    def settimeout(self, value):
        self.socket.settimeout(value)

    def connect(self, ipaddr):
        return self.socket.connect(ipaddr)

    def bind(self, ipaddr):
        self.socket.bind(ipaddr)
        self.socket.listen(5)

    def accept(self):
        return self.socket.accept()

    def send(self, int_type, bytes_data):
        if isinstance(bytes_data, str):
            bytes_data = bytes_data.encode()
        data = struct.pack("!II", int_type, len(bytes_data))
        data += bytes_data
        self.socket.sendall(data)

    def recv(self):
        """ return data or None, for unfinished message """
        if self.remain_size == 0:
            len_fixed_data = self.HEADER_SIZE
            data_recv = self.socket.recv(len_fixed_data)
            if not data_recv:
                raise ConnectionError
            if len(data_recv) < len_fixed_data:
                raise Exception("非法的数据【{}】".format(data_recv))
            msg_type, len_data = struct.unpack("!II", data_recv)
            # if msg_type not in [UINT_HEAD_CMD, UINT_HEAD_DATA,
            #                   UINT_HEAD_ERROR, UINT_HEAD_HEART]:
            #     raise Exception("非法的数据【{}】".format(msg_type))
            if len_data == 0:
                return data_recv
            else:
                # var_data = self.socket.recv(len_data)  # 异步??
                # return data_recv + var_data
                self.remain_size = len_data
                self.buffer = data_recv
        else:
            data_recv = self.socket.recv(self.remain_size)
            if data_recv is None:
                raise ConnectionError
            self.buffer += data_recv
            self.remain_size -= len(data_recv)
            if not self.remain_size:
                msg = self.buffer
                self.buffer = b""
                return msg

    def msg_split(self, msg):
        msg_type = msg[:4]
        msg_body = msg[self.HEADER_SIZE:]
        return msg_type, msg_body


try:
    import zmq
    from collections import Iterable
except ImportError:
    print("无法载入zmq模块，故未能导入class ZmqFrame.")
    pass
else:
    ZmqPoller = zmq.Poller

    class ZmqFrame(SocketProxy):
        def __init__(self, type_, **kwargs):
            """ type_:
                    REQ/REP,
                    PUB/SUB,
                    PUSH/PULL,
                    ROUTER/DELLER,
            """
            context = zmq.Context()
            if type_ == "REQ":
                self.socket = context.socket(zmq.REQ)
            elif type_ == "REP":
                self.socket = context.socket(zmq.REP)
            elif type_ == "PUB":
                self.socket = context.socket(zmq.PUB)
            elif type_ == "SUB":
                self.socket = context.socket(zmq.SUB)
                if "topic" in kwargs:
                    topic = kwargs["topic"]
                else:
                    logger.warning("创建的ZMQ-socket未指定Topic")
                    topic = ""
                self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
            elif type_ == "PUSH":
                self.socket = context.socket(zmq.PUSH)
                self.sock_result.setsockopt(zmq.LINGER, 0)  # 如对端关闭，则放弃发送数据
            elif type_ == "PULL":
                self.socket = context.socket(zmq.PULL)
            elif type_ == "ROUTER":
                self.socket = context.socket(zmq.ROUTER)
            elif type_ == "DELLER":
                self.socket = context.socket(zmq.DELLER)

            # elif type_ == "POLLER":
            #     self.socket = zmq.Poller()
            else:
                raise Exception("无法解析的ZMQ类型：{}".format(type_))

        def close(self):
            self.socket.close()

        def bind(self, ipaddr: tuple, protocal="tcp"):
            """ 默认绑定TCP端口 """
            str_addr = "{}://{}:{}".format(protocal, *ipaddr)
            self.socket.bind(str_addr)

        def connect(self, ipaddr: tuple, protocal="tcp"):
            str_addr = "{}://{}:{}".format(protocal, *ipaddr)
            self.socket.connect(str_addr)

        def send(self, int_type, pyobj_data):
            bytes_type = int_type.to_bytes(4, byteorder='big', signed=False)
            tuple_pack = (bytes_type, pyobj_data)
            self.socket.send_pyobj(tuple_pack)

        def recv(self):
            """ return a tuple of (bytes_type, pyobj_data) """
            tuple_pack = self.socket.recv_pyobj()
            return tuple_pack

        def msg_split(self, msg: tuple):
            if not isinstance(msg, Iterable) or len(msg) != 2:
                raise Exception("非法的ZmqFrame数据包：{}".format(type(msg)))
            return msg
