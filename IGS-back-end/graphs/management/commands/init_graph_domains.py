from django.core.management.base import BaseCommand
from graphs.models import GraphDomain


class Command(BaseCommand):
    help = '初始化知识图谱领域数据'

    def handle(self, *args, **options):
        domains = [
            'C/C++ 编程',
            'Python 编程',
            'Web 前端开发',
            '数据结构与算法',
            '机器学习',
            '数据库技术',
            '云计算与容器',
            '移动应用开发',
            '测试技术',
            '其他编程技术'
        ]
        
        created_count = 0
        existing_count = 0
        
        for domain_name in domains:
            domain, created = GraphDomain.objects.get_or_create(
                name=domain_name,
                defaults={'created_by': None}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 创建领域: {domain_name}')
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f'- 领域已存在: {domain_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n完成！新建 {created_count} 个领域，{existing_count} 个已存在'
            )
        )
