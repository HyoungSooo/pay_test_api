-- Create model User
--
CREATE TABLE `account_user` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `password` varchar(128) NOT NULL, `last_login` datetime(6) NULL, `is_superuser` bool NOT NULL, `first_name` varchar(150) NOT NULL, `last_name` varchar(150) NOT NULL, `email` varchar(254) NOT NULL, `is_staff` bool NOT NULL, `is_active` bool NOT NULL, `date_joined` datetime(6) NOT NULL, `username` varchar(10) NULL, `phone_number` varchar(13) NOT NULL UNIQUE);
CREATE TABLE `account_user_groups` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `user_id` bigint NOT NULL, `group_id` integer NOT NULL);
CREATE TABLE `account_user_user_permissions` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `user_id` bigint NOT NULL, `permission_id` integer NOT NULL);
ALTER TABLE `account_user_groups` ADD CONSTRAINT `account_user_groups_user_id_group_id_4d09af3e_uniq` UNIQUE (`user_id`, `group_id`);
ALTER TABLE `account_user_groups` ADD CONSTRAINT `account_user_groups_user_id_14345e7b_fk_account_user_id` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`);
ALTER TABLE `account_user_groups` ADD CONSTRAINT `account_user_groups_group_id_6c71f749_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);
ALTER TABLE `account_user_user_permissions` ADD CONSTRAINT `account_user_user_permis_user_id_permission_id_48bdd28b_uniq` UNIQUE (`user_id`, `permission_id`);
ALTER TABLE `account_user_user_permissions` ADD CONSTRAINT `account_user_user_pe_user_id_cc42d270_fk_account_u` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`);
ALTER TABLE `account_user_user_permissions` ADD CONSTRAINT `account_user_user_pe_permission_id_66c44191_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);

-- Create model Product
--
CREATE TABLE `api_product` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `category` varchar(30) NOT NULL, `price` integer NOT NULL, `cost` integer NOT NULL, `name` varchar(20) NOT NULL UNIQUE, `des` longtext NOT NULL, `barcode` varchar(100) NOT NULL, `expiration_date` datetime(6) NOT NULL, `size` varchar(1) NOT NULL, `initial_set` varchar(20) NULL);