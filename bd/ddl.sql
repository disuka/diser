CREATE DATABASE `diser` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

CREATE TABLE `t_url` (
  `id_url` int NOT NULL AUTO_INCREMENT,
  `url` varchar(700) NOT NULL DEFAULT 'длина 700 - если больше, то индекс не создается' COMMENT 'сам урл',
  `url_red` varchar(2048) DEFAULT NULL,
  `url_id_iskl` smallint unsigned NOT NULL COMMENT 'тут будут причины, по которым попытка сделать GET(url) вызвала Exception',
  `kod_otveta` smallint unsigned DEFAULT NULL COMMENT '100-600 по стандарту RFC9110',
  `busy` int unsigned NOT NULL COMMENT 'признак, что запись занята. можно ставить ид обработчика. поэтому размерность большая',
  `status` int NOT NULL COMMENT '1 - стартовая запись\n\n\n------\nв дальнейшем перейти к словарю',
  `limit_recurs` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0 - лимит по глубине не достигли\\\\\\\\n1 - лимит по глубине достигли и остановились',
  `kolwo_recurs` smallint unsigned DEFAULT NULL COMMENT 'глубина вложенности, с которой вышли из рекурсии или остановились по лимиту\\\\n',
  `limit_href` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0 - лимит по количеству ссылок на одной странице не достигли\\\\\\\\n1 - лимит по количеству ссылок на одной странице достигли и остановились, сверх лимита не обрабатываем\n',
  `kolwo_href` smallint unsigned DEFAULT NULL COMMENT 'количество ссылок на странице, которое обработано или лимит обработки. может и не быть вовсе',
  `limit_size` int unsigned NOT NULL DEFAULT '0' COMMENT 'достигнут ли лимит на размер ответа страницы. 1 - превышение лимита, не обрабатываем. 0 - превышения нет, находимся в рамках',
  `url_size` int unsigned DEFAULT NULL COMMENT 'размер страницы из ответа в байтах пока что. потом можно будет сделать в килобайтах для уменьшения размерности',
  `create_dt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `edit_dt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `err_txt` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id_url`),
  UNIQUE KEY `url_UNIQUE` (`url`),
  KEY `iskluchenieee_idx` (`url_id_iskl`),
  CONSTRAINT `t_url_iskluchenieee` FOREIGN KEY (`url_id_iskl`) REFERENCES `t_iskl` (`id_iskl`)
) ENGINE=InnoDB AUTO_INCREMENT=12346 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `t_log` (
  `nom` int unsigned NOT NULL AUTO_INCREMENT COMMENT 'чисто для автоинкремента, чтобы ставил номера строк по возрастанию, т.к. даже миллисекунды в поле датавремя могут быть одинаковы',
  `dt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `class` varchar(45) NOT NULL,
  `metod` varchar(45) NOT NULL,
  `level` tinyint unsigned NOT NULL COMMENT 'для построения логов в виде ступенек-вложенности',
  `worker_nom` smallint unsigned NOT NULL COMMENT 'идентификатор воркера',
  `txt` varchar(555) DEFAULT NULL COMMENT 'ну собственно сам лог. наверное, может иногда быть null',
  PRIMARY KEY (`nom`)
) ENGINE=InnoDB AUTO_INCREMENT=455 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='таблица логов';

CREATE TABLE `t_iskl` (
  `id_iskl` smallint unsigned NOT NULL COMMENT 'ключ',
  `iskl_txt` varchar(222) NOT NULL COMMENT 'ну само описание эксепшена',
  `iskl_gde` varchar(45) DEFAULT NULL COMMENT 'область, где возникает',
  PRIMARY KEY (`id_iskl`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='таблица, которая будет содержать разные коды эксепшенов';
