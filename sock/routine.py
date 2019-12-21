# encoding: utf-8

###############################################################################
# Name:         routine
# Usage:
# Author:       Bright Li
# Modified by:
# Created:      2019/12/10
# Version:      [0.4.3]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import socket
from time import sleep
from threading import Thread, Event

from util.base import Deletable
from util.socket import TcpFrame, UdpFrame
from util.socket import Poller

from util.log import getLogger
logger = getLogger()


TIMEOUT_RECV = 2        # 接收数据超时
TIMEOUT_SHUTDOWN = 30   # 最大等待超时
HEART_BEAT_PERIOD = 2   # 心跳间隔时长
HEART_LISTEN_PERIOD = 1 # 心跳检测时长


class Routine(Thread):
    def __init__(self):
        """ self.sock: SocketProxy对象(TcpFrame/UdpFrame) """
        super().__init__()
        # self.sock = None
        self.isRunning = False  # or threading.Event()
        self.runHeart = False

    def set_protocal(self, protocal):
        """ protocal: TransBase对象 """
        protocal.load_proxy(self.sock)
        self.protocal = protocal

    def run(self):
        """ listen 监听循环 """
        self.isRunning = True
        while self.isRunning:
            self.recv_msg()

    # def recv_msg(self):
    #     pass

    listen = Thread.start
    """ 启动线程 """

    # def listen(self, runHeart: bool, callback=None):
    #     """ 使用listen，可以提供更多的可选参数 """
    #     self.func_clean = callback
    #     self.runHeart = runHeart
    #     self.start()

    def stop(self):
        """ 仅限于self线程外部调用 """
        if self.isRunning:
            self.isRunning = False

        # if self.runHeart:
        #     logger.debug("回收心跳线程...")
        #     self.tid_heart.join()
        #     self.runHeart = False

        if self.is_alive():
            logger.debug("回收监听线程...")
            self.join()  # 等待listen退出循环，回收自身线程

        logger.debug("关闭socket")
        self.sock.close()


# Routine的子类——Server/Client的区别仅仅在于谁主动发送心跳

class Client(Routine):
    def __init__(self):
        super().__init__()

    def heart_beat(self):
        """ 发送心跳 """
        pass

class Server(Routine):
    def __init__(self):
        super().__init__()
        # self.sock = None

    def heart_echo(self):
        """ 回复心跳 """
        pass

    def accept_client(self):
        pass

    def close_client(self, addr):
        pass


#####################################################################

class UdpServer(Server):
    def __init__(self, port):
        super().__init__()

        self.sock = UdpFrame(buf_num=10)
        self.sock.bind(("", port))
        self.sock.settimeout(TIMEOUT_RECV)

        self.isRunning = False
        self.tid_heart = None

    def heart_echo(self):
        """ 启动线程实现对每个链接的心跳超时判断 """
        self.dict_clnt = {}  # address: {heart}

        def timeout_count():
            while self.isRunning:
                sleep(HEART_LISTEN_PERIOD)

                list_closing = []
                for address, dict_clnt_info in self.dict_clnt.items():
                    dict_clnt_info["heart"] += HEART_LISTEN_PERIOD
                    if dict_clnt_info["heart"] > TIMEOUT_SHUTDOWN:
                        list_closing.append(address)

                for address in list_closing:
                    self.close_client(address)
            logger.info("心跳监听已终止")

        self.tid_heart = Thread(target=timeout_count)
        # self.tid_heart.setDaemon(True)
        self.tid_heart.start()

    def accept_client(self, address):
        self.dict_clnt[address] = {"heart": 0}
        logger.debug("新增客户端连接：【{}】".format(self.dict_clnt))

    def close_client(self, address):
        logger.debug("关闭一个客户端连接【{}】".format(address))
        del self.dict_clnt[address]
        self.protocal.reply_conn_break(address)  # 协议栈清理

    def listen(self, runHeart=False):
        """ UDP默认不启动heart-beat """
        self.runHeart = runHeart
        self.start()

    def run(self):
        self.isRunning = True
        if self.runHeart:
            logger.debug("UDP启动心跳线程...")
            self.heart_echo()

        while self.isRunning:
            try:
                self.recv_msg()

            except socket.timeout:
                pass

            except (ConnectionError, OSError):
                logger.error("ConnectionError")

            except Exception as e:
                from traceback import print_exc
                print_exc()
                logger.critical(e)
                assert 0, e

    def recv_msg(self):
        # 接收一整条数据
        rc = self.sock.recv()  # 阻塞 + 超时
        if rc is None:  # 消息未接收完整
            return
        else:
            data, addr = rc
        # logger.debug("Recv Msg... [{}] from [{}]".format(data, addr))

        if self.runHeart:
            if addr not in self.dict_clnt:
                self.accept_client(addr)

        _, body = self.sock.msg_split(data)
        # 区分指令、心跳、数据
        if self.protocal.check_heart(data):
            # logger.debug("接收到心跳")
            if self.runHeart:
                self.dict_clnt[addr]["heart"] = 0
                # heart_echo
                self.protocal.send_heart(addr)
        elif self.protocal.check_error(data):
            reason = body.decode()
            logger.error("Except: {}".format(reason))
        else:
            self.protocal.reply(data, addr)

    def stop(self):
        """ 仅限于self线程外部调用 """
        if self.isRunning:
            self.isRunning = False

        if self.runHeart:
            logger.debug("回收心跳线程...")
            self.tid_heart.join()
            self.runHeart = False

        if self.is_alive():
            logger.debug("回收监听线程...")
            self.join()  # 等待listen退出循环，回收自身线程

        logger.debug("关闭socket")
        self.sock.close()


class UdpClient(Client):
    def __init__(self, ipaddr):
        super().__init__()

        self.sock = UdpFrame()
        self.sock.connect(ipaddr)
        self.sock.settimeout(TIMEOUT_RECV)

        self.isRunning = False
        self.tid_heart = None
        self.func_clean = None

    def heart_beat(self):
        """ 利用定时器发送心跳 """
        def send_heart():
            while self.isRunning:
                self.protocal.send_heart()
                sleep(HEART_BEAT_PERIOD)
            logger.info("心跳循环已结束")

        self.tid_heart = Thread(target=send_heart)
        # self.tid_heart.setDaemon(True)
        self.tid_heart.start()

    def listen(self, callback=None, runHeart=False):
        """ UDP默认不启动heart-beat """
        self.runHeart = runHeart
        self.func_clean = callback
        self.start()

    def run(self):
        self.isRunning = True
        self.timeout_shutdown = 0
        if self.runHeart:
            logger.debug("UDP启动心跳线程...")
            self.heart_beat()

        while self.isRunning:
            self.recv_msg()

        # 清理回调
        self.isRunning = False
        if self.func_clean is not None:
            self.func_clean()

    def recv_msg(self):
        try:
            rc = self.sock.recv()  # 阻塞 + 超时
            if rc is None:  # 消息未接收完整
                return
            else:
                data, addr = rc
            self._parse_msg(data)

        except socket.timeout:
            if self.runHeart:
                self.timeout_shutdown += TIMEOUT_RECV
                # logger.debug("超时计数【{}】".format(self.timeout_shutdown))

                if self.timeout_shutdown >= TIMEOUT_SHUTDOWN:
                    logger.error("心跳超时")
                    self.isRunning = False

        except ConnectionError:
            logger.error("服务器宕机")
            self.isRunning = False
            # raise AssertionError("服务器宕机")  # 委托回调 ??

        except OSError:
            # OSError: [WinError 10038] 在一个非套接字上尝试了一个操作
            logger.error("UDP对端已断开连接")
            self.isRunning = False

    def _parse_msg(self, data):
        # 区分指令、心跳、数据
        _, body = self.sock.msg_split(data)
        if self.protocal.check_heart(data):
            # logger.debug("接收到心跳返回")
            self.timeout_shutdown = 0
        elif self.protocal.check_error(data):
            reason = body.decode()
            logger.error("Except:【{}】".format(reason))
        else:
            self.protocal.parse_reply(data)

    def stop(self):
        """ 仅限于self线程外部调用 """
        if self.isRunning:
            self.isRunning = False

        if self.runHeart:
            logger.debug("回收心跳线程...")
            self.tid_heart.join()
            self.runHeart = False

        if self.is_alive():
            logger.debug("回收监听线程...")
            self.join()  # 等待listen退出循环，回收自身线程

        logger.debug("关闭socket")
        self.sock.close()


#####################################################################

class TcpServer(Server):
    def __init__(self, port):
        super().__init__()

        self.sock = TcpFrame()
        self.sock.bind(("", port))

        self.dict_clnt = {}  # socket: {heart, sock_proxy}
        self.isRunning = False

    def heart_echo(self):
        """ 启动线程实现对每个链接的心跳超时判断 """
        def timeout_count():
            while self.isRunning:
                sleep(HEART_LISTEN_PERIOD)

                list_closing = []  # 超时的TCP连接
                for sock, dict_clnt_info in self.dict_clnt.items():
                    dict_clnt_info["heart"] += HEART_LISTEN_PERIOD
                    if dict_clnt_info["heart"] > TIMEOUT_SHUTDOWN:
                        list_closing.append(sock)

                for sock in list_closing:
                    self.close_client(sock)
            logger.info("心跳监听已终止")

        self.tid_heart = Thread(target=timeout_count)
        # self.tid_heart.setDaemon(True)
        self.tid_heart.start()

    def accept_client(self):
        raw_sock, addr = self.sock.accept()
        self.poller.register(raw_sock, Poller.POLLIN)
        self.dict_clnt[raw_sock] = {"heart": 0, "proxy": TcpFrame(raw_sock)}
        logger.debug("新增客户端连接：【{}】".format(self.dict_clnt))

    def close_client(self, raw_sock):
        address = raw_sock.getpeername()
        logger.debug("关闭一个客户端连接【{}】".format(address))
        self.poller.unregister(raw_sock)
        del self.dict_clnt[raw_sock]
        raw_sock.close()
        self.protocal.reply_conn_break(raw_sock)  # 协议栈清理

    def listen(self, runHeart=True):
        """ TCP默认开启心跳 """
        self.runHeart = runHeart
        self.start()

    def run(self):
        """ 多路复用，接受消息 """
        self.isRunning = True
        if self.runHeart:
            self.heart_echo()

        # poller create...
        sock_server = self.sock.socket
        self.poller = Poller()
        self.poller.register(sock_server, Poller.POLLIN)

        while self.isRunning:
            try:
                socks = self.poller.poll(TIMEOUT_RECV)  # 阻塞，用于响应退出指令 ??
                if socks.get(sock_server) == Poller.POLLIN:
                    self.accept_client()
                    del socks[sock_server]

                for raw_sock, status in socks.items():
                    if status == Poller.POLLIN:
                        self.recv_msg(raw_sock)
                    else:
                        raise Exception("敬请期待【{}, pollin/{}】".format(raw_sock, status))

            except socket.timeout:
                pass

            except (ConnectionError, OSError):
                self.close_client(raw_sock)

        # 退出循环
        self.poller.close()

    def recv_msg(self, raw_sock):
        # logger.debug("接收到客户端请求...")
        sock = self.dict_clnt[raw_sock]["proxy"]
        data = sock.recv()  # 阻塞
        if data is None:  # 数据尚未完整接收
            return
        # logger.debug("Recv Msg >> [{} ... ] from [{}]".format(data[:30], sock))

        _, body = self.sock.msg_split(data)
        # 区分指令、心跳、数据
        if self.protocal.check_heart(data):
            # logger.debug("接收到心跳")
            self.dict_clnt[raw_sock]["heart"] = 0
            # heart_echo
            self.protocal.send_heart(sock)
        elif self.protocal.check_error(data):
            reason = body.decode()
            logger.error("Except: {}".format(reason))
        else:
            self.protocal.reply(data, sock)

    def stop(self):
        """ 仅限于self线程外部调用 """
        if self.isRunning:
            self.isRunning = False

        if self.runHeart:
            logger.debug("回收心跳线程...")
            self.tid_heart.join()
            self.runHeart = False

        if self.is_alive():
            logger.debug("回收监听线程...")
            self.join()  # 等待listen退出循环，回收自身线程

        logger.debug("关闭socket")
        self.sock.close()


class TcpClient(Client):
    """ 客户端是socket的载体，维持心跳和多路复用的监听；
        实际数据发送和指令控制，直接使用协议接口。
    """
    def __init__(self, ipaddr):
        super().__init__()

        self.sock = TcpFrame()
        self.sock.connect(ipaddr)

        self.isRunning = False
        self.func_clean = None

    def heart_beat(self):
        """ 利用定时器发送心跳 """
        def send_heart():
            try:
                while self.isRunning:
                    self.protocal.send_heart()
                    sleep(HEART_BEAT_PERIOD)
            except ConnectionError:
                # self.isRunning = False  # 仅限主线程改写isRunning状态
                pass
            logger.info("心跳循环已结束")

        self.tid_heart = Thread(target=send_heart)
        logger.debug("心跳线程已启动")
        # self.tid_heart.setDaemon(True)
        self.tid_heart.start()

    def listen(self, callback=None, runHeart=True):
        """ TCP默认开启心跳 """
        self.runHeart = runHeart
        self.func_clean = callback
        self.start()

    def run(self):
        self.isRunning = True
        self.timeout_shutdown = 0
        if self.runHeart:
            self.heart_beat()

        raw_sock = self.sock.socket
        self.poller = Poller()
        self.poller.register(raw_sock, Poller.POLLIN)

        while self.isRunning:
            self.recv_msg()

        # 退出循环
        self.poller.close()

        # 清理回调
        self.isRunning = False
        if self.func_clean is not None:
            self.func_clean()

        # UDP超时后，关闭socket，禁止继续发送数据
        self.sock.close()

    def recv_msg(self):
        try:
            socks = self.poller.poll(TIMEOUT_RECV)
            # if raw_sock in socks:
            data = self.sock.recv()  # 阻塞
            if data is None:  # 数据尚未完整接收
                return
            # logger.debug("Recv Msg >> [{} ... ] from server".format(data[:30]))
            self._parse_msg(data)

        except socket.timeout:
            self.timeout_shutdown += TIMEOUT_RECV
            # logger.debug("超时计数【{}】".format(self.timeout_shutdown))

            if self.timeout_shutdown >= TIMEOUT_SHUTDOWN:
                logger.error("心跳超时")
                self.isRunning = False

        except ConnectionError:
            logger.error("服务器宕机")
            self.isRunning = False
            # raise AssertionError("服务器宕机")  # 委托回调 ??

        except OSError:
            # OSError: [WinError 10038] 在一个非套接字上尝试了一个操作
            logger.error("TCP对端已断开连接")
            self.isRunning = False

    def _parse_msg(self, data):
        # 区分指令、心跳、数据
        _, body = self.sock.msg_split(data)
        if self.protocal.check_heart(data):
            # logger.debug("接收到心跳返回")
            self.timeout_shutdown = 0
        elif self.protocal.check_error(data):
            reason = body.decode()
            logger.error("Except:【{}】".format(reason))
        else:
            self.protocal.parse_reply(data)

    def recv_whole(self):
        while True:
            data = self.sock.recv()
            if data:
                # logger.debug("Recv Msg >> [{} ... ] from server".format(data[:30]))
                self._parse_msg(data)
                break

    def stop(self):
        """ 仅限于self线程外部调用 """
        if self.isRunning:
            self.isRunning = False

        if self.runHeart:
            logger.debug("回收心跳线程...")
            self.tid_heart.join()
            self.runHeart = False

        if self.is_alive():
            logger.debug("回收监听线程...")
            self.join()  # 等待listen退出循环，回收自身线程

        logger.debug("关闭socket")
        self.sock.close()

#####################################################################

try:
    from util.socket import ZmqFrame, ZmqPoller
except ImportError:
    print("无法载入zmq模块，故未能导入class ZmqServer/ZmqClient.")
    pass
else:
    class ZmqServer(Routine):
        """ ZmqServer仅仅作为示例模板，且不包含心跳包的管理（由ZMQ自管理） """
        def __init__(self, port):
            super().__init__()

            self.sock = ZmqFrame("REP")
            self.sock.bind(("*", port))

        def run(self):
            self.isRunning = True

            sock_server = self.sock.socket
            poller = ZmqPoller()
            poller.register(sock_server, 1)

            TIMEOUT_RECV_ = TIMEOUT_RECV * 1000
            while self.isRunning:
                socks = dict(poller.poll(TIMEOUT_RECV_))  # 超时，用于响应退出指令 ??
                if not socks:
                    # logger.debug("Poller超时...")
                    continue
                elif socks.get(sock_server) == 1:
                    self.recv_msg()
                else:
                    raise Exception("未解析poll --> socket: 【{}】".format(socks))

            # poller.close()  # zmq.Poller() 无需处理关闭 ??

        def recv_msg(self):
            """ 阻塞模式 """
            data = self.sock.recv()
            self.protocal.reply(data)


    class ZmqClient:
        """ 这里，ZmqClient并未继承于Routine：
            Routine设计模型为收发异步，而ZMQ的Request模型则需要同步处理
            故而，ZmqClient无法与Routine保持统一……
        """
        def __init__(self, ipaddr):
            self.sock = ZmqFrame("REQ")
            self.sock.connect(ipaddr)

        set_protocal = Routine.set_protocal

        # def request(self, command):
        #     self.protocal.send_cmd(command)
        #     data = self.sock.recv()
        #     self.protocal.parse_reply(data)

        def listen(self, callback):
            pass

        def stop(self):
            self.sock.close()
