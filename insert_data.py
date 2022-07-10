import psycopg2

def main():
    try:

        con = psycopg2.connect(user="",
                                                                                                                                                                password="2zDtGzz98aJDFrN8qU",
                           host="web0.eecs.uottawa.ca",
                           port="",
                           dbname="group")
        print("Successfully connected to database.")

        cursor = con.cursor()
        file = open('deleteTables.txt', 'r')
        s = file.read()
        cursor.execute("SET search_path = project_deliverable; " + s)
        con.commit()
        print("Previously existing tables deleted successfully.")
        file = open('createTablesandTriggers.txt', 'r')
        s = file.read()
        cursor.execute("SET search_path = project_deliverable; " + s)
        con.commit()
        print("All tables, triggers and functions created successfully.")
        populate_tables(con, cursor)
        con.close()
        print("All data inserted.")
    except Exception as e:
        print("Failed to connect to database.")
        print(e)


def populate_tables(con, cursor):

    file = open('insertalldata.txt', 'r')
    s = file.read()
    cursor.execute("SET search_path = project_deliverable; " + s)
    con.commit()


if __name__ == '__main__':
    main()


