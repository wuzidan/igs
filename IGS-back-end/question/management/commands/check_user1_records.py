from django.core.management.base import BaseCommand
from user.models import User
from question.models import PracticeRecord

class Command(BaseCommand):
    help = 'Check practice records for user 1'

    def handle(self, *args, **options):
        # 获取用户1
        user = User.objects.get(id=1)
        self.stdout.write(f"User: {user.username}")

        # 获取用户1的练习记录
        practice_records = PracticeRecord.objects.filter(student=user)
        self.stdout.write(f"Found {practice_records.count()} practice records for user 1")

        # 打印前10条记录
        for record in practice_records[:10]:
            challenge_id = record.challenge.challenge_id if record.challenge else None
            self.stdout.write(f"Challenge ID: {challenge_id}, Score: {record.score}")
