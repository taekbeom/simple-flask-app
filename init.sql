CREATE TABLE user_role (
	id SERIAL PRIMARY KEY,
	role_name VARCHAR(16) NOT NULL UNIQUE
);

CREATE TABLE user_info (
	id SERIAL PRIMARY KEY,
	username VARCHAR(64) NOT NULL UNIQUE,
	"password" VARCHAR(256) NOT NULL,
	email VARCHAR(320) NOT NULL UNIQUE,
	user_role INTEGER REFERENCES user_role(id)
);

INSERT INTO user_role(role_name) VALUES('user'), ('admin');

CREATE OR REPLACE FUNCTION update_role_func ()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
	BEGIN
		IF NEW.user_role IS NULL THEN
			UPDATE user_info SET user_role = (SELECT id FROM user_role WHERE role_name = 'user')
			WHERE id = NEW.id;
		END IF;
		RETURN NEW;
	END;
$$;

CREATE TRIGGER update_role
	AFTER INSERT ON user_info
	FOR EACH ROW
	EXECUTE FUNCTION update_role_func();