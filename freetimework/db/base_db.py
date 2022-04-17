from peewee import MySQLDatabase
from peewee import Model

# 线上etsy端数据
HOST = "127.0.0.1"  # us机器用内网，其他机器用外网
USER = "root"
PASSWORD = ""
PORT = 3306

database = MySQLDatabase(
    host=HOST,
    user=USER,
    password=PASSWORD,
    port=PORT,
    database="etsy_data_us",
    charset="utf8mb4",
)

