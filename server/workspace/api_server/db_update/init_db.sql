-- phpMyAdmin SQL Dump
-- version 3.4.10.1deb1
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2016 年 06 月 03 日 13:52
-- 服务器版本: 5.5.46
-- PHP 版本: 5.3.10-1ubuntu3.21

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `beiqi_ssp`
--

-- --------------------------------------------------------
/*Table structure for table `db_version` */

DROP TABLE IF EXISTS `db_version`;

CREATE TABLE `db_version` (
  `db_version` int(11) NOT NULL DEFAULT '1' COMMENT '数据库版本'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

/*Data for the table `db_version` */

insert  into `db_version`(`db_version`) values (1);

--
-- 表的结构 `eticket`
--
DROP TABLE IF EXISTS `eticket`;

CREATE TABLE `eticket` (
  `code` varchar(25) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '电子客车票代码',
  `stat` tinyint(2) unsigned NOT NULL COMMENT '状态：0:未启用，1启用，2验证',
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_unicode_ci COMMENT='电子客车票';

--
-- 转存表中的数据 `eticket`
--

INSERT INTO `eticket` (`code`, `stat`) VALUES
('0101102016051618007583001', 2),
('0101102016051618007583012', 2),
('0101102016051618007583101', 2),
('0101102016051618007583102', 1),
('0101102016051618007583103', 2),
('0101102016051618007583104', 1),
('0101102016051618007583105', 1),
('0101102016051618007583106', 2),
('0101102016051618007583107', 2),
('0101102016051618007583108', 1),
('0101102016051618007583109', 1),
('0101102016051618007583110', 1),
('0101102016051618007583111', 1),
('0101102016051618007583112', 1),
('0101102016051618007583113', 1),
('0101102016051618007583114', 2),
('0101102016051618007583115', 1),
('0101102016051618007583116', 1),
('0101102016051618007583117', 1),
('0101102016051618007583118', 1),
('0101102016051618007583119', 1),
('0101102016051618007583120', 1),
('278423', 2),
('369510', 2),
('420815', 2),
('649861', 2),
('742248', 2),
('815255', 2);

-- --------------------------------------------------------

--
-- 表的结构 `resource`
--
DROP TABLE IF EXISTS `resource`;

CREATE TABLE `resource` (
  `id` varchar(20) COLLATE utf8_unicode_ci NOT NULL COMMENT '资源id',
  `album_id` varchar(20) COLLATE utf8_unicode_ci NOT NULL COMMENT '专辑id',
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL COMMENT '名称',
  `ref` tinytext COLLATE utf8_unicode_ci NOT NULL COMMENT '引用地址',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 转存表中的数据 `resource`
--

INSERT INTO `resource` (`id`, `album_id`, `name`, `ref`) VALUES
('res_1', 'ab_1', 'Kalimba.mp3', '88d7dce4248c314fdd773f86b7198b31dd0aff81719dfd54aa033641df0a83b25cf5c6a1a146d340b0bbf3e2475dabefe4cbd1e8f4adeb706a91d6a02b28a80e57586dbfa413e19b29987f484660ec6709a94b74c2307ee1cb5e0f5d421cf0fdef08d10006197e47ce64eaeeafa8293e58a61d'),
('res_2', 'ab_2', 'Maid with the Flaxen Hair.mp3', '88d7dce4248c314fdd773f86b7198b31dd0aff81719dfd54aa033641df0a83b25cf5c6a1a146d340b0bbf3e2475dabefe4cbd1e8f4adeb706a91d6a02b28a80e57586dbfa413e19b29987f484660ec6709a94b74c2307ee1cb5e0f5d421cf0fdef08d10006197e47ce64eaeeafa8293e58a61d'),
('res_3', 'ab_3', 'Sleep Away.mp3', '88d7dce4248c314fdd773f86b7198b31dd0aff81719dfd54aa033641df0a83b25cf5c6a1a146d340b0bbf3e2475dabefe4cbd1e8f4adeb706a91d6a02b28a80e57586dbfa413e19b29987f484660ec6709a94b74c2307ee1cb5e0f5d421cf0fdef08d10006197e47ce64eaeeafa8293e58a61d'),
('res_4', 'ab_4', 'Sleep Away.mp3', '88d7dce4248c314fdd773f86b7198b31dd0aff81719dfd54aa033641df0a83b25cf5c6a1a146d340b0bbf3e2475dabefe4cbd1e8f4adeb706a91d6a02b28a80e57586dbfa413e19b29987f484660ec6709a94b74c2307ee1cb5e0f5d421cf0fdef08d10006197e47ce64eaeeafa8293e58a61d'),
('res_5', 'ab_5', 'Maid with the Flaxen Hair.mp3', '88d7dce4248c314fdd773f86b7198b31dd0aff81719dfd54aa033641df0a83b25cf5c6a1a146d340b0bbf3e2475dabefe4cbd1e8f4adeb706a91d6a02b28a80e57586dbfa413e19b29987f484660ec6709a94b74c2307ee1cb5e0f5d421cf0fdef08d10006197e47ce64eaeeafa8293e58a61d');

-- --------------------------------------------------------

--
-- 表的结构 `res_album`
--
DROP TABLE IF EXISTS `res_album`;

CREATE TABLE `res_album` (
  `id` varchar(20) COLLATE utf8_unicode_ci NOT NULL COMMENT '专辑ID，无意义',
  `cls_id` varchar(20) COLLATE utf8_unicode_ci NOT NULL COMMENT '分类ID',
  `album` varchar(50) COLLATE utf8_unicode_ci NOT NULL COMMENT '专辑',
  `des` tinytext COLLATE utf8_unicode_ci COMMENT '描述',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 转存表中的数据 `res_album`
--

INSERT INTO `res_album` (`id`, `cls_id`, `album`, `des`) VALUES
('ab_1', 'cls_1', '专辑1', '专辑1'),
('ab_2', 'cls_2', '专辑2', '专辑2'),
('ab_3', 'cls_3', '专辑3', '专辑3'),
('ab_4', 'cls_3', '专辑3', '专辑3'),
('ab_5', 'cls_4', '专辑4', '专辑4');

-- --------------------------------------------------------

--
-- 表的结构 `res_cls`
--
DROP TABLE IF EXISTS `res_cls`;

CREATE TABLE `res_cls` (
  `id` varchar(20) COLLATE utf8_unicode_ci NOT NULL COMMENT '分类id',
  `media_type` varchar(50) COLLATE utf8_unicode_ci NOT NULL COMMENT '媒体类型，text,video, audio',
  `cls` varchar(50) COLLATE utf8_unicode_ci NOT NULL COMMENT '资源分类,儿歌，故事等',
  `des` tinytext COLLATE utf8_unicode_ci COMMENT '描述',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 转存表中的数据 `res_cls`
--

INSERT INTO `res_cls` (`id`, `media_type`, `cls`, `des`) VALUES
('cls_1', 'audio', '分类1', '分类1'),
('cls_2', 'audio', '分类2', '分类2'),
('cls_3', 'audio', '分类3', '分类3'),
('cls_4', 'audio', '分类4', '分类4');

-- --------------------------------------------------------

--
-- 表的结构 `user_info`
--
DROP TABLE IF EXISTS `user_info`;

CREATE TABLE `user_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `nickname` varchar(20) DEFAULT NULL,
  `reg_from` varchar(10) DEFAULT NULL,
  `reg_agent` varchar(60) DEFAULT NULL,
  `reg_ts` datetime DEFAULT NULL,
  `reg_ip` varchar(40) DEFAULT NULL,
  `last_login_agent` varchar(60) DEFAULT NULL,
  `last_login_ts` datetime DEFAULT NULL,
  `last_login_ip` varchar(40) DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  `vip_lvl` varchar(10) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `remarks` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=35 ;

--
-- 转存表中的数据 `user_info`
--

INSERT INTO `user_info` (`id`, `username`, `nickname`, `reg_from`, `reg_agent`, `reg_ts`, `reg_ip`, `last_login_agent`, `last_login_ts`, `last_login_ip`, `status`, `vip_lvl`, `mobile`, `remarks`) VALUES
(1, '18650089855@jiashu.com', 'gxm', NULL, 'okhttp/2.2.0', '2016-03-31 07:44:09', '120.39.51.210', 'okhttp/2.2.0', '2016-04-25 01:36:00', '121.204.97.229', NULL, NULL, NULL, NULL),
(2, '13559937192@jiashu.com', '多禄', NULL, 'okhttp/2.2.0', '2016-03-31 07:52:05', '120.39.51.210', 'okhttp/2.2.0', '2016-04-25 01:10:36', '121.204.97.229', NULL, NULL, NULL, NULL),
(3, '13685011233@jiashu.com', NULL, NULL, 'okhttp/2.2.0', '2016-03-31 08:00:47', '120.39.51.210', 'okhttp/2.2.0', '2016-03-31 08:00:58', '120.39.51.210', NULL, NULL, NULL, NULL),
(4, '13124070068@jiashu.com', '九林', NULL, 'okhttp/2.2.0', '2016-03-31 09:13:51', '121.204.168.86', 'okhttp/2.2.0', '2016-04-22 08:23:41', '27.159.71.61', NULL, NULL, NULL, NULL),
(5, '18606092764@jiashu.com', '木里', NULL, 'okhttp/2.2.0', '2016-03-31 09:15:43', '121.204.168.86', 'okhttp/2.2.0', '2016-05-23 08:21:21', '218.85.146.174', NULL, NULL, NULL, NULL),
(6, '15606913317@jiashu.com', NULL, NULL, 'okhttp/2.2.0', '2016-04-02 02:13:41', '220.249.191.180', 'okhttp/2.2.0', '2016-04-24 07:29:22', '220.200.41.73', NULL, NULL, NULL, NULL),
(7, '18606919996@jiashu.com', NULL, NULL, '贝奇助手/35 CFNetwork/758.2.8 Darwin/15.0.0', '2016-04-02 02:21:42', '59.56.187.30', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-24 07:29:37', '220.200.41.73', NULL, NULL, NULL, NULL),
(8, '18559279649@jiashu.com', NULL, NULL, 'Python-httplib2/0.9.2 (gzip)', '2016-04-07 08:35:31', '127.0.0.1', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(9, '13635276132@jiashu.com', NULL, NULL, 'okhttp/2.2.0', '2016-04-13 10:26:39', '223.104.6.52', 'okhttp/2.2.0', '2016-04-23 08:08:54', '27.159.71.61', NULL, NULL, NULL, NULL),
(10, '13338283996@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:03:32', '175.44.114.91', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:07:10', '175.44.114.91', NULL, NULL, NULL, NULL),
(11, '18941860177@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:03:40', '113.238.53.234', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:05:48', '113.238.53.234', NULL, NULL, NULL, NULL),
(12, '15266589980@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:03:46', '27.217.159.156', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:04:49', '27.217.159.156', NULL, NULL, NULL, NULL),
(13, '15640644795@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/711.1.12 Darwin/14.0.0', '2016-04-18 06:03:56', '123.188.153.92', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(14, '18796691180@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:03:57', '211.138.199.181', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:04:21', '211.138.199.181', NULL, NULL, NULL, NULL),
(15, '13604175056@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:04:07', '112.40.25.122', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(16, '18603340696@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:04:53', '110.245.45.74', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:06:07', '110.245.45.74', NULL, NULL, NULL, NULL),
(17, '18434652376@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:05:38', '123.175.16.40', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:06:37', '123.175.16.40', NULL, NULL, NULL, NULL),
(18, '15257091072@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:05:56', '122.225.19.19', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:07:33', '122.225.19.19', NULL, NULL, NULL, NULL),
(19, '15881783081@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.2.8 Darwin/15.0.0', '2016-04-18 06:06:17', '182.146.11.241', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(20, '13915789234@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:06:19', '114.217.87.93', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(21, '18080724446@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:06:30', '182.139.118.225', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(22, '18091203849@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:06:52', '111.19.73.57', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:08:26', '111.19.73.57', NULL, NULL, NULL, NULL),
(23, '18219021210@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:08:32', '220.114.252.72', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(24, '13154484558@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:08:53', '218.6.163.143', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:09:43', '218.6.163.143', NULL, NULL, NULL, NULL),
(25, '18218358800@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:09:28', '110.81.23.22', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(26, '13719996134@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.2.8 Darwin/15.0.0', '2016-04-18 06:09:34', '113.118.117.77', '贝奇助手/43 CFNetwork/758.2.8 Darwin/15.0.0', '2016-04-18 06:10:31', '113.118.117.77', NULL, NULL, NULL, NULL),
(27, '13589679842@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:10:34', '112.7.3.16', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:11:49', '112.7.3.16', NULL, NULL, NULL, NULL),
(28, '18911335392@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:11:56', '42.81.42.0', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(29, '18081289099@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.2.8 Darwin/15.0.0', '2016-04-18 06:12:32', '117.172.24.28', '贝奇助手/43 CFNetwork/758.2.8 Darwin/15.0.0', '2016-04-18 06:13:02', '117.172.24.28', NULL, NULL, NULL, NULL),
(30, '13971731786@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:13:47', '117.150.178.96', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(31, '13952957331@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:20:05', '218.3.131.89', '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-18 06:20:50', '218.3.131.89', NULL, NULL, NULL, NULL),
(32, '13556653860@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/711.1.16 Darwin/14.0.0', '2016-04-18 06:24:05', '183.8.10.143', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(33, '18240486005@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/711.4.6 Darwin/14.0.0', '2016-04-18 06:30:04', '39.153.17.85', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(34, '18671400751@jiashu.com', NULL, NULL, '贝奇助手/43 CFNetwork/758.3.15 Darwin/15.4.0', '2016-04-23 09:36:54', '27.24.29.231', NULL, NULL, NULL, NULL, NULL, NULL, NULL);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
