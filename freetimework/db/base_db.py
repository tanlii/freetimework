from peewee import MySQLDatabase
from peewee import Model

# 线上etsy端数据
HOST = "127.0.0.1"  # us机器用内网，其他机器用外网
USER = "root"
PASSWORD = "123456"
PORT = 3306

database = MySQLDatabase(
    host=HOST,
    user=USER,
    password=PASSWORD,
    port=PORT,
    database="freetimework",
    charset="utf8mb4",
)


class BaseModel(Model):
    class Meta:
        database = database
