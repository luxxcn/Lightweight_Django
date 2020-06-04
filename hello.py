"""
 Django 是一个MTV框架（model-template-view）
 该文件将典型的views.py和urls.py文件合并了
"""
import sys

from django.conf import settings
# 设置
settings.configure(
    DEBUG=True,
    SECRET_KEY='thisissecretkey',
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
import fcntl

# 创建视图
def index(request):
    return HttpResponse('Hello World')

# 将视图于一个URL模式相关联
urlpatterns = (
    url(r'^$', index), # 这个逗号不能少
)

application = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
