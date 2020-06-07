"""
 Django 是一个MTV框架（model-template-view）
 该文件将典型的views.py和urls.py文件合并了
"""
import os
import sys

from django.conf import settings

"""
获取运行环境的debug和secret_key设置
    export DEBUG=off # win下用set命令设置
    python hello.py runserver
"""
DEBUG = os.environ.get('DEBUG', 'on') == 'on'

SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))

# debug 为False时，需要设置ALLOWED_HOSTS
# You must set settings.ALLOWED_HOSTS if DEBUG is False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# 设置
settings.configure(
    DEBUG=DEBUG,
    SECRET_KEY=SECRET_KEY,
    ALLOWED_HOSTS=ALLOWED_HOSTS,
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )
)

from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse

# 创建视图
def index(request):
    return HttpResponse('Hello World')

# 将视图于一个URL模式相关联
urlpatterns = (
    url(r'^$', index), # 末尾这个逗号不能少
)

application = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
