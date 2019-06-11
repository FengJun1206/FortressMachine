import base64
from binascii import hexlify
import getpass
import os
import select
import socket
import sys
import time
import traceback
from paramiko.py3compat import input

import paramiko

try:
    import interactive
except ImportError:
    from . import interactive

def manual_auth(t, hostname, username, password):
    """
    验证登录
    :param t:
    :param hostname: 主机地址
    :param username: 主机账户
    :param password: 主机密码
    :return:
    """
    default_auth = 'p'      # p：表示以用户名、密码登录，r：以公钥登录（免登陆），d：未知，这里我们用 p 登录
    #auth = input('Auth by (p)assword, (r)sa key, or (d)ss key? [%s] ' % default_auth)
    # if len(auth) == 0:
    #     auth = default_auth
    auth = default_auth
    if auth == 'r':
        default_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
        path = input('RSA key [%s]: ' % default_path)
        if len(path) == 0:
            path = default_path
        try:
            key = paramiko.RSAKey.from_private_key_file(path)
        except paramiko.PasswordRequiredException:
            password = getpass.getpass('RSA key password: ')
            key = paramiko.RSAKey.from_private_key_file(path, password)
        t.auth_publickey(username, key)
    elif auth == 'd':
        default_path = os.path.join(os.environ['HOME'], '.ssh', 'id_dsa')
        path = input('DSS key [%s]: ' % default_path)
        if len(path) == 0:
            path = default_path
        try:
            key = paramiko.DSSKey.from_private_key_file(path)
        except paramiko.PasswordRequiredException:
            password = getpass.getpass('DSS key password: ')
            key = paramiko.DSSKey.from_private_key_file(path, password)
        t.auth_publickey(username, key)
    else:
        #pw = getpass.getpass('Password for %s@%s: ' % (username, hostname))
        t.auth_password(username, password)     # 验证登录


def ssh_connect(ssh_handler_instance, host_to_user_obj):
    """
    :param ssh_handler_instance: 模块 ssh_interactive 中类 SshHandler() 的实例对象
    :param host_to_user_obj: <HostToRemoteUser: test：root: 123> 对象
     用户选中的主机对象，里面存储有主机名、地址、端口等信息
    :return:
    """
    # 主机相关信息
    hostname = host_to_user_obj.host.ip_addr
    port = host_to_user_obj.host.port
    username = host_to_user_obj.remote_user.username
    password = host_to_user_obj.remote_user.password
    print(hostname, port, username, password)

    # 选择开始连接
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))        # socket 通信，连接远程主机
    except Exception as e:
        print('**** 连接失败：' + str(e))
        traceback.print_exc()
        sys.exit(1)

    try:
        t = paramiko.Transport(sock)
        try:
            t.start_client()
        except paramiko.SSHException:
            print('*** SSH negotiation failed')
            sys.exit(1)

        try:
            keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        except IOError:
            try:
                keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
            except IOError:
                print('*** Unable to open host keys file')
                keys = {}

        # check server's host key -- this is important.
        key = t.get_remote_server_key()
        if hostname not in keys:
            print('*** WARNING: Unknown host key!')
        elif key.get_name() not in keys[hostname]:
            print('*** WARNING: Unknown host key!')
        elif keys[hostname][key.get_name()] != key:
            print('*** WARNING: Host key has changed!!!')
            sys.exit(1)
        else:
            print('*** Host key OK.')

        if not t.is_authenticated():
            manual_auth(t, hostname, username, password)
        if not t.is_authenticated():
            print('*** Authentication failed. :(')
            t.close()
            sys.exit(1)

        chan = t.open_session()
        chan.get_pty()
        chan.invoke_shell()

        # 将堡垒机账户赋值到  chan 变量中，以便于在 interactive 模块中，能够记录命令，写入日志
        chan.crazyeye_account = ssh_handler_instance.user   # 堡垒机账户, ssh_interactive 模块中将 self.user = user
        chan.host_to_user_obj = host_to_user_obj
        chan.models = ssh_handler_instance.models       # ssh_interactive 模块中将 self.models = models

        print('*** Here we go!\n')          # 开始登录远程主机
        print(ssh_handler_instance, host_to_user_obj, type(host_to_user_obj))

        # 登录远程主机时，也要记录日志
        ssh_handler_instance.models.AuditLog.objects.create(
            user=ssh_handler_instance.user,
            log_type=0,
            host_to_remote_user=host_to_user_obj,
            content="***user login***"
        )

        # ssh_handler_instance.models.AuditLog.objects.create(
        #     user=ssh_handler_instance.user,
        #     log_type=0,
        #     host_to_remote_user=host_to_user_obj,
        #     content="***user login***"
        # )

        interactive.interactive_shell(chan)
        chan.close()
        t.close()

        # 登出远程主机时，也要记录日志
        ssh_handler_instance.models.AuditLog.objects.create(
            user=ssh_handler_instance.user,
            log_type=2,
            host_to_remote_user=host_to_user_obj,
            content="***user login***"
        )

    except Exception as e:
        print('*** Caught exception: ' + str(e))
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
        sys.exit(1)



