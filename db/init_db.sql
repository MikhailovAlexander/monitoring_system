CREATE TABLE script (
	script_id integer PRIMARY KEY AUTOINCREMENT,
	script_name text NOT NULL,
	script_description text NOT NULL,
	script_author text NOT NULL,
	script_beg_date datetime NOT NULL,
	script_end_date datetime,
	script_hash blob NOT NULL,
	object_type_id integer NOT NULL,
	FOREIGN KEY (object_type_id) REFERENCES object_type(object_type_id)
);

CREATE UNIQUE INDEX uidx_script_name
on script (script_name);

CREATE TABLE user (
	user_id integer PRIMARY KEY AUTOINCREMENT,
	user_name text NOT NULL
);

CREATE UNIQUE INDEX uidx_user_name
on user (user_name);

CREATE TABLE fact_check_status (
	fact_check_status_id integer PRIMARY KEY AUTOINCREMENT,
	fact_check_status_name text NOT NULL
);

CREATE UNIQUE INDEX uidx_fact_check_status
on fact_check_status (fact_check_status_name);

CREATE TABLE fact_check (
	fact_check_id integer PRIMARY KEY AUTOINCREMENT,
	fact_check_que_date datetime NOT NULL,
	fact_check_end_date datetime,
	fact_check_obj_count integer,
	user_script_link_id integer NOT NULL,
	fact_check_status_id integer NOT NULL,
	FOREIGN KEY (user_script_link_id) REFERENCES user_script_link(user_script_link_id),
	FOREIGN KEY (fact_check_status_id) REFERENCES fact_check_status(fact_check_status_id)
);

CREATE UNIQUE INDEX uidx_fact_check_composite
on fact_check (fact_check_que_date, user_script_link_id);

CREATE TABLE object_type (
	object_type_id integer PRIMARY KEY AUTOINCREMENT,
	object_type_name text NOT NULL
);

CREATE UNIQUE INDEX uidx_object_type_name
on object_type (object_type_name);

CREATE TABLE error_level (
	error_level_id integer PRIMARY KEY AUTOINCREMENT,
	error_level_name text NOT NULL
);

CREATE UNIQUE INDEX uidx_error_level_name
on error_level (error_level_name);

CREATE TABLE object (
	object_id integer PRIMARY KEY AUTOINCREMENT,
	object_name text NOT NULL,
	object_identifier text NOT NULL,
	object_comment text,
	object_author text,
	object_date datetime NOT NULL,
	fact_check_id integer NOT NULL,
	error_level_id integer NOT NULL,
	FOREIGN KEY (fact_check_id) REFERENCES fact_check(fact_check_id),
	FOREIGN KEY (error_level_id) REFERENCES error_level(error_level_id)
);

CREATE UNIQUE INDEX uidx_object_composite
on object (object_name, object_identifier, fact_check_id, error_level_id);

CREATE TABLE user_script_link (
	user_script_link_id integer PRIMARY KEY AUTOINCREMENT,
	user_id integer NOT NULL,
	script_id integer NOT NULL,
	user_script_link_beg_date datetime NOT NULL,
	user_script_link_end_date datetime,
	FOREIGN KEY (script_id) REFERENCES script(script_id),
	FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE UNIQUE INDEX uidx_user_script_link_composite
on user_script_link (user_id, script_id, user_script_link_beg_date);

INSERT INTO user(user_name) VALUES('admin'),('test');
INSERT INTO object_type(object_type_name)
    VALUES('Файл'),('Запись в БД'),('Объект в БД');
INSERT INTO error_level(error_level_name)
    VALUES('trivial'),('warning'),('error');
INSERT INTO fact_check_status(fact_check_status_name)
    VALUES('В очереди'),('Выполнен'),('Завершен с ошибкой'),('Отменен');
INSERT INTO script(
	script_name,
	script_description,
	script_author,
	script_beg_date,
	script_hash,
	object_type_id) 
	VALUES(
		'TestCheck',
		'TestCheck',
		'AV Mikhaylov',
		CURRENT_TIMESTAMP,
		CAST(1 as BLOB),
		(SELECT object_type_id FROM object_type WHERE object_type_name = 'Файл')
	);
INSERT INTO user_script_link(
	user_id,
	script_id,
	user_script_link_beg_date) 
	VALUES
		((SELECT user_id FROM user WHERE user_name = 'admin'),
		(SELECT script_id FROM script WHERE script_name = 'TestCheck'),
		CURRENT_TIMESTAMP),
		((SELECT user_id FROM user WHERE user_name = 'test'),
		(SELECT script_id FROM script WHERE script_name = 'TestCheck'),
		CURRENT_TIMESTAMP);