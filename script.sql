-- ============================================================
-- 图书借阅管理系统 - 数据库初始化脚本
-- 数据库: MySQL 5.7+ / 8.0+
-- 字符集: utf8mb4
-- 说明: 直接在 MySQL 中执行本脚本即可完成建库建表和初始化
-- ============================================================

-- 创建数据库
DROP DATABASE IF EXISTS `library_db`;
CREATE DATABASE `library_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `library_db`;

-- 删除已存在的表（按依赖逆序，避免外键约束冲突）
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `favorite`;
DROP TABLE IF EXISTS `borrow_record`;
DROP TABLE IF EXISTS `book`;
DROP TABLE IF EXISTS `category`;
DROP TABLE IF EXISTS `user`;
SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;

-- ============================================================
-- 1. 用户表 user
-- ============================================================
CREATE TABLE `user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户唯一标识',
  `username` VARCHAR(50) NOT NULL COMMENT '登录用户名（唯一）',
  `password` VARCHAR(100) NOT NULL COMMENT '登录密码（bcrypt 哈希存储，不存明文）',
  `role` ENUM('admin','reader') NOT NULL DEFAULT 'reader' COMMENT '角色：admin 管理员 / reader 读者',
  `real_name` VARCHAR(50) NOT NULL COMMENT '真实姓名',
  `phone` VARCHAR(20) NOT NULL COMMENT '手机号（11 位）',
  `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
  `contact` VARCHAR(200) DEFAULT NULL COMMENT '备用联系方式（可选）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表（管理员与读者）';

-- ============================================================
-- 2. 分类表 category
-- ============================================================
CREATE TABLE `category` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '分类唯一标识',
  `name` VARCHAR(50) NOT NULL COMMENT '分类名称（唯一，如：文学、科技）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书分类表';

-- ============================================================
-- 3. 图书表 book
-- ============================================================
CREATE TABLE `book` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '图书唯一标识',
  `title` VARCHAR(200) NOT NULL COMMENT '书名（必填）',
  `author` VARCHAR(100) NOT NULL COMMENT '作者（必填）',
  `isbn` VARCHAR(20) NOT NULL COMMENT 'ISBN 编号（必填，唯一）',
  `category_id` BIGINT NOT NULL COMMENT '分类 ID（外键，关联 category.id）',
  `publisher` VARCHAR(100) DEFAULT NULL COMMENT '出版社',
  `publish_year` INT DEFAULT NULL COMMENT '出版年份',
  `total_count` INT NOT NULL DEFAULT 1 COMMENT '总馆藏数量（>=1）',
  `available_count` INT NOT NULL DEFAULT 1 COMMENT '可借数量（0 <= available_count <= total_count）',
  `summary` TEXT DEFAULT NULL COMMENT '简介（选填）',
  `cover_url` VARCHAR(500) DEFAULT NULL COMMENT '封面图片地址（选填，本地上传或 URL）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_isbn` (`isbn`),
  KEY `idx_category_id` (`category_id`),
  KEY `idx_title_author` (`title`, `author`),
  CONSTRAINT `fk_book_category` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书表';

-- ============================================================
-- 4. 借阅记录表 borrow_record
-- ============================================================
CREATE TABLE `borrow_record` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '记录唯一标识',
  `user_id` BIGINT NOT NULL COMMENT '借阅读者 ID（外键，关联 user.id）',
  `book_id` BIGINT NOT NULL COMMENT '所借图书 ID（外键，关联 book.id）',
  `borrow_time` DATETIME NOT NULL COMMENT '借出时间',
  `due_time` DATETIME NOT NULL COMMENT '应还时间（借出时间 + 借期 30 天）',
  `return_time` DATETIME DEFAULT NULL COMMENT '实际归还时间（未归还时为 NULL）',
  `status` ENUM('borrowed','returned','overdue') NOT NULL DEFAULT 'borrowed' COMMENT '状态：borrowed 借阅中 / returned 已归还 / overdue 逾期',
  `operator_id` BIGINT DEFAULT NULL COMMENT '办理归还的操作人 ID（读者自助归还=本人；管理员办理=对应管理员）',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_book_id` (`book_id`),
  KEY `idx_status` (`status`),
  KEY `idx_borrow_time` (`borrow_time`),
  CONSTRAINT `fk_record_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_record_book` FOREIGN KEY (`book_id`) REFERENCES `book` (`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_record_operator` FOREIGN KEY (`operator_id`) REFERENCES `user` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='借阅记录表（借还业务凭据，永久保留）';

-- ============================================================
-- 5. 收藏记录表 favorite
-- ============================================================
CREATE TABLE `favorite` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '收藏记录唯一标识',
  `user_id` BIGINT NOT NULL COMMENT '收藏读者 ID（外键，关联 user.id）',
  `book_id` BIGINT NOT NULL COMMENT '被收藏图书 ID（外键，关联 book.id）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_book` (`user_id`, `book_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_book_id` (`book_id`),
  CONSTRAINT `fk_fav_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_fav_book` FOREIGN KEY (`book_id`) REFERENCES `book` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏记录表（同一读者对同一图书仅一条，图书删除时级联删除）';

-- ============================================================
-- 初始数据插入
-- ============================================================

-- ---------- 用户数据 ----------
-- 管理员账号: admin / 123456 （密码使用 bcrypt 哈希存储）
-- 哈希值由 Python bcrypt.hashpw('123456', gensalt()) 生成
INSERT INTO `user` (`username`, `password`, `role`, `real_name`, `phone`, `email`, `contact`) VALUES
('admin', '$2b$12$/BW4Ec7IpZd4s1U2SwzfD.e1MHw5WQ4Sa4Ww3mYjmbduI.5puZoG.', 'admin', '系统管理员', '13800000001', 'admin@library.com', NULL),
('reader1', '$2b$12$/BW4Ec7IpZd4s1U2SwzfD.e1MHw5WQ4Sa4Ww3mYjmbduI.5puZoG.', 'reader', '张三', '13800000002', 'zhangsan@library.com', NULL),
('reader2', '$2b$12$/BW4Ec7IpZd4s1U2SwzfD.e1MHw5WQ4Sa4Ww3mYjmbduI.5puZoG.', 'reader', '李四', '13800000003', 'lisi@library.com', NULL);

-- ---------- 分类数据 ----------
INSERT INTO `category` (`id`, `name`) VALUES
(1, '文学'),
(2, '科技'),
(3, '历史'),
(4, '计算机'),
(5, '艺术');

-- ---------- 图书数据 ----------
INSERT INTO `book` (`id`, `title`, `author`, `isbn`, `category_id`, `publisher`, `publish_year`, `total_count`, `available_count`, `summary`, `cover_url`) VALUES
(1, '红楼梦', '曹雪芹', '9787020002207', 1, '人民文学出版社', 1996, 5, 3, '中国古典四大名著之一，描写贾府兴衰。', NULL),
(2, '三体', '刘慈欣', '9787536692930', 2, '重庆出版社', 2008, 4, 4, '中国科幻里程碑，讲述人类文明与三体文明的故事。', NULL),
(3, '人类简史', '尤瓦尔·赫拉利', '9787508647357', 3, '中信出版社', 2014, 3, 2, '从认知革命到科学革命，重新审视人类历史。', NULL),
(4, '明朝那些事儿', '当年明月', '9787540461188', 3, '湖南人民出版社', 2009, 6, 6, '以通俗笔法讲述明朝三百年兴衰。', NULL),
(5, '苏菲的世界', '乔斯坦·贾德', '9787544263566', 1, '南海出版公司', 2011, 2, 1, '一本西方哲学史的入门小说。', NULL),
(6, '西游记', '吴承恩', '9787020008704', 1, '人民文学出版社', 2004, 3, 3, '四大名著之一，讲述唐僧师徒西天取经。', NULL),
(7, '时间简史', '史蒂芬·霍金', '9787535732309', 2, '湖南科学技术出版社', 2010, 2, 0, '探索宇宙起源与时间本质的科普经典。', NULL),
(8, '深入理解计算机系统', 'Randal E. Bryant', '9787111544937', 4, '机械工业出版社', 2016, 2, 2, '从程序员的视角理解计算机系统的工作原理。', NULL),
(9, '艺术的故事', '贡布里希', '9787549550869', 5, '广西美术出版社', 2008, 2, 2, '西方艺术史的经典入门读物。', NULL),
(10, '自然的艺术形态', '恩斯特·海克尔', '9787555104515', 2, '广西科学技术出版社', 2015, 1, 1, '展示自然界生物的对称之美与艺术形态。', NULL);

-- ---------- 借阅记录数据 ----------
-- 为 reader1 (user_id=2) 制造一条逾期记录（40 天前借出，应还时间已过）和一条正常借阅记录
INSERT INTO `borrow_record` (`user_id`, `book_id`, `borrow_time`, `due_time`, `return_time`, `status`, `operator_id`) VALUES
-- 逾期记录：红楼梦，40天前借出，应还时间为10天前，未归还
(2, 1, DATE_SUB(NOW(), INTERVAL 40 DAY), DATE_SUB(NOW(), INTERVAL 40 DAY) + INTERVAL 30 DAY, NULL, 'overdue', 2),
-- 正常借阅：人类简史，10天前借出，20天后到期
(2, 3, DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_SUB(NOW(), INTERVAL 10 DAY) + INTERVAL 30 DAY, NULL, 'borrowed', 2),
-- 已归还记录：西游记，60天前借出，35天前归还
(2, 6, DATE_SUB(NOW(), INTERVAL 60 DAY), DATE_SUB(NOW(), INTERVAL 60 DAY) + INTERVAL 30 DAY, DATE_SUB(NOW(), INTERVAL 35 DAY), 'returned', 2);

-- ---------- 收藏记录数据 ----------
-- reader1 (user_id=2) 收藏了三体和苏菲的世界
INSERT INTO `favorite` (`user_id`, `book_id`) VALUES
(2, 2),
(2, 5);

-- ============================================================
-- 重置自增起始值（确保后续插入从合适的位置开始）
-- ============================================================
ALTER TABLE `user`     AUTO_INCREMENT = 4;
ALTER TABLE `category` AUTO_INCREMENT = 6;
ALTER TABLE `book`     AUTO_INCREMENT = 11;
ALTER TABLE `borrow_record` AUTO_INCREMENT = 4;
ALTER TABLE `favorite` AUTO_INCREMENT = 3;

-- ============================================================
-- 验证：查询初始化结果
-- ============================================================
SELECT '===== 数据库初始化完成 =====' AS info;

SELECT CONCAT('用户数: ', COUNT(*)) AS info FROM `user`;
SELECT CONCAT('分类数: ', COUNT(*)) AS info FROM `category`;
SELECT CONCAT('图书数: ', COUNT(*)) AS info FROM `book`;
SELECT CONCAT('借阅记录数: ', COUNT(*)) AS info FROM `borrow_record`;
SELECT CONCAT('收藏记录数: ', COUNT(*)) AS info FROM `favorite`;

SELECT '----- 用户列表 -----' AS info;
SELECT id, username, role, real_name, phone, email FROM `user`;

SELECT '----- 分类列表 -----' AS info;
SELECT id, name, created_at FROM `category`;

SELECT '----- 图书列表 -----' AS info;
SELECT id, title, author, isbn, category_id, total_count, available_count FROM `book`;

SELECT '----- 借阅记录 -----' AS info;
SELECT id, user_id, book_id, borrow_time, due_time, return_time, status FROM `borrow_record`;

SELECT '----- 收藏记录 -----' AS info;
SELECT id, user_id, book_id, created_at FROM `favorite`;
