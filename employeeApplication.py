import traceback

import psycopg2
import datetime
from datetime import timedelta

MINIMUM_RENTAL = 2


def start():
    try:

        con = psycopg2.connect(user=,
                               password=,
                               host="web0.eecs.uottawa.ca",
                               port=,
                               dbname=)
        print("Successfully connected to database.")
        archive_bookings_and_rentings(con)
        main_program(con)
        con.close()

    except Exception as e:
        print("Failed to connect to database.")
        print(e)
        print(traceback.format_exc())
        input("")


def main_program(con):
    employee_id, hotel_id = login_employee(con)
    print("employee id: " + str(employee_id), "hotel id : " + str(hotel_id))
    employee_services(con, hotel_id)


def employee_services(con, hotel_id):
    print("Enter the option you would like: \n")

    while True:
        selection = input("View available rooms (available for at least 1  day)   (1)\n"
                          "Transform booked room into renting    (2) \n"
                          "Rent room directly without a booking  (3) \n"
                          "Quit   (q)  \n")

        if selection.strip() in ['1', '2', '3']:
            break
        elif selection.lower().strip() == 'q':
            print("Quitting.")
            return
        else:
            print("Invalid selection")

    if selection == '1':
        view_available_rooms(con, hotel_id)
    elif selection == '2':
        transform_to_renting(con, hotel_id)

    else:
        rent_directly(con, hotel_id)


def transform_to_renting(con, hotel_id):
    # customer_id = input("Enter customer id:")
    # customer_id = customer_id.split()

    while True:
        selection = input("Enter by customer id (1)\n"
                          "Enter by customer SIN/SSN (2)\n")
        if selection.strip() not in ['1', '2']:

            print("Invalid selection.")
        else:
            if selection.strip() == '2':
                while True:

                    sin = input("Enter customer SIN/SSN: ")
                    sin = sin.strip().lower()
                    if not sin.isdigit():
                        print("SIN/SSN cannot contain letters or punctuation.")
                    else:
                        cursor = con.cursor()
                        cursor.execute("SET search_path = project_deliverable; "
                                       "SELECT exists ((SELECT 1 FROM Person WHERE SIN = \'" + str(
                            sin) + "\') LIMIT 1)")
                        result = cursor.fetchall()
                        # print(result) # [(False,)]
                        if result[0][0]:
                            cursor.execute("SET search_path = project_deliverable; "
                                           "SELECT customer_id from Customer c, Person p WHERE p.SIN = " + sin + " AND c.user_id = p.user_id")
                            sin = cursor.fetchall()
                            print(sin)
                            customer_ID = sin[0][0]
                            cursor = con.cursor()
                            cursor.execute("SET search_path = project_deliverable; "
                                           "SELECT b FROM bookings b WHERE b.customer_id = " + str(customer_ID) + ";")
                            booking = cursor.fetchall()
                            room_id = booking[0][2]
                            start_booking = booking[0][4]
                            today = datetime.date.today()
                            start = convert_to_date(start_booking)

                            cursor.execute("SET search_path = project_deliverable; "
                                           "SELECT r.hotel_id FROM room r WHERE r.room_id = " + str(room_id) + ";")
                            booking_hotel_id = cursor.fetchall()
                            booking_hotel_id = booking_hotel_id[0][0]
                            print("booking hotel id =" + booking_hotel_id)
                            booking_hotel_id = int(booking_hotel_id)
                            h = int(hotel_id)
                            if booking_hotel_id == h:

                                if start == today:
                                    break
                                else:
                                    print("This booking doesn't start today.")
                            else:
                                print("This booking is not for this hotel.")

                        elif len(sin) > 15:
                            print("Cannot exceed 15 characters.")
                        else:
                            print("No customer with this SIN/SSN.")
            else:
                while True:

                    sin = input("Enter customer ID: ")
                    sin = sin.strip().lower()
                    if not sin.isdigit():
                        print("Customer id cannot contain letters or punctuation.")
                    else:
                        cursor = con.cursor()
                        cursor.execute("SET search_path = project_deliverable; "
                                       "SELECT exists ((SELECT 1 FROM Customer WHERE Customer_ID = " + sin + ") LIMIT 1)")
                        result = cursor.fetchall()
                        # print(result) # [(False,)]
                        if result[0][0]:
                            customer_ID = sin
                            cursor = con.cursor()
                            cursor.execute("SET search_path = project_deliverable; "
                                           "SELECT b.booking_id, b.room_id, b.start_date, b.end_date, b.number_of_occupants"
                                           " FROM bookings b WHERE b.customer_id = " + str(customer_ID) + ";")

                            booking = cursor.fetchall()
                            #print(booking)
                            room_id = booking[0][1]
                            start_booking = booking[0][2]
                            today = datetime.date.today()
                            start = convert_to_date(start_booking)

                            cursor.execute("SET search_path = project_deliverable; "
                                           "SELECT r.hotel_id FROM room r WHERE r.room_id = " + str(room_id) + ";")
                            booking_hotel_id = cursor.fetchall()
                            booking_hotel_id = booking_hotel_id[0][0]
                            #print("booking hotel id =" + str(booking_hotel_id))
                            booking_hotel_id = int(booking_hotel_id)
                            h = int(hotel_id)
                            if booking_hotel_id == h:

                                if start == today:
                                    break
                                else:
                                    print("This booking doesn't start today.")
                                    return
                            else:
                                print("This booking is not for this hotel.")
                                return
                        else:
                            print("No customer with this id.")
                            return

            break

    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable; "
                   "SELECT  b.booking_id, b.customer_id, b.room_id, b.archived, b.start_date, b.end_date, b.number_of_occupants"
                   " FROM bookings b WHERE b.customer_id = " + str(customer_ID) + ";")
    booking = cursor.fetchall()
    #print(booking)

    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable; "
                   "SELECT setval('rentings_renting_id_seq', (SELECT MAX(renting_id) FROM rentings));")

    cursor.execute("SET search_path = project_deliverable; "
                   "SELECT MAX(renting_id) FROM rentings")
    renting_id = cursor.fetchall()[0][0]
    renting_id = int(renting_id) + 1
    renting = list(booking[0])
    renting = [renting_id] + renting
    renting = tuple(renting)
    #print(renting)

    cursor.execute("SET search_path = project_deliverable; "
                   "INSERT INTO RENTINGS VALUES " + str(renting) + ";")
    con.commit()

    cursor.execute("SET search_path = project_deliverable; "
                   "UPDATE bookings SET archived = TRUE WHERE customer_id = " + str(customer_ID) + " ;")

    print("Transformed to renting successfully.")

    cursor.execute("SET search_path = project_deliverable; "
                   "SELECT setval('payments_payment_id_seq', (SELECT MAX(payment_id) FROM payments));")
    #print("Renting ID: " + str(renting_id))

    cursor.execute("SET search_path = project_deliverable; "
                   "SELECT r.price From room r, rentings f WHERE f.room_id = r.room_id AND f.renting_id = " + str(
        renting_id) + ";")
    amount = cursor.fetchall()
    amount = int(amount[0][0])

    cursor.execute("SET search_path = project_deliverable;"
                   "INSERT INTO PAYMENTS VALUES (DEFAULT, " + str(amount) + ", " + str(renting_id) + ");")
    con.commit()
    print("Customer payment of  $" + str(amount) + " received.")

    employee_services(con, hotel_id)


def rent_directly(con, hotel_id):
    room_num_to_id_dict, number_of_days = view_available_rooms(con, hotel_id)
    # print(room_num_to_id_dict)

    while True:
        capacity = input("For how many guests: ")
        capacity = capacity.strip()

        try:
            chosen_capacity = int(capacity)
            break
        except ValueError:
            print("Not a number. Must be an integer")

    while True:
        chosen_room = input("Enter room number to book: ")
        chosen_room = chosen_room.strip()

        try:
            chosen_room = int(chosen_room)
            if chosen_room in room_num_to_id_dict:
                if room_num_to_id_dict[chosen_room][1] >= chosen_capacity:

                    room_id = room_num_to_id_dict[chosen_room][0]
                    print("Renting for room : " + str(chosen_room) + ".")
                    break
                else:
                    print("This room doesn't have enough capacity")
            else:
                print("Invalid room selection.")

        except ValueError:
            print("Not a number.")

    while True:
        sin = input("Enter customer ID: ")
        sin = sin.strip().lower()
        if not sin.isdigit():
            print("ID cannot contain letters or punctuation.")
        else:
            cursor = con.cursor()
            cursor.execute("SET search_path = project_deliverable; "
                           "SELECT exists ((SELECT 1 FROM Customer WHERE customer_id = " + sin + ") LIMIT 1)")
            result = cursor.fetchall()
            # print(result) # [(False,)]
            if result[0][0]:
                customer_ID = sin
                break
            else:
                print("No customer with this id")

    # start_date, end_date = choose_dates()
    today = datetime.date.today()
    start_date = today
    end_date = start_date + datetime.timedelta(number_of_days)
    #print(start_date, end_date)
    start_date = "\' " + format_to_db_date(start_date) + "\' "
    end_date = "\' " + format_to_db_date(end_date) + "\' "
    #print(start_date, end_date)
    try:

        cursor = con.cursor()
        cursor.execute(" SELECT setval('rentings_renting_id_seq', (SELECT MAX(renting_id) FROM rentings));"
                       # no + 1 if using setval
                       )
        con.commit()
        renting_value = "(DEFAULT, NULL, " + str(customer_ID) + ', ' + str(
            room_id) + ', ' + "FALSE," + start_date + ', ' + end_date + ',' + str(chosen_capacity) + ')'
        #print(renting_value)
        cursor.execute("SET search_path = project_deliverable;"
                       "INSERT INTO RENTINGS VALUES" + renting_value + ";")
        con.commit()

        cursor.execute("SET search_path = project_deliverable; "
                       "SELECT MAX(renting_id) FROM rentings")
        renting_id = cursor.fetchall()[0][0]
        renting_id = int(renting_id)

        cursor.execute("SET search_path = project_deliverable; "
                       "SELECT setval('payments_payment_id_seq', (SELECT MAX(payment_id) FROM payments));")
        #print("Renting ID: " + str(renting_id))

        cursor.execute("SET search_path = project_deliverable; "
                       "SELECT r.price From room r, rentings f WHERE f.room_id = r.room_id AND f.renting_id = " + str(
            renting_id) + ";")
        amount = cursor.fetchall()

        amount = int(amount[0][0])

        cursor.execute("SET search_path = project_deliverable;"
                       "INSERT INTO PAYMENTS VALUES (DEFAULT, " + str(amount) + ", " + str(renting_id) + ");")
        con.commit()
        print("Customer payment received.")

        print("Renting and payment created successfully\n")
        employee_services(con, hotel_id)
    except Exception as e:
        print(e)
        print(traceback.format_exc())


def format_to_db_date(s):
    m1 = str(s.month)
    if s.month < 10:
        m1 = '0' + m1
    d1 = str(s.day)
    if s.day < 10:
        d1 = '0' + d1
    y1 = str(s.year)
    return m1 + d1 + y1


def choose_dates():
    today = datetime.date.today()
    start_date, end_date = None, None
    start_date = today
    invalid_end_date = True
    chosen_end = None
    while invalid_end_date:
        print("Note: You can only rent a room for a maximum of 40 days and a minimum of 2 days.")
        chosen_end = input("Please enter the end date of your desired booking in the same format (MM/DD/YYYY)"
                           ", e.g. 11/30/2030 : ")
        chosen_end_r = chosen_end.replace("/", "")
        if len(chosen_end_r) != 8 or not chosen_end_r.isdigit():
            print("Invalid format or non-numeric characters given.")

        else:
            try:

                end_date = convert_to_date(chosen_end_r)
                if end_date < today:
                    print("You cannot pick a date in the past.")
                elif end_date == today:
                    print("End date cannot be on the same day as today.")
                elif end_date == start_date:
                    print("End date cannot be on the same day as start date.")
                elif end_date < start_date:
                    print("End date cannot be before your start date.")
                elif (end_date - start_date).days > 40:
                    print("You can only rent a room for a maximum of 40 days.")
                else:
                    invalid_end_date = False
            except ValueError:
                print("Not a valid date.")

    if chosen_end:
        print("Your chosen end date is : " + chosen_end)

    return start_date, end_date


def view_available_rooms(con, hotel_id):
    while True:
        number = input("For how many days? (including today) ")
        number = number.strip()

        try:
            number = int(number)
            if number > 0:
                number_of_days = number
                break
            elif number > 31:
                print("Cannot rent a room for more than 31 days.")
            else:
                print("Must be at least for 1 day.")

        except ValueError:
            print("Not a number.")

    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable;"
                   "SELECT room_id, Room_Number,  capacity, price, mountain_view, sea_view, extendable "
                   "FROM room WHERE room_ID IN (SELECT DISTINCT r.room_id FROM Room r, Hotels h WHERE "
                   "r.hotel_id = " + hotel_id + " );")

    hotel_rooms = cursor.fetchall()
    room_ids = [r[0] for r in hotel_rooms]
    room_numbers = [r[1] for r in hotel_rooms]
    room_num_to_id_dict = dict()
    for r in hotel_rooms:
        if r[6] == True:  # if extendable
            room_num_to_id_dict[r[1]] = (r[0], r[2] + 1)
        else:
            room_num_to_id_dict[r[1]] = (r[0], r[2])

    print("room ids")
    print(room_ids)
    dictionary = dict()
    print()
    print("Available rooms from today for " + str(number_of_days) + " days: ")
    print()
    for room in hotel_rooms:

        cursor = con.cursor()
        cursor.execute("SET search_path = project_deliverable;"
                       "SELECT booking_id, room_id, start_date, end_date FROM Bookings WHERE booking_ID IN ("
                       "SELECT DISTINCT b.booking_id FROM room r, Bookings b WHERE "
                       "r.hotel_id = " + hotel_id + " AND  b.room_id  = " + str(
            room[0]) + " AND b.Archived = False);")

        all_bookings_for_room = cursor.fetchall()

        bookings_and_rentings = []
        all_dates = []
        for booking in all_bookings_for_room:
            bookings_and_rentings.append(
                ('b', booking[0], booking[1], booking[2],
                 booking[3]))  # (booking, booking_id, room_id, start date, end date)
            all_dates.append((convert_to_date(booking[2]), convert_to_date(booking[3])))

        cursor.execute("SET search_path = project_deliverable;"
                       "SELECT renting_id, room_id, start_date, end_date FROM Rentings WHERE Renting_ID IN ("
                       "SELECT DISTINCT f.renting_ID FROM room r, Rentings f WHERE r.hotel_id =" + hotel_id +
                       " AND f.room_id = " + str(room[0]) + " AND f.booking_ID = NULL"
                                                            " AND f.Archived = False);")

        all_rentings_for_room = cursor.fetchall()

        for renting in all_rentings_for_room:
            bookings_and_rentings.append(('r', renting[0], renting[1], renting[2], renting[3]))
            all_dates.append((convert_to_date(renting[2]), convert_to_date(renting[3])))

        today = datetime.date.today()
        date_range = set()
        for i in range(1, number_of_days + 1):
            date_range.add(today + timedelta(i))
        end = today + timedelta(number_of_days)
        available = True
        for d in all_dates:
            if today <= d[1] and end >= d[0]:
                available = False


        '''
        invalid_dates = set()
        #for elem in date_range:
        #    for d in all_dates:
        #        if d[0] <= elem <= d[1]:
        #            invalid_dates.add(elem)
        # print(available_dates)
        if available_dates:
            dictionary[room[1]] = available_dates.copy()  # dictionary of room number to available dates
        else:
            dictionary[room[1]] = None  # dictionary of room number to available dates

        if number_of_days >= 2:
            l = get_consecutive_ranges(available_dates)
            dates_output = format_consecutive(l)
        else:
            print(available_dates)
            if available_dates:
                l = available_dates[0]
                dates_output = [format_day(l)]
            else:
                l = None
                dates_output = None
        '''
        cursor.execute("SET search_path = project_deliverable;"
                       "SELECT a.Amenities_name FROM Amenities a, has_room_amenities h, room r WHERE "
                       "r.room_id = " + str(room[0]) + " AND h.room_id = " + str(
            room[0]) + " AND h.amenities_id = a.amenities_id;")

        amenities = cursor.fetchall()
        amenities_string = ""

        if amenities[0]:
            for a in amenities[0]:
                amenities_string += str(a) + ', '
        print("For room number " + str(room[1]) + " :")

        if available:
            print("Is available From: ", end="")
            #for elem in dates_output:
            print(format_day(today) + " to " + format_day(end))
            print("Room details: ")
            print("Room ID: " + str(room[0]))
            print("Room price: " + str(room[3]))
            print("Room capacity: " + str(room[2]))
            print("Sea view: " + str(room[5]))
            print("Mountain view: " + str(room[4]))
            print("Extendable: " + str(room[6]))
            if amenities_string:
                print("Amenities: " + amenities_string[:-2])
            else:
                print("No Amenities")
            print("-------------------------------------------------------")

        else:
            room_numbers.remove(room[1])  # Can't book this room.
            room_num_to_id_dict.pop(room[1])
            print("Not available from today for that many days.")

    return room_num_to_id_dict, number_of_days


def format_day(s):
    m1 = str(s.month)
    if s.month < 10:
        m1 = '0' + m1
    d1 = str(s.day)
    if s.day < 10:
        d1 = '0' + d1
    y1 = str(s.year)
    return m1 + "/" + d1 + "/" + y1 #+ " to " + m1 + "/" + d1 + "/" + y1


def login_employee(con):
    while True:
        print("Enter employee login")

        while True:

            email = input("Enter your email (case-insensitive): ")
            email = email.lower()  # Case insensitive
            password = input("Enter your password: ")
            cursor = con.cursor()
            cursor.execute(
                "SET search_path = project_deliverable; SELECT e.employee_id, e.hotel_id, p.first_name, p.last_name "
                "FROM Employee e, person p "
                "WHERE p.user_id = e.user_id AND lower(p.Email) = '" + email + "' AND  "
                                                                               "p.password = '" + password + "';")
            result = cursor.fetchall()
            if result:

                employee_id = result[0][0]
                hotel_id = result[0][1]
                first_name = result[0][2]
                last_name = result[0][3]

                break
            else:
                print("Invalid email or password for employee account.")

        print("Logged in as employee.")
        print("Hello Employee: " + first_name + " " + last_name + "!")
        return str(employee_id), str(hotel_id)


def format_consecutive(l):
    if not l:
        return None
    output = []
    for each_range in l:

        if len(each_range) > 1:
            s = each_range[0]
            e = each_range[len(each_range) - 1]
            m1 = str(s.month)
            if s.month < 10:
                m1 = '0' + m1
            d1 = str(s.day)
            if s.day < 10:
                d1 = '0' + d1
            y1 = str(s.year)

            m2 = str(e.month)
            if e.month < 10:
                m2 = '0' + m2
            d2 = str(e.day)
            if e.day < 10:
                d2 = '0' + d2
            y2 = str(e.year)

            string = m1 + "/" + d1 + "/" + y1 + " to " + m2 + "/" + d2 + "/" + y2
            output.append(string)
    return output


def get_consecutive_ranges(c):
    d = []
    temp = []
    prev = False
    for i in range(len(c) - 1):
        if (c[i + 1] - c[i]).days == 1:
            if not prev:
                temp.append(c[i])
                prev = True
            temp.append(c[i + 1])
            if i == len(c) - 2:
                d.append(temp)
        else:
            d.append(temp)
            temp = []
            prev = False
    return d


def convert_to_date(date):
    y = int(date[-4:])
    d = int(date[2:4])
    m = int(date[:2])
    return datetime.date(y, m, d)


def archive_bookings_and_rentings(con):

    today = datetime.date.today()
    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable;"
                   "SELECT booking_id, end_date FROM Bookings WHERE archived = True;")

    bookings = cursor.fetchall()
    #print(bookings)
    for booking in bookings:
        id = str(booking[0])
        end = booking[1]
        end = convert_to_date(end)
        if end < today:
            cursor.execute("SET search_path = project_deliverable;"
                           "UPDATE bookings SET archived = False WHERE booking_id = " + id + " ;")

    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable;"
                   "SELECT renting_id, end_date FROM rentings WHERE archived = True;")

    rentings = cursor.fetchall()
    for renting in rentings:
        id = str(renting[0])
        end = renting[1]
        end = convert_to_date(end)
        if end < today:
            cursor.execute("SET search_path = project_deliverable;"
                           "UPDATE rentings SET archived = False WHERE renting_id = " + id + " ;")

    print("Archived bookings and rentings.")


if __name__ == "__main__":
    start()
