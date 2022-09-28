import sqlite3
import pathlib


def check_db():
    database = pathlib.Path('content.db')
    print(database)
    if database.exists() == False:
        create_db()
        print('db has been created')
    else:
        print('db passed')
        pass


def create_db():
    connection = sqlite3.connect("content.db")
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE users
                      (user_id integer,
                      name text,
                      phone  integer)
                   """)

    connection.commit()

    cursor.execute("""CREATE TABLE company
                      (name text,
                       admin_id interer,
                       worker_id integer,
                       goal text,
                       otdel text)
                   """)
    connection.commit()

    cursor.execute("""CREATE TABLE workers
                      (name text,
                       user_id,
                       worker_id text,
                       goal text)
                   """)


    # у каждого своя таблица (?)
    # cursor.execute("""CREATE TABLE workspace
    #                   (name text,
    #                    text text)
    #                """)
    # connection.commit()
    #
    # cursor.execute("""CREATE TABLE articles
    #                   (
    #                   name text,
    #                   text text)
    #                """)
    #
    # connection.commit()


