import psycopg2
from flask import Flask

app = Flask(__name__, template_folder='C:/Users/MasterChief/PycharmProjects/pythonbdstud/students_back/templates')
try:
    # пытаемся подключиться к базе данных
    conn = psycopg2.connect(dbname='Students', user='postgres', password='123', host='localhost')
except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    exit('Can`t establish connection to database')
