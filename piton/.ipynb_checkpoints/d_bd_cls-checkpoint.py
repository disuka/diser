# этот файл для импорта, только в формате питона, не ЮПИТЕРА!
from datetime import datetime
import threading
import mysql.connector
from mysql.connector import Error, errorcode
import time




class Bd_rabota():
  def __init__(self, reg):
    print(f'{datetime.now()}| cls_bd.INIT(idO={reg}): инициализация объекта БД_работа.')
    self.__host='localhost'         # например, 'localhost' или IP адрес сервера
    self.__database='diser' # имя вашей базы данных
    self.__user='forpiton'     # имя пользователя
    self.__password='passwordpiton'   # пароль
    self.__connection = None #само соединение с СУБД. предполагается держать открытым
    self.__oregno = reg  #идентификатор для многопоточной работы
    #print(errorcode.ER_DUP_ENTRY, 'ddddddd')

  def conn(self): #коннект воркера к бд
    print(f"{datetime.now()}| cls_bd.CONNECT(idO={self.__oregno}): метод коннекта к бд начало.")
    if self.__connection:
      kod_log = self.add_log(self.__class__.__name__,'conn',200,'пытались выполнить метод connect, но коннект то уже есть. выходим')
      return 200

    try:
            self.__connection = mysql.connector.connect(host=self.__host,
                database=self.__database,
                user=self.__user,
                password=self.__password)
            if self.__connection.is_connected():
                print(f"  {datetime.now()}| cls_bd.CONNECT(idO={self.__oregno}): Успешно подключено к базе данных")
    except Error as e:
            raise Crit20020(f"  {datetime.now()}| cls_bd.CONNECT(idO={self.__oregno}): Ошибка в методе CONN при подключении к MySQL: {e}", 20020)

  def disc(self): #дисконнект воркера к бд
    print(f"{datetime.now()}| cls_bd.DISCONNECT(idO={self.__oregno}): метод дисконнекта от бд начало, conn= {self.__connection}")
    try:
#      if self.__connection.is_connected():
      if self.__connection:
          self.__connection.close()
          print(f"  {datetime.now()}| cls_bd.DISCONNECT(idO={self.__oregno}): Соединение с MySQL было закрыто")
      else:
        print(f'  {datetime.now()}| cls_bd.DISCONNECT(idO={self.__oregno}):в методе дисконнект на найдено открытого подключения к субд')
    except Error as e:
      print(f"{datetime.now()}| cls_bd.DISCONNECT(idO={self.__oregno}) Ошибка в методе DISCONNECT при отключении от MySQL: {e}")

  def day_rows(self, select_txt):
    print(f'cls_bd.DAY_ROWS(idO={self.__oregno}): зашел в процедуру day_cursor')
    try:
      if self.__connection.is_connected():
        print(f'  cls_bd.DAY_ROWS(idO={self.__oregno}): живой коннект обнаружен')
        curs = self.__connection.cursor()
        # Выполнение запроса SELECT
        curs.execute(select_txt)
        print(f'  cls_bd.DAY_ROWS(idO={self.__oregno}): select выполнил, возвращаю LIST ')
        recs = curs.fetchall()  # Получение всех результатов запроса. обязательно выполнять, иначе is_connected() будет возвращать FALSE
        curs.close() # закрыть сразу
        return recs
      else:
        print(f'  cls_bd.DAY_ROWS(idO={self.__oregno}): живого коннекта не обнаружено, возвращать нечего')
    except Error as e:
        print(f"cls_bd.DAY_ROWS(idO={self.__oregno}): Ошибка в методе DAY_ROWS(): {e}")
  
  def ins_url(self, uurl, uurlred, iskl, kod, status,lim_rcs, lim_hrf, lim_sz, sz, errortext,recurs_lvl):
    print(f'{datetime.now()}| cls_bd.INSERT(idO={self.__oregno}): метод INSERT записи в таблицу. урл={uurl}, status={status}')
    error_kod = 0
    try:
      if self.__connection.is_connected():
        print(f'  {datetime.now()}| cls_bd.INSERT(idO={self.__oregno}): живой коннект обнаружен')
        cursor_insert = self.__connection.cursor()
        #insert_txt = f'insert into t_url (url, url_red, url_id_iskl, kod_otveta, busy, status, limit_recurs, limit_href, limit_size, url_size, err_txt) values ("{uurl}","{uurlred}",{iskl},{kod},{self.__oregno}, {status}, {lim_rcs}, {lim_hrf}, {lim_sz}, {sz},"{errortext}")'
        insert_txt = f'''
        insert into t_url set url="{uurl}", url_red="{uurlred}", url_id_iskl={iskl}, kod_otveta={kod}, busy={self.__oregno}, status={status}, 
        limit_recurs={lim_rcs}, limit_href={lim_hrf}, limit_size={lim_sz}, url_size={sz}, err_txt="{errortext}", kolwo_recurs={recurs_lvl}'''

        print(f'  {datetime.now()}| cls_bd.INSERT(idO={self.__oregno}): после сборки insert={insert_txt}')
        try:
          cursor_insert.execute(insert_txt)
          self.__connection.commit()
        except Error as e:
          print(f"    {datetime.now()}| cls_bd.INSERT(idO={self.__oregno}): Ошибка в методе INS_URL(). insert сломался: {e}, код ошибки: {e.errno}")  
          error_kod = e.errno
      else:
        print(f'  {datetime.now()}| cls_bd.INSERT(idO={self.__oregno}): живого коннекта не обнаружено, на всякий случай остановлюсь')  
        return 'stop'
        
    except Error as e:
        print(f"  {datetime.now()}| cls_bd.INSERT(idO={self.__oregno}): Ошибка в методе INS_URL(): {e}, код ошибки: {e.errno}")
        error_kod = e.errno
    finally:
      if cursor_insert:
          cursor_insert.close()
          print(f"  {datetime.now()}| cls_bd.INSERT(idO={self.__oregno}): Mетод INS_URL(), успешно закрыт курсор")
      else:
          print(f"  {datetime.now()}| cls_bd.INSERT(idO={self.__oregno}): Ошибка в методе INS_URL()? при закрытии курсора")
      print( f'{datetime.now()}| сейчас буду выходить из ins_url c кодом выхода {error_kod}')    
      return error_kod

  def add_log(self, klass, metod, level, txt): #запись в лог-таблицу
    insert_txt =''
    if not self.__connection:
      raise Crit20010(f'коннект к БД не найден в классе {self.__class__.__name__}, метод add_log', 20010)
    try:
      curs_add_log = self.__connection.cursor()
      insert_txt = f'insert into t_log set class="{klass}", metod="{metod}", level={level}, worker_nom={self.__oregno}, txt="{txt}"'
      curs_add_log.execute(insert_txt)
      self.__connection.commit()
    except Exception as e:
      print(f' insert= {insert_txt}')
      raise Crit20010(f' {e}, класс= {self.__class__.__name__}, метод add_log', 20030)
    finally:
      if curs_add_log:
        curs_add_log.close()
      else:
        raise Crit20010(f'if curs_add_log в значении FALSE, класс= {self.__class__.__name__}, метод add_log', 20010)

  def test_conn(self):
    print(f'cls_bd.TEST_CONN(idO={self.__oregno}): зашел в процедуру test_conn')
    try:
      if self.__connection.is_connected():
        print(f'  cls_bd.TEST_CONN(idO={self.__oregno}): живой коннект обнаружен')
      else:
        print(f'  cls_bd.TEST_CONN(idO={self.__oregno}): живого коннекта не обнаружено, возвращать нечего')
    except Error as e:
        print(f"cls_bd.TEST_CONN(idO={self.__oregno}): Ошибка в методе TEST_CONN: {e}")    
      
      
  def inf(self): # инфо
    print(f'cls_bd.INF(idO={self.__oregno}): информация о переменных. Хост=', self.__host,  ' дб=',self.__database, ' юзер=',self.__user, ' пароль=',self.__password, ' regno=',self.__oregno, ' connection=',self.__connection)
    if self.__connection.is_connected():
      print(f'  cls_bd.INF(idO={self.__oregno}): connect обнаружен')
    else:
      print(f'  cls_bd.INF(idO={self.__oregno}): connect НЕ обнаружен')

  def day_svoy_nomer(self):
    return self.__oregno
# ^^^^^^^^^^^^^^^^^^^^^^^ конец класса Bd_rabota ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^