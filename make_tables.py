from config import *

import psycopg2


def main():
    conn = psycopg2.connect(database=db_con_database, user=db_con_user,
                            password=db_con_password, host=db_con_host, port=db_con_port,
                            options=f'-c search_path={db_con_schema}')

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CREATE TABLE project (" +
                            "id SERIAL PRIMARY KEY, " +
                            "name character varying(255), " +
                            "description character varying(255) " +
                            ")")
                cur.execute("CREATE TABLE server (" +
                            "id SERIAL PRIMARY KEY, " +
                            "name character varying(255), " +
                            "ip_address character varying(100), " +
                            "description character varying(255) " +
                            ")")
                cur.execute("CREATE TABLE recognizing_results (" +
                            "\"date\" date, " +
                            "\"time\" time without time zone, " +
                            "id bigint PRIMARY KEY, " +
                            "result smallint, " +
                            "phone_number character varying(25), " +
                            "duration real, " +
                            "recognizing_result text, " +
                            "project_id integer, " +
                            "server_id integer, " +
                            ")")
                cur.execute("ALTER TABLE recognizing_results " +
                            "ADD CONSTRAINT fk_project " +
                            "FOREIGN KEY (project_id) " +
                            "REFERENCES project (id) "
                            )
                cur.execute("ALTER TABLE recognizing_results " +
                            "ADD CONSTRAINT fk_server " +
                            "FOREIGN KEY (server_id) " +
                            "REFERENCES server (id) "
                            )
    finally:
        conn.close()


if __name__ == '__main__':
    main()
