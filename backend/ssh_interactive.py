from django.contrib.auth import authenticate
from web import models
from backend import paramiko_ssh


class SshHandler(object):
    """堡垒机交互脚本"""

    def __init__(self, argv_handler_instance):
        self.argv_handler_instance = argv_handler_instance
        self.models = models

    def auth(self):
        """登录认证"""
        count = 0
        while count < 3:
            username = input('堡垒机账号：').strip()
            password = input('密码：').strip()
            user = authenticate(username=username, password=password)
            if user:
                self.user = user
                return True
            else:
                count += 1

    def interactive(self):
        if self.auth():
            print('以下为所有认证过的主机。。。')

            # 所有主机组
            while True:
                host_group_list = self.user.host_groups.all()   # <QuerySet [<HostGroup: WEB Server>, <HostGroup: DB>]>

                # 循环主机分组对象，取出主机分组名、已经对应的主机账号个数
                for index1, host_group_obj in enumerate(host_group_list):
                    print('%s \t %s [%s]' % (index1, host_group_obj.name, host_group_obj.host_to_remote_users.count()))

                print('z. \t未分组主机 [%s]' % (self.user.host_to_remote_users.count()))

                # 选择输入代码
                choices = input('请选择主机组：>>>')
                if choices.isdigit():   # 如果是数字，则继续
                    choices = int(choices)
                    # 已选择的主机分组
                    selected_host_group = host_group_list[choices]      # <QuerySet [<HostGroup: WEB Server>, <HostGroup: DB>]>[1]
                elif choices == 'z':
                    selected_host_group = self.user     # 赋值

                while True:
                    """selected_host_group.host_to_remote_users.all() = 
                    <QuerySet [<HostToRemoteUser: test：root: 123>, <HostToRemoteUser: centOS：shit: 123>, <HostToRemoteUser: centOS：root: 12
345>]>
                    """
                    # 所有关联的主机账户信息
                    all_related_host_user_list = selected_host_group.host_to_remote_users.all()

                    for index2, host_to_user_obj in enumerate(all_related_host_user_list):
                        print('%s \t %s' % (index2, host_to_user_obj))

                    choices = input('请选择主机>>>：').strip()
                    if choices.isdigit():
                        choices = int(choices)
                        # 用户已选择的主机账户对象
                        seleced_host_to_user_obj = all_related_host_user_list[choices]
                        print('开始登录 %s' % seleced_host_to_user_obj)

                        paramiko_ssh.ssh_connect(self, seleced_host_to_user_obj)
                    elif choices == 'b':
                        break






