
-- new in v10.0
ALTER TABLE `<TABLE_PREFIX>-writing-stats` ADD is_ta int ;

-- new in v10.1
UPDATE `<TABLE_PREFIX>-users` SET `cli`=1 WHERE  `default`=1;

-- new in v17.0
ALTER TABLE `<TABLE_PREFIX>-users` ADD apikey_id VARCHAR(200) ;
ALTER TABLE `<TABLE_PREFIX>-users` ADD apikey_secret VARCHAR(200) ;
