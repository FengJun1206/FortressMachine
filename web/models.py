from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)


class Host(models.Model):
    """主机"""
    name = models.CharField(max_length=64, verbose_name='主机名', unique=True)
    ip_addr = models.GenericIPAddressField(unique=True, verbose_name='主机地址')
    port = models.SmallIntegerField(verbose_name='端口', default=22)
    idc = models.ForeignKey('IDC', on_delete=models.CASCADE, verbose_name='所属机房')

    def __str__(self):
        return self.name


class HostGroup(models.Model):
    """主机组，将主机分组"""
    name = models.CharField(max_length=64, verbose_name='主机分组名')
    host_to_remote_users = models.ManyToManyField('HostToRemoteUser', verbose_name='远程主机账户')

    def __str__(self):
        return self.name


class RemoteUser(models.Model):
    """
    存储远程要管理的主机的账户信息
    auth_key 为登录主机的方式：a. 密码方式、b. 公钥方式（不需要密码，因此密码可为空）
    """
    auth_type_choice = ((0, 'ssh-password'), (1, 'ssh-key'))
    auth_type = models.SmallIntegerField(choices=auth_type_choice, default=0, verbose_name='登录主机方式')
    username = models.CharField(max_length=32, verbose_name='主机账户')
    password = models.CharField(max_length=64, blank=True, null=True, verbose_name='主机密码')

    class Meta:
        # 登录方式和账户、密码联合唯一，不能重复，同样的登录方式，登录账户密码不一致
        unique_together = ('auth_type', 'username', 'password')

    def __str__(self):
        return '%s: %s' % (self.username, self.password)


class HostToRemoteUser(models.Model):
    """绑定主机和远程用户的对应关系"""
    host = models.ForeignKey('Host', on_delete=models.CASCADE, verbose_name='主机名')
    remote_user = models.ForeignKey('RemoteUser', on_delete=models.CASCADE, verbose_name='主机账户')

    class Meta:
        unique_together = ('host', 'remote_user')

    def __str__(self):
        return '%s :%s [%s]' % (self.host, self.host.ip_addr , self.remote_user)


class IDC(models.Model):
    """IDC 机房，放置服务器的机房"""
    name = models.CharField(max_length=64, verbose_name='机房名')
    addr = models.CharField(max_length=128, verbose_name='机房地址', blank=True, null=True)

    def __str__(self):
        return "%s-%s" % (self.name, self.addr)


class AuditLog(models.Model):
    """存储审计日志"""
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, verbose_name='堡垒机账户', null=True,blank=True)
    host_to_remote_user = models.ForeignKey('HostToRemoteUser', verbose_name='远程主机', on_delete=models.CASCADE, null=True,blank=True)

    log_type_choices = ((0, 'login'), (1, 'cmd'), (2, 'logout'))        # 日志类型分为登录、输入命令时以及登出
    log_type = models.SmallIntegerField(choices=log_type_choices, verbose_name='日志类型', default=0)

    content = models.CharField(max_length=255, null=True, blank=True, verbose_name='日志内容')
    date = models.DateTimeField(auto_now_add=True, verbose_name='日志记录时间', null=True,blank=True)

    def __str__(self):
        return '%s %s' % (self.host_to_remote_user, self.content)


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """创建普通账户"""
        if not email:
            raise ValueError('账户必须有一个邮件地址')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """创建一个超级用户"""
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser,PermissionsMixin):
    """堡垒机账号"""
    email = models.EmailField(
        verbose_name='邮箱',
        max_length=255,
        unique=True,

    )
    name = models.CharField(max_length=64, verbose_name="账户名")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    objects = UserProfileManager()

    host_to_remote_users = models.ManyToManyField("HostToRemoteUser", blank=True, null=True, verbose_name='远程主机账户')
    host_groups = models.ManyToManyField("HostGroup", blank=True, null=True, verbose_name='主机组')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email


class Task(models.Model):
    """批量任务"""
    task_type_choices = (('cmd', '批量命令'), ('file_transfer', '批量文件'))
    task_type = models.CharField(choices=task_type_choices, max_length=64, verbose_name='批量任务类型')
    content = models.CharField(max_length=255, verbose_name='任务内容', default='cmd')
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, verbose_name='谁创建的任务')

    def __str__(self):
        return "%s %s" % (self.task_type, self.content)


class TaskDetail(models.Model):
    """存储匹配任务子结果"""
    task = models.ForeignKey('Task', on_delete=models.CASCADE, verbose_name='哪个任务的结果')
    host_to_remote_user = models.ForeignKey('HostToRemoteUser', on_delete=models.CASCADE)
    result = models.TextField(verbose_name='任务执行结果')

    status_choices = ((0, 'initialized'), (1, 'success'), (2, 'failed'), (3, 'timeout'))
    status = models.PositiveIntegerField(choices=status_choices, default=0, verbose_name='状态')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.task, self.host_to_remote_user)
