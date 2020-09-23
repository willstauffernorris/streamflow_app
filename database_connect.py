import os
import psycopg2
import psycopg2.extras as extras
import pandas as pd
# from dotenv import load_dotenv



df = pd.read_csv("data/generated_latest_flows.csv", index_col=0)
print(df)

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

#####create my 'flow' table######
####Only need to do this once####
# cursor=conn.cursor()
# cursor.execute(
# """
# CREATE TABLE flow (
#    id SERIAL PRIMARY KEY,
#    Observation FLOAT,
#    date DATE,
#    lat FLOAT,
#    lon FLOAT,
#    station VARCHAR,
#    Forecast FLOAT
# );
# """)
# cursor.close()
###########################


def delete_existing_and_execute_values(conn, df, table):
    """
    Using psycopg2.extras.execute_values() to insert the dataframe
    """
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]
    # Comma-separated dataframe columns
    cols = ','.join(list(df.columns))
    # SQL quert to execute
    query  = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM {table}")
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("execute_values() done")
    cursor.close()


# calling the function
delete_existing_and_execute_values(conn, df, 'flow')


#     # Print PostgreSQL Connection properties
# print(conn.get_dsn_parameters(),"\n")

#     # Print PostgreSQL version
# cursor.execute("SELECT version();")
# record = cursor.fetchone()
# print("You are connected to - ", record,"\n")






# cursor.execute("INSERT INTO flow_mapping (Observation, date) VALUES (%s, %s)",(344,"2020-09-21"))

# # cursor.execute("CREATE TABLE flow_mapping (id serial PRIMARY KEY, Observation float, date varchar);")
# cursor.execute("INSERT INTO flow_mapping (Observation, date) VALUES (%s, %s)",(344,"2020-09-21"))

# # Query the database and obtain data as Python objects
# cursor.execute("SELECT * FROM test;")
# print(cursor.fetchall())
# # (1, 100, "abc'def")
# conn.commit()

# count = cursor.rowcount
# print(count, "Record inserted successfully into mobile table")



