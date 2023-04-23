from django.core.management.base import BaseCommand, CommandError
from django.db import connection

class Command(BaseCommand):
    help = '데이터베이스의 charactor set을 변경하는 커맨드.'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('SHOW TABLES')
        results=[]
        for row in cursor.fetchall(): results.append(row)
        for row in results: cursor.execute('ALTER TABLE %s CONVERT TO CHARACTER SET utf8 COLLATE     utf8_general_ci;' % (row[0]))
    
        self.stdout.write(self.style.SUCCESS('Successfully change database settings' ))