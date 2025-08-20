# этот файл для импорта, только в формате питона, не ЮПИТЕРА!
import requests
from requests.exceptions import HTTPError
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, urlunsplit
from datetime import datetime
import time
from mysql.connector import Error, errorcode

class Krauler():
  def __init__(self, start_url, psubd):
    self.__subd = psubd #один объект Bd_rabota на один объект краулера. типа это пользователь. не нужно беспокоиться о конкурентном доступе при многопоточной работе краулеров. СУБД сама разрулит одновременный доступ от разных краулеров. пул коннектов решил не делать,т.к. поток всегда чтото пишет.вроде логично держать один коннект на один поток/воркер
    self.__krregno = self.__subd.day_svoy_nomer()
    self.__subd.add_log(self.__class__.__name__,'init',1,'инициализация объекта Krauler.')

#    try:
#      self.__subd.add_log(self.__class__.__name__,'start1',1,f'Начало метода START1 в Krauler. стартую с урла:{self.__start_url}')
#    except Log_20000:
#      return 20000

    self.__start_url = start_url  # откуда начинаем
    self.__max_count = 1   # максимальное количество скачиваний урлов. сквозная относительно вложенности и количества урлов на странице
    self.__now_count = 0   # текущее количество скачиваний урлов. сквозная относительно вложенности и количества урлов на странице
    #self.__visited = set()          # посещенные страницы
    self.__setup_lim_recurs = 10 #глубина вложенности. на сколько в рекурсию можем провалиться одним воркером
    self.__now_recurs = 0 #глубина вложенности. на текущий момент
    self.__setup_lim_href = 40 #максимальное количество ссылок на странице. сверх этого не обрабатываем
    self.__setup_lim_size = 1048576 #максимальный размер ответа в байтах, который обрабатываем
    self.__urldubley = 0 #здесь можно считать дубли, которые будут пытаться записываться в базу. для дальнейшего анализа

  def start1(self): # по-большому счету для красоты, чтобы понять, откуда стартуем
    self.__subd.add_log(self.__class__.__name__,'start1',1,f'Начало метода START1 в Krauler. стартую с урла:{self.__start_url}')
    kod_dl = self.__download_link(self.__start_url, 1)
    self.__subd.add_log(self.__class__.__name__,'start1',1,f'Закончил метод START1 в Krauler с кодом {kod_dl}, дублей всего было {self.__urldubley}')

  def __download_link(self, url, status=0): # это уже рекуррентная функция
    """
   if (self.__now_count>8):
      print ('ddddddddddddddddddddddddddddddddddddddddd')
      raise NNN
    """

    if self.__now_recurs >= self.__setup_lim_recurs:
      print (f'    {datetime.now()}| cls_kr.DOWNLOAD_LINK(idO={self.__krregno}): достигли лимит по кол-ву рекурсий выходим.')
      self.__subd.add_log(self.__class__.__name__,'__download_link',30,f'--- начало, url={url}, status={status}, лимит(рекурс)={self.__now_recurs}')
      return 'хватит по уровню рекурсии'
    self.__subd.add_log(self.__class__.__name__,'__download_link',1,f'--- начало, url={url}, status={status}')
    isklu4enie = None #моя личная классификация исключений. один код может включать несколько реальных кодов ошибок. так что это группировочные некие коды
    errtxt = '' #для записи в БД текст ошибки. он будет появляться только если сработал эксепшн.

    def get_redirect_url(rr): #это для возвращения урла, на который идет редирект
      if rr.status_code in [301, 302, 303, 307, 308]:
        return rr.headers.get('location') #регистронезависимое извлечение заголовка
      return ''

    try:
      self.__now_count += 1 #попытка увеличивается независимо от того, будет ли гет успешным. может ссылка живая, но заблокирована по законодательству. получим таймаут или еще чего, но попытка увеличивается
      response = requests.get(url,timeout=(3, 10), allow_redirects=False)  # 3 сек. на подключение, 10 сек. на чтение, запрет редиректов, иначе не разобраться
      isklu4enie = 0   #если эксепшенов не было, то поставим в ноль. будет означать, что какойто код у нас имеется
      response.raise_for_status() # Метод raise_for_status() выбросит исключение HTTPError, если статус ответа указывает на ошибку (4xx или 5xx):
      kod_otveta=response.status_code
      self.__subd.add_log(self.__class__.__name__,'__download_link',10,f' get(url) выполнен для: {url}. код ответа={kod_otveta}, всего посетили страниц: {self.__now_count}')

      kod_insert = self.__subd.ins_url(url, get_redirect_url(response), isklu4enie, kod_otveta, status, self.__setup_lim_recurs,self.__setup_lim_href,self.__setup_lim_size, len(response.content),errtxt,self.__now_recurs) #запись в бд
      if kod_insert == errorcode.ER_DUP_ENTRY:
        self.__urldubley += 1
        self.__subd.add_log(self.__class__.__name__,'__download_link',20,f'обнаружена попытка задублировать строку. похоже, что ее мы уже обрабатывали раньше. выходим.')
        return 'дубль'
      elif self.__now_count >= self.__max_count:
        self.__subd.add_log(self.__class__.__name__,'__download_link',30,f'Достигли предел настроек по общему количестсву: max={self.__max_count}, текущий счетчик: {self.__now_count}')
        return 'достигнут общий лимит'
      if kod_otveta == 200:
        self.__subd.add_log(self.__class__.__name__,'__download_link',40,f'обрабатываю ответ 200, буду посылать в парсер')
        soup = BeautifulSoup(response.text, 'html.parser')
        self.__parse_links(soup, url)
      else:
        self.__subd.add_log(self.__class__.__name__,'__download_link',50,f'Парсить не будем, т.к. не получил код 200: {url} (Status code: {kod_otveta})')

    except requests.exceptions.ConnectTimeout as e:
      isklu4enie = 1
      errtxt = e
    except requests.exceptions.ReadTimeout as e:
      isklu4enie = 2
      errtxt = e
    except requests.exceptions.Timeout as e:
      isklu4enie = 3
      errtxt = e
    except requests.exceptions.ConnectionError as e:
      isklu4enie = 1000
      errtxt = e
    except HTTPError as e:
      isklu4enie = 404
      errtxt = e
    except requests.RequestException as e: #если скачать страничку не получилось. ошибка вобще непонятная при получении request
      isklu4enie = 999
      errtxt = e
      print(f"  {datetime.now()}| cls_kr.DOWNLOAD_LINK(idO={self.__krregno}): ошибка 999 при попытке сделать GET непонятная: {e}")
    except Exception as e: #если ошибка вобще-вобще непонятная
      isklu4enie = 9999
      errtxt = e
      print(f"  {datetime.now()}| cls_kr.DOWNLOAD_LINK(idO={self.__krregno}): ошибка 9999 вобще-вобще непонятная: {e} nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
    
    if isklu4enie == None: # вобще такого никогда не должно быть
      print(f'  {datetime.now()}| cls_kr.DOWNLOAD_LINK(idO={self.__krregno}): вобще хрень какая-то, не должно такого быть. на выходе.')
      return 'error_HZ'
    elif isklu4enie == 0:
      return 'ok'  # если ноль, то значит мы сделали гет и он прошел норм и мы уже адрес записали в бд и сходили по рекурсии парсить
    else: #здесь формируем инсерт в том случае, если было какое-то исключение.
      kod_insert = self.__subd.ins_url(url, '', isklu4enie, 'NULL', status, self.__setup_lim_recurs,self.__setup_lim_href,self.__setup_lim_size, 0, errtxt,self.__now_recurs) #запись в бд
    #except Exception: #если скачать страничку не получилось вобще непонятно почему
      #print(f"  cls_kr.DOWNLOAD_LINK(idO={self.__krregno}): ошибка вобще ХЗ --{Exception.error}")
      #print(f"    cls_kr.DOWNLOAD_LINK(idO={self.__krregno}): переданный урл:{url}")
        # Delay to avoid overwhelming the server
    time.sleep(1)

  def __parse_links(self, soup, base_url):
    print(f'{datetime.now()}| cls_kr.PARSE_LINKS(idO={self.__krregno}): зашел')
    self.__now_recurs += 1
    for link in soup.find_all('a', href=True):
      absolute_url = urljoin(base_url, link['href']) #здесь могут быть еще параметры всякие в урле, нужно их выкусить
      p_url = urlsplit(absolute_url)
      absolute_url = urlunsplit((p_url.scheme, p_url.netloc, p_url.path, '', '')) #вот тут все выкусили из урла, все параметры и их значения. может и потом нужно их обрабатывать будет
      #if absolute_url not in self.__visited:
        #self.__download_link(absolute_url) # уходим в рекурсию
      #print('абсолютный urllllllll:',absolute_url,', base_url=',base_url, '. сам href=', link['href'])
      print (f"  {datetime.now()}| cls_kr.PARSE_LINKS(idO={self.__krregno})| base_url={base_url}: нашел такой:{absolute_url}, link={link['href']}")
      kod_rec = self.__download_link(absolute_url) # уходим в рекурсию
    print (f"  {datetime.now()}| cls_kr.PARSE_LINKS(idO={self.__krregno})| base_url={base_url}: вышел из рекурсии:{absolute_url} с кодом выхода {kod_rec}, сейчас буду брать след. адрес")
    self.__now_recurs -= 1
