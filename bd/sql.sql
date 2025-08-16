#посмотреть блокировки
SELECT * FROM INFORMATION_SCHEMA.INNODB_TRX;

#посмотреть текущие сессии
SELECT * FROM information_schema.PROCESSLIST order by user, id;