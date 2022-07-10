import psycopg2


def main():
    try:

        con = psycopg2.connect(user=, # Removed credentials
                               password=",
                               host="web0.eecs.uottawa.ca",
                               port="",
                               dbname="group_")
        print("Successfully connected to database.")
        while True:

            query = runsqlquery()
            if query:
                try:
                    cursor = con.cursor()
                    cursor.execute(query)
                    con.commit()
                    print("Query successful.")
                except Exception as e:
                    print("Invalid query.")
                    print(e)
            else:
                break

    except Exception as e:
        print("Failed to connect to database.")
        print(e)


def runsqlquery():
    query = input(
        "Enter sql query or press q to quit. Remember to start query with SET search_path = project deliverable; \n")
    if query.strip().lower() == 'q':
        return None
    else:
        return query




if __name__ == '__main__':
    main()
