from backend import ssh_interactive

class ArgvHander(object):
    """
    接收用户参数，并调用相应功能
    """
    def __init__(self, argv):
        self.argv = argv

    def help_msg(self, error_msg=''):
        """帮助提示"""
        msg = """
        %s
        run 启动交互脚本程序
        """ % error_msg
        exit(msg)       # 打印并退出，Python 内置方法

    def call(self):
        """
        解析 sys.argv 输入的命令，并调用对应方法
         python3 crazyeye_manage.py：['crazyeye_manage.py']
         python3 crazyeye_manage.py run：['crazyeye_manage.py', 'run']
        :return:
        """
        if len(self.argv) == 1:
            self.help_msg()
        else:
            print(self.argv)
            if hasattr(self, self.argv[1]):     # 是否有 run
                func = getattr(self, self.argv[1])
                func()      # 执行 run() 方法
            else:
                self.help_msg('没有方法 %s' % self.argv[1])

    def run(self):
        """
        启动用户交互程序
        :return:
        """
        obj = ssh_interactive.SshHandler(self)
        obj.interactive()

