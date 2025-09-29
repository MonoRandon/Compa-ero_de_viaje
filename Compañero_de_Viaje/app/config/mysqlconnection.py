import pymysql.cursors

class MySQLConnection:
    def __init__(self, db):
        connection = pymysql.connect(host='localhost',
                                    port= 5022,
                                    user='root',
                                    password='root',
                                    db=db,
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor,
                                    autocommit=True)
        self.connection = connection
    def query_db(self, query, data=None):
        with self.connection.cursor() as cursor:
            try:
                query_str = cursor.mogrify(query, data)
                print('Correr el Query:', query_str)
                cursor.execute(query, data)
                if query.lower().find('insert') >= 0:
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find('select') >= 0:
                    result = cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
            except Exception as e:
                print('Algo Salio mal', e)
                return False
            finally:
                self.connection.close()


