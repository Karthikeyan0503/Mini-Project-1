import sqlite3
#import mysql
import pandas as pd

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel (
            channel_id VARCHAR(255) PRIMARY KEY,
            channel_name VARCHAR(255),
            channel_views INT,
            channel_description TEXT,
            channel_status VARCHAR(255),
            subscriber_count INT,
            video_count INT,
            playlist_Id VARCHAR(255)    
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video (
            video_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255),  -- Foreign key referencing Channel table
            video_title VARCHAR(255),
            video_description TEXT,
            video_upload_date DATETIME,
            video_comment_count INT,
            video_views INT,
            video_likes INT,
            video_dislikes INT,
            duration INT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comment (
            comment_id VARCHAR(255) PRIMARY KEY,
            video_id VARCHAR(255),  -- Foreign key referencing Video table
            comment_text TEXT,
            comment_author VARCHAR(255),
            comment_published_date DATETIME
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlist (
            channel_id VARCHAR(255) PRIMARY KEY,
            playlist_name VARCHAR(255),
            playlist_Id VARCHAR(255)    
        )
    ''')
    conn.commit()

def insert_data(df, table_name):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    create_tables(conn)    
    data_tuples = tuple(df.to_records(index=False))
    column_names = tuple(df.columns)
    cursor.executemany(f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({', '.join(['?'] * len(column_names))})", data_tuples)
    conn.commit()


# def insert_data_sql(df, table_name):
#     try:
#         mydb = mysql.connector.connect(
#                             host="localhost",
#                             user="root",
#                             password="123456789",
#                             database="MAB2"
#                         )

#         mycursor = mydb.cursor()
#         for index, row in df.iterrows():
#             sql = "INSERT INTO " + table_name + " VALUES ("
#             sql += ", ".join(["%s"] * len(row)) + ")"
#             val = tuple(row)
#             mycursor.execute(sql, val)
#         mydb.commit()
#         mycursor.close()
#         mydb.close()
#     except mysql.connector.Error as error:
#         if error.errno == 1062:
#             print(f"Table {table_name} already exists or has duplicate entries.")
#         else:
#             print(f"Failed to insert data into {table_name}: {error}")
    
def fetch_data_from_db(query):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    df = pd.DataFrame(data, columns=column_names)
    conn.close()
    return df


def delete_data_from_db(query):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()