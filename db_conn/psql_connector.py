import psycopg2 as pg
import os
from dotenv import load_dotenv

load_dotenv()


class PsqlConnection:
    def __init__(self):
        try:
            self.con = pg.connect(
                # dbname=os.environ.get('DB_NAME'),
                dbname='ml_orch_db',
                # user=os.environ.get('DB_USER'),
                user='postgres',
                # password=os.environ.get('DB_PASSWORD'),
                password='Osmani.1994',
                # host=os.environ.get('DB_HOST'),
                host='localhost',
                # port=int(os.environ.get('DB_PORT')),
                port=5454,
            )
        except Exception:
            raise ConnectionError('Connection not reached, check your credentials')


class Cursor(PsqlConnection):
    def __init__(self):
        super().__init__()
        self.cursor = self.con.cursor

    def dictfetchall(self, query, *args):
        cursor = self.cursor()
        try:
            if not args or args[0].__class__ is str:
                cursor.execute(query, args)
            else:
                cursor.execute(query, args[0])
        except:
            query = query.replace('%s', '{}')
            cursor.execute(query.format(args[0]))
        cols = []
        for c in cursor.description:
            cols.append(c.name)
        result_list = []
        for row in cursor.fetchall():
            result_dict = {}
            for i, col in enumerate(cols):
                result_dict[col] = row[i]
            result_list.append(result_dict)
        return result_list