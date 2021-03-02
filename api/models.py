from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

def upload_avatar_path(instance, filename):
    # 拡張子を取得
    ext = filename.split('.')[-1]
    return '/'.join(['avatars', str(instance.userProfile.id)+str(instance.nickName)+str(".")+str(ext)])

def upload_post_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['posts', str(instance.userPost.id)+str(instance.title)+str(".")+str(ext)])

# Djangoの雛形をemail用にカスタマイズ(通常はusernameとpassword)
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('email is must')

        # emailの正規化
        user = self.model(email=self.normalize_email(email))
        # passwordをハッシュ化してから設定
        user.set_password(password)
        # データベースに保存
        user.save(using=self._db)
        return user

    # UserManagerをカスタマイズした場合は、methodもemailのversionでオーバーライドする必要がある。
    def create_superuser(self, email, password):
        # 通常のuserをcreate
        user = self.create_user(email, password)
        # add authority
        # staff => AdminのDashboardにログインする権限
        user.is_staff = True
        # superuser => 全権限
        user.is_superuser = True
        user.save(using=self._db)

        return user

# User Model (email versionにオーバーライド)
class User(AbstractBaseUser, PermissionsMixin):

    # emailがidを役割も担う => unique=True
    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # UserManagerのmethodをUser classのインスタンスから呼べるようになる。
    objects = UserManager()

    # defaultはusername
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

class Profile(models.Model):
    nickName = models.CharField(max_length=20)
    userProfile = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='userProfile',
        # userが削除された時に、対象のprofileも連動して削除
        on_delete=models.CASCADE
    )
    # Profileのインスタンス生成時の日時
    created_on = models.DateTimeField(auto_now_add=True)
    # Avatar 登録必須ではない
    img = models.ImageField(blank=True, null=True, upload_to=upload_avatar_path)

    def __str__(self):
        return self.nickName

class Post(models.Model):
    title = models.CharField(max_length=100)
    # 投稿したuserは誰か
    userPost = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='userPost',
        on_delete=models.CASCADE
    )
    # 投稿日時
    created_on = models.DateTimeField(auto_now_add=True)
    # 投稿画像
    img = models.ImageField(blank=True, null=True, upload_to=upload_post_path)
    # いいね
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked', blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    # comment内容
    text = models.CharField(max_length=100)
    # 誰のcommentか
    userComment = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='userComment',
        on_delete=models.CASCADE
    )
    # どの投稿に対するcommentか
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.text