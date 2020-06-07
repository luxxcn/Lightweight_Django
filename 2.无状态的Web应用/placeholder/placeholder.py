"""
可复用模板

与project_name文件同级目录下执行以下命令，
可以创建foo目录和可运行的foo.py项目文件 :
    django-admin startproject foo --template=project_name
"""
import hashlib
import os
import sys

from django.conf import settings

DEBUG = os.environ.get('DEBUG', 'on') == 'on'

# 由命令startproject随机生成
SECRET_KEY = os.environ.get('SECRET_KEY', 'mqb7i(f#-_3ryh@n7ly-y(19#!1yz-3t%is!2_df!gs^!(6kw&')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

BASE_DIR = os.path.dirname(__file__) # 基于placeholder.py文件路径来创建相对路径

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
    ),
    INSTALLED_APPS=(
        'django.contrib.staticfiles',
    ),
    TEMPLATES=(
        {
            'BACKEND': 'django.template.bankends.django.DjangoTemplates',
            'DIRS': (os.path.join(BASE_DIR, 'templates'), ),
        },
    ),
    STATICFILES_DIRS=(
        os.path.join(BASE_DIR, 'static'),
    ),
    STATIC_URL='/static/',
)

from django import forms
from django.conf.urls import url
from django.core.cache import cache
# django2.0 把原来的 django.core.urlresolvers 包 更改为了 django.urls包
# from django.core.urlresolvers import reverse
from django.urls import reverse
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import etag

from io import BytesIO # 用来保存图片的字节
from PIL import Image, ImageDraw # 通过Pillow的Image来创建图片

class ImageForm(forms.Form):
    """利用表单数据检查占位图片有效性"""

    height = forms.IntegerField(min_value=1, max_value=2000)
    width  = forms.IntegerField(min_value=1, max_value=2000)

    def generate(self, image_format='PNG'):
        """创建图片，默认为png格式"""
        height  = self.cleaned_data['height'] # 通过cleaned_data获取表单数据
        width   = self.cleaned_data['width']
        key     = '{}.{}.{}'.format(width, height, image_format) # 以宽度、高度、图片格式生成一个缓存键值
        content = cache.get(key)
        if content is None:
            image = Image.new('RGB', (width, height))
            draw  = ImageDraw.Draw(image) # 在图片尺寸合适的地方覆盖文字
            text  = '{} x {}'.format(width, height)
            textwidth, textheight = draw.textsize(text)
            if textwidth < width and textheight < height:
                texttop  = (height - textheight) // 2
                textleft = (width - textwidth) // 2
                draw.text((textleft, texttop), text, fill=(255, 255, 255))
            content = BytesIO()
            image.save(content, image_format)
            content.seek(0)
            cache.set(key, content, 60 * 60) # 缓存图片一小时（3600秒）
        return content

def generate_etag(request, width, height):
    """使用hashlib来返回一个基于width和height值变化的不透明的ETag值"""
    content = 'Placeholder: {0} x {1}'.format(width, height)
    return hashlib.sha1(content.encode('utf-8')).hexdigest()

# 服务器将在浏览器第一次请求时生成改图片，
# 在后续的请求中，如果浏览器发送了一个匹配ETag的请求，
# 它将会收到304 Not Modified作为图片的相应
@etag(generate_etag)
def placeholder(request, width, height):
    form = ImageForm({'height': height, 'width': width})
    if form.is_valid():
        image = form.generate()
        return HttpResponse(image, content_type='image/png')
    else:
        return HttpResponseBadRequest('请求的图片无效') # 发送一个400 Bad Request响应

# 创建视图
def index(request):
    example = reverse('placeholder', kwargs={'width': 50, 'height': 50})
    context = {
        'example': request.build_absolute_uri(example)
    }
    return render(request, 'home.html', context)

# 将视图于一个URL模式相关联
urlpatterns = (
    url(r'^image/(?P<width>[0-9]+)x(?P<height>[0-9]+)/$', placeholder, name='placeholder'),
    url(r'^$', index, name='homepage'), # 末尾这个逗号不能少
)

application = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
