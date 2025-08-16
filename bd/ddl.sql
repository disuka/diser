CREATE DATABASE `diser` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

CREATE TABLE `t_url` (
  `id_url` int NOT NULL AUTO_INCREMENT,
  `url` varchar(700) NOT NULL DEFAULT '����� 700 - ���� ������, �� ������ �� ���������' COMMENT '��� ���',
  `url_red` varchar(2048) DEFAULT NULL,
  `url_id_iskl` smallint unsigned NOT NULL COMMENT '��� ����� �������, �� ������� ������� ������� GET(url) ������� Exception',
  `kod_otveta` smallint unsigned DEFAULT NULL COMMENT '100-600 �� ��������� RFC9110',
  `busy` int unsigned NOT NULL COMMENT '�������, ��� ������ ������. ����� ������� �� �����������. ������� ����������� �������',
  `status` int NOT NULL COMMENT '1 - ��������� ������\n\n\n------\n� ���������� ������� � �������',
  `limit_recurs` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0 - ����� �� ������� �� ��������\\\\\\\\n1 - ����� �� ������� �������� � ������������',
  `kolwo_recurs` smallint unsigned DEFAULT NULL COMMENT '������� �����������, � ������� ����� �� �������� ��� ������������ �� ������\\\\n',
  `limit_href` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0 - ����� �� ���������� ������ �� ����� �������� �� ��������\\\\\\\\n1 - ����� �� ���������� ������ �� ����� �������� �������� � ������������, ����� ������ �� ������������\n',
  `kolwo_href` smallint unsigned DEFAULT NULL COMMENT '���������� ������ �� ��������, ������� ���������� ��� ����� ���������. ����� � �� ���� �����',
  `limit_size` int unsigned NOT NULL DEFAULT '0' COMMENT '��������� �� ����� �� ������ ������ ��������. 1 - ���������� ������, �� ������������. 0 - ���������� ���, ��������� � ������',
  `url_size` int unsigned DEFAULT NULL COMMENT '������ �������� �� ������ � ������ ���� ���. ����� ����� ����� ������� � ���������� ��� ���������� �����������',
  `create_dt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `edit_dt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `err_txt` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id_url`),
  UNIQUE KEY `url_UNIQUE` (`url`),
  KEY `iskluchenieee_idx` (`url_id_iskl`),
  CONSTRAINT `t_url_iskluchenieee` FOREIGN KEY (`url_id_iskl`) REFERENCES `t_iskl` (`id_iskl`)
) ENGINE=InnoDB AUTO_INCREMENT=12346 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `t_log` (
  `nom` int unsigned NOT NULL AUTO_INCREMENT COMMENT '����� ��� ��������������, ����� ������ ������ ����� �� �����������, �.�. ���� ������������ � ���� ��������� ����� ���� ���������',
  `dt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `class` varchar(45) NOT NULL,
  `metod` varchar(45) NOT NULL,
  `level` tinyint unsigned NOT NULL COMMENT '��� ���������� ����� � ���� ��������-�����������',
  `worker_nom` smallint unsigned NOT NULL COMMENT '������������� �������',
  `txt` varchar(555) DEFAULT NULL COMMENT '�� ���������� ��� ���. ��������, ����� ������ ���� null',
  PRIMARY KEY (`nom`)
) ENGINE=InnoDB AUTO_INCREMENT=455 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='������� �����';

CREATE TABLE `t_iskl` (
  `id_iskl` smallint unsigned NOT NULL COMMENT '����',
  `iskl_txt` varchar(222) NOT NULL COMMENT '�� ���� �������� ���������',
  `iskl_gde` varchar(45) DEFAULT NULL COMMENT '�������, ��� ���������',
  PRIMARY KEY (`id_iskl`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='�������, ������� ����� ��������� ������ ���� ����������';
