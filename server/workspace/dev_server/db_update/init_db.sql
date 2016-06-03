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
-- 表的结构 `device_info`
--
DROP TABLE IF EXISTS `device_info`;

CREATE TABLE `device_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sn` varchar(20) NOT NULL,
  `gid` varchar(10) DEFAULT NULL,
  `nice_gid` varchar(10) DEFAULT NULL,
  `factory` varchar(15) DEFAULT NULL,
  `dev_model` varchar(10) DEFAULT NULL,
  `dev_type` varchar(10) DEFAULT NULL,
  `soft_version` varchar(10) DEFAULT NULL,
  `status` varchar(10) NOT NULL,
  `primary` varchar(30) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `production_date` datetime DEFAULT NULL,
  `saved_ts` datetime NOT NULL,
  `remarks` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sn` (`sn`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=56 ;

--
-- 转存表中的数据 `device_info`
--

INSERT INTO `device_info` (`id`, `sn`, `gid`, `nice_gid`, `factory`, `dev_model`, `dev_type`, `soft_version`, `status`, `primary`, `mobile`, `production_date`, `saved_ts`, `remarks`) VALUES
(1, 'P081101551000001', '477823', '', '福州自组装', 'P108', 'HomePad', '0.9.0', 'binded', '18060992926@jiashu.com', '18060992926', '2016-01-15 09:05:31', '2016-03-31 07:08:41', ''),
(2, 'P081101551000002', '359998', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-03-31 07:08:41', ''),
(3, 'P081101551000003', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-03-31 07:08:41', ''),
(4, 'P081101551000004', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'unbound', '', '', '2016-01-15 09:05:31', '2016-03-31 07:08:41', ''),
(5, 'P081101551000005', '301078', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'binded', '13635276132@jiashu.com', '13635276132', '2016-01-15 09:05:31', '2016-03-31 07:08:41', ''),
(6, 'P081101551000006', '109595', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'binded', '18606092764@jiashu.com', '18606092764', '2016-01-15 09:05:31', '2016-03-31 07:08:41', ''),
(7, 'P081101551000007', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-03-31 07:08:41', ''),
(8, 'P081101551000008', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-03-31 07:08:41', ''),
(9, 'P081101551000009', '447847', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'unbound', '', '', '2016-01-15 09:05:31', '2016-03-31 07:08:41', ''),
(10, 'P081101551000010', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-03-31 07:08:41', ''),
(11, 'P081101551000011', '488873', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-03-31 07:36:02', ''),
(12, 'P081101551000012', '410162', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'binded', '15750701209@jiashu.com', '15750701209', '2016-01-15 09:05:31', '2016-03-31 07:36:02', ''),
(13, 'P081101551000013', '426613', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'unbound', '', '', '2016-01-15 09:05:31', '2016-03-31 07:36:02', ''),
(14, 'P081101551000014', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'binded', '18650089855@jiashu.com', '18650089855', '2016-01-15 09:05:31', '2016-03-31 07:36:02', ''),
(15, 'P081101551000015', '308051', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-03-31 07:36:02', ''),
(16, 'P081101551000016', '862546', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'binded', '15606913317@jiashu.com', '15606913317', '2016-01-15 09:05:31', '2016-03-31 07:36:02', ''),
(17, 'P081101551000017', '518336', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'binded', '13559937192@jiashu.com', '13559937192', '2016-01-15 09:05:31', '2016-03-31 07:36:02', ''),
(18, 'P081101551000018', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-03-31 07:36:02', ''),
(19, 'P081101551000019', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-03-31 07:36:02', ''),
(20, 'P081101551000020', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-03-31 07:36:02', ''),
(21, 'P081101535000001', '528204', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'unbound', '', '', '2016-01-15 09:05:31', '2016-04-01 12:26:33', ''),
(22, 'P081101535000002', '823969', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', 'binded', '13124070068@jiashu.com', '13124070068', '2016-01-15 09:05:31', '2016-04-01 12:26:33', ''),
(23, 'P081101535000003', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-04-01 12:26:33', ''),
(24, 'P081101535000004', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-04-01 12:26:33', ''),
(25, 'P081101535000005', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-04-01 12:26:33', ''),
(26, 'P081101535000006', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-04-01 12:26:33', ''),
(27, 'P081101535000007', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-04-01 12:26:33', ''),
(28, 'P081101535000008', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-04-01 12:26:33', ''),
(29, 'P081101535000009', '', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-04-01 12:26:33', ''),
(30, 'P081101535000010', '622411', NULL, '福州自组装', 'P108', 'HomePad', '0.9.0', '', '', '', '2016-01-15 09:05:31', '2016-04-01 12:26:33', ''),
(31, '0123456789ABCDEF', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-18 11:55:31', '2016-05-18 11:55:31', ''),
(32, '0123456790ABCDE1', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-18 11:55:32', '2016-05-18 11:55:32', ''),
(33, '0123456790ABCDE2', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-18 11:55:33', '2016-05-18 11:55:33', ''),
(34, '0123456790ABCDE3', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-18 11:55:34', '2016-05-18 11:55:34', ''),
(35, '0123456790ABCDE4', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-18 11:55:35', '2016-05-18 11:55:35', ''),
(36, '0123456790ABCDE5', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-18 11:55:36', '2016-05-18 11:55:36', ''),
(37, '0123456790ABCDE6', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-18 11:55:37', '2016-05-18 11:55:37', ''),
(38, '0123456790ABCDE7', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-18 11:55:38', '2016-05-18 11:55:38', ''),
(39, '0123456790ABCDE8', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-18 11:55:39', '2016-05-18 11:55:39', ''),
(40, '0123456790ABCDE9', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-18 11:55:40', '2016-05-18 11:55:40', ''),
(45, 'P081101535000011', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', ''),
(46, 'P081101535000012', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', ''),
(47, 'P081101535000013', '161272', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', ''),
(48, 'P081101535000014', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', ''),
(49, 'P081101535000015', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', ''),
(50, 'P081101535000016', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', ''),
(51, 'P081101535000017', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', ''),
(52, 'P081101535000018', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', ''),
(53, 'P081101535000019', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', ''),
(54, 'P081101535000020', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', ''),
(55, 'P081101535000021', '', '', '演示设备', 'P108', 'BeiqiPad', '0.9.0', '', '', '', '2016-05-24 11:55:31', '2016-05-24 11:55:31', '');

-- --------------------------------------------------------

--
-- 表的结构 `dev_state`
--
DROP TABLE IF EXISTS `dev_state`;

CREATE TABLE `dev_state` (
  `pid` char(10) DEFAULT NULL,
  `sn` char(16) DEFAULT NULL,
  `dev_type` varchar(10) DEFAULT NULL,
  `src_ts` datetime DEFAULT NULL,
  `battery` tinyint(4) DEFAULT NULL,
  `charge` tinyint(4) DEFAULT NULL,
  `soft_ver` varchar(10) DEFAULT NULL,
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `dev_state`
--



-- --------------------------------------------------------

--
-- 表的结构 `gid_info`
--
DROP TABLE IF EXISTS `gid_info`;

CREATE TABLE `gid_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gid` int(10) unsigned NOT NULL,
  `sn` varchar(20) DEFAULT NULL,
  `gid_kind` smallint(6) NOT NULL,
  `status` varchar(10) DEFAULT NULL,
  `remarks` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=900001 ;

--
-- 转存表中的数据 `gid_info`
--


-- --------------------------------------------------------

--
-- 表的结构 `location`
--
DROP TABLE IF EXISTS `location`;

CREATE TABLE `location` (
  `pid` char(10) DEFAULT NULL,
  `sn` char(17) DEFAULT NULL,
  `dev_type` varchar(10) DEFAULT NULL,
  `src_ts` datetime NOT NULL,
  `loc_type` tinyint(4) DEFAULT NULL,
  `provider` char(10) DEFAULT NULL,
  `address` varchar(80) DEFAULT NULL,
  `country` varchar(20) DEFAULT NULL,
  `province` varchar(20) DEFAULT NULL,
  `city` varchar(20) DEFAULT NULL,
  `district` varchar(20) DEFAULT NULL,
  `road` varchar(30) DEFAULT NULL,
  `ad_code` char(6) DEFAULT NULL,
  `zip_code` char(6) DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `altitude` smallint(5) unsigned DEFAULT NULL,
  `accuracy` smallint(5) unsigned DEFAULT NULL,
  `saved_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `location`
--

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
