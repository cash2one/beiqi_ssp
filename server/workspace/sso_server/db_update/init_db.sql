-- phpMyAdmin SQL Dump
-- version 3.4.10.1deb1
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2016 年 06 月 03 日 13:53
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
-- 表的结构 `ssp_user_login`
--

DROP TABLE IF EXISTS `ssp_user_login`;
CREATE TABLE `ssp_user_login` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `password` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=37 ;

--
-- 转存表中的数据 `ssp_user_login`
--

INSERT INTO `ssp_user_login` (`id`, `username`, `mobile`, `password`) VALUES
(1, '18650089855@jiashu.com', '18650089855', '2jmj7l5rSw0yVb/vlWAYkK/YBwk='),
(2, '13559937192@jiashu.com', '13559937192', 'fEqNCco3Yq9h5ZUglD3CZJT4lBs='),
(3, '13685011233@jiashu.com', '13685011233', 'PU8r8H3BvjiyDNbkaUmhBx+dDj0='),
(4, '13124070068@jiashu.com', '13124070068', 'fEqNCco3Yq9h5ZUglD3CZJT4lBs='),
(5, '18606092764@jiashu.com', '18606092764', 'fEqNCco3Yq9h5ZUglD3CZJT4lBs='),
(6, '15606913317@jiashu.com', '15606913317', 'fCIvspJ9goryL1khNOiTJIBjfA0='),
(7, '18606919996@jiashu.com', '18606919996', 'fCIvspJ9goryL1khNOiTJIBjfA0='),
(8, '18559279649@jiashu.com', '18559279649', 'fEqNCco3Yq9h5ZUglD3CZJT4lBs='),
(9, '13635276132@jiashu.com', '13635276132', 'fEqNCco3Yq9h5ZUglD3CZJT4lBs='),
(10, '13338283996@jiashu.com', '13338283996', 'i8Xeg88dr3ntWy8T+T18BdAdA4g='),
(11, '18941860177@jiashu.com', '18941860177', 'QpF7P+Z6/BPWEkdHsL+yxaTLY8g='),
(12, '15266589980@jiashu.com', '15266589980', 'fY9LS0YT3H4VMz5kSWkq1K9QLR0='),
(13, '15640644795@jiashu.com', '15640644795', '6W5mRkWmzeqAqoCRmfap0ph2hNI='),
(14, '18796691180@jiashu.com', '18796691180', 'HJBsMdAxxpsaPakWsL235AzBf24='),
(15, '13604175056@jiashu.com', '13604175056', 'ar+u1bwKZM2oFUYALo/SczsSd8c='),
(16, '18603340696@jiashu.com', '18603340696', 'G5c4izRs4A35JqPWO94lDCwsMkQ='),
(17, '18434652376@jiashu.com', '18434652376', '4KFX1Uks62r60+cCBzXZv1xwIEI='),
(18, '15257091072@jiashu.com', '15257091072', 'k+xxsieTqBVpyUyhfk2cKT2OIB8='),
(19, '15881783081@jiashu.com', '15881783081', 'ksUD7Wycz/vCiru3AewQqi84O10='),
(20, '13915789234@jiashu.com', '13915789234', 'xUOyEllXFOgvu5LCuDSQh3F0Uew='),
(21, '18080724446@jiashu.com', '18080724446', 'C7Zp4fS7fgFyGd2EUfw6tDpbNLA='),
(22, '18091203849@jiashu.com', '18091203849', 'fEqNCco3Yq9h5ZUglD3CZJT4lBs='),
(23, '18219021210@jiashu.com', '18219021210', 'TZX2ss/T0txEEfo2KrjtzNDkKEY='),
(24, '13154484558@jiashu.com', '13154484558', 'VxrQ99UFb2jQ8reV6vRhjAgqidk='),
(25, '18218358800@jiashu.com', '18218358800', 'o5weh4Yt9aOdQYkw9i2I8IRpnIk='),
(26, '13719996134@jiashu.com', '13719996134', 'fEqNCco3Yq9h5ZUglD3CZJT4lBs='),
(27, '13589679842@jiashu.com', '13589679842', '7mnMU6CWWFOkYSrmKd/QToOKIjM='),
(28, '18911335392@jiashu.com', '18911335392', 'SWSWSrqUYnE7FkHhvrJv5trpmiw='),
(29, '18081289099@jiashu.com', '18081289099', 'vSmGRc2/9S0sLDdyH3opGTkFaIM='),
(30, '13971731786@jiashu.com', '13971731786', 'ewKfZphDvXGBNVhrY4+B7Ll7+rY='),
(31, '13952957331@jiashu.com', '13952957331', 'ooEyAL1ZSgmcT9XggJTkW2G9J2Y='),
(32, '13556653860@jiashu.com', '13556653860', 'fEqNCco3Yq9h5ZUglD3CZJT4lBs='),
(33, '18240486005@jiashu.com', '18240486005', 'ofu0uX72bC4Y/e68/I8+ZsWGTYU='),
(34, '18671400751@jiashu.com', '18671400751', '98O8HYCOBHMq32eZZczDTKeuNEE='),
(35, '18610060484@jiashu.com', '18610060484', 'bDPU1RRGIxpkK4YKdxfvQSrkdvY='),
(36, '15806034557@jiashu.com', '15806034557', 'fEqNCco3Yq9h5ZUglD3CZJT4lBs=');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
