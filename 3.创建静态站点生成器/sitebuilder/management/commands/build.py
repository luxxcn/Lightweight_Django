"""
执行构建命令： python prototypes.py build
建立的静态站点存放在输出目录： _build
"""

import os
import shutil

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse
from django.test.client import Client

def get_pages():
    for name in os.listdir(settings.SITE_PAGES_DIRECTORY):
        if name.endswith('.html'):
            yield name[:-5]

class Command(BaseCommand):
    help = 'Build static site ouput.'
    leave_local_alone = True

    def add_arguments(self, parser):
        """添加命令中带的参数"""
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        """执行创建命令，创建并输出静态文件"""
        settings.DEBUG = False
        settings.COMPRESS_ENABLED = True
        if args: # 根据参数创建部分页面
            pages = args
            available = list(get_pages())
            invalid = []
            for page in pages:
                if page not in available:
                    invalid.append(page)
            if invalid: # 不存在的页面，报错
                msg = 'Invalid pages: {}'.format(', '.join(invalid))
                raise CommandError(msg)
        else: # 创建全部
            pages = get_pages()
            if os.path.exists(settings.SITE_OUTPUT_DIRECTORY):
                shutil.rmtree(settings.SITE_OUTPUT_DIRECTORY) # 清除已创建的内容
            os.mkdir(settings.SITE_OUTPUT_DIRECTORY)
        os.makedirs(settings.STATIC_ROOT, exist_ok=True)
        call_command('collectstatic', interactive=False, clear=True, verbosity=0)
        # call_command('compress', interactive=False, force=True) # django-compressor 不再支持 interactive
        call_command('compress', force=True)
        client = Client()
        for page in pages:
            url = reverse('page', kwargs={'slug': page})
            response = client.get(url)
            if page == 'index':
                output_dir = settings.SITE_OUTPUT_DIRECTORY
            else:
                output_dir = os.path.join(settings.SITE_OUTPUT_DIRECTORY, page)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            with open(os.path.join(output_dir, 'index.html'), 'wb') as f:
                f.write(response.content)