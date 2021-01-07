CREATE TABLE script (
	script_id integer PRIMARY KEY AUTOINCREMENT,
	script_name text,
	script_description text,
	script_author text,
	script_beg_date datetime,
	script_end_date datetime,
	script_hash blob,
	object_type_id integer,
	FOREIGN KEY (object_type_id) REFERENCES object_type(object_type_id)
);

CREATE UNIQUE INDEX uidx_script_name
on script (script_name);

CREATE TABLE user (
	user_id integer PRIMARY KEY AUTOINCREMENT,
	user_name text
);

CREATE UNIQUE INDEX uidx_user_name
on user (user_name);

CREATE TABLE fact_check (
	fact_check_id integer PRIMARY KEY AUTOINCREMENT,
	fact_check_date datetime,
	fact_check_obj_count integer,
	user_script_link_id integer,
	fact_check_is_finished integer,
	FOREIGN KEY (user_script_link_id) REFERENCES user_script_link(user_script_link_id)
);

CREATE TABLE object_type (
	object_type_id integer PRIMARY KEY AUTOINCREMENT,
	object_type_name text
);

CREATE UNIQUE INDEX uidx_object_type_name
on object_type (object_type_name);

CREATE TABLE error_level (
	error_level_id integer PRIMARY KEY AUTOINCREMENT,
	error_level_name text
);

CREATE UNIQUE INDEX uidx_error_level_name
on error_level (error_level_name);

CREATE TABLE object (
	object_id integer PRIMARY KEY AUTOINCREMENT,
	object_name text,
	object_identifier text,
	object_comment text,
	object_author text,
	object_date datetime,
	fact_check_id integer,
	error_level_id integer,
	FOREIGN KEY (fact_check_id) REFERENCES fact_check(fact_check_id),
	FOREIGN KEY (error_level_id) REFERENCES error_level(error_level_id)
);

CREATE TABLE user_script_link (
	user_script_link integer PRIMARY KEY AUTOINCREMENT,
	user_id integer,
	script_id integer,
	user_script_link_beg_date datetime,
	user_script_link_end_date datetime,
	FOREIGN KEY (script_id) REFERENCES script(script_id),
	FOREIGN KEY (user_id) REFERENCES user(user_id)
);

