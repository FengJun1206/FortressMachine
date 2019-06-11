import socket
import sys
import time
from paramiko.py3compat import u

try:
    import termios  # 终端
    import tty

    has_termios = True
except ImportError:
    has_termios = False


def interactive_shell(chan):
    """
    调用执行脚本，判断是在 Linux 或 Windows 上执行，posix_shell() 表示 Linux shell
    :param chan:
    :return:
    """
    if has_termios:
        posix_shell(chan)
    else:
        windows_shell(chan)


def posix_shell(chan):
    import select

    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)
        cmd = []
        # f = open('ssh_test.log','w')
        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = u(chan.recv(1024))
                    if len(x) == 0:
                        sys.stdout.write('\r\n*** EOF\r\n')
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                if len(x) == 0:
                    break
                if x == '\r':
                    print('input>', ''.join(cmd))
                    # log = "%s   %s\n" %(time.strftime("%Y-%m-%d %X", time.gmtime()), ''.join(cmd))
                    # print(log)

                    # 存储到数据库日志中
                    chan.models.AuditLog.objects.create(
                        user=chan.crazyeye_account,
                        log_type=1,         # 1：表示在输入命令，0 ：登录，2：登出
                        host_to_remote_user=chan.host_to_user_obj,
                        content=''.join(cmd)
                    )
                    # f.write(log)
                    cmd = []
                else:
                    cmd.append(x)
                chan.send(x)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
        # f.close()


# thanks to Mike Looijmans for this code
def windows_shell(chan):
    print("window chan", chan.host_to_user_obj)
    print("window chan", chan.crazyeye_account)
    import threading

    sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")

    def writeall(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                sys.stdout.flush()
                break
            sys.stdout.write(str(data))
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()

    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            chan.send(d)
    except EOFError:
        # user hit ^Z or F6
        pass
