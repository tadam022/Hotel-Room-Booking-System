import traceback

import psycopg2
import datetime
from datetime import timedelta

BOOK_ADVANCE = 31


# from datetime import datetime, time, date, timedelta


def start_connection():
    try:

        con = psycopg2.connect(user="",
                               password="",
                               host="web0.eecs.uottawa.ca",
                               port="",
                               dbname="")
        print("Successfully connected to database.")
        main_program(con)
        con.close()

    except Exception as e:
        print("Failed to connect to database.")
        print(e)
        print(traceback.format_exc())


def main_program(con):
    invalid = True
    valid_user_types = ['2', '1']
    user_type = None
    while invalid:
        user_type = input("Welcome. Login as Customer         Press (1)\n"
                          "Register as Customer               Press(2)\n")
        user_type = user_type.strip().lower()
        if user_type in valid_user_types:
            invalid = False
        else:
            print("Not a valid input.")

    if user_type == '1':
        customer_id = login_customer(con)
        if customer_id:
            run_customer_services(con, customer_id)
    elif user_type == '2':
        register_customer(con)


def get_person_info(con):
    while True:
        first = input("Enter first name: ")
        first = first.strip().lower()
        if not first.isalpha():
            print("Names cannot contain numbers or punctuation.")
        else:
            first_name = first.capitalize()
            break

    while True:

        last = input("Enter last name: ")
        last = last.strip().lower()
        if not last.isalpha():
            print("Names cannot contain numbers or punctuation.")
        else:
            last_name = last.capitalize()
            break

    while True:

        sin = input("Enter SIN/SSN: ")
        sin = sin.strip().lower()
        if not sin.isdigit():
            print("SIN/SSN cannot contain letters or punctuation.")
        else:
            cursor = con.cursor()
            cursor.execute("SET search_path = project_deliverable; "
                           "SELECT exists ((SELECT 1 FROM Person WHERE SIN = \'" + str(sin) + "\') LIMIT 1)")
            result = cursor.fetchall()
            # print(result) # [(False,)]
            if result[0][0]:
                print("This SIN/SSN is already taken.")
                print(sin)
            else:
                if len(sin) > 15:
                    print("Cannot exceed 15 characters.")
                else:
                    SIN_or_SSN = sin
                    break

    while True:

        e = input("Enter email: ")
        e = e.strip()
        if len(e) > 254:
            print("Email address cannot exceed 254 characters.")
        else:
            cursor = con.cursor()
            cursor.execute("SET search_path = project_deliverable; "
                           "SELECT exists ((SELECT 1 FROM Person WHERE lower(email) = lower(' " + str(
                sin) + " ')) LIMIT 1)")
            result = cursor.fetchall()
            if result[0][0]:
                print("This email address is already taken.")
            else:
                Email = e
                break

    while True:

        phone = input("Enter PhoneNumber: ")
        phone = phone.strip()
        if len(phone) > 80:
            print("Phone Number cannot exceed 80 characters.")
        else:
            cursor = con.cursor()
            cursor.execute("SET search_path = project_deliverable; "
                           "SELECT exists (SELECT 1 FROM Person WHERE lower(Phone_Number) = lower(' " + str(
                phone) + " ') LIMIT 1)")
            result = cursor.fetchall()
            if result[0][0]:
                print("This phone number is already taken.")
            else:
                Phone_Number = phone
                break

    while True:
        password = input("Enter Password: ")
        password = password.strip()
        if len(password) > 32 or len(password) == 0 or len(password) <= 5:
            print("Password must be between 5 and 32 characters, inclusive.")
        else:
            Pass = password
            break

    return first_name, last_name, SIN_or_SSN, Email, Phone_Number, Pass


def get_address_info():
    print("Getting Address:")
    while True:

        country = input("Enter Country: ")
        country = country.strip().lower()
        country_z = country.replace(" ", "")
        if not country_z.isalpha():
            print("Country field can only contain letters")
        else:
            if len(country) == 0:
                print("Country field cannot be left blank.")
            elif len(country) > 100:
                print("Country field cannot exceed 100 characters.")
            else:
                Country = "\'" + country + "\'"

                break
    while True:
        c = input("Enter City: ")
        c = c.strip().lower()
        c_z = c.replace(" ", "")
        if not c_z.isalpha():
            print("City field can only contain letters")
        else:
            if len(c) == 0:
                print("City field cannot be left blank.")
            elif len(c) > 100:
                print("City field cannot exceed 100 characters.")
            else:
                City = "\'" + c + "\'"
                break
    while True:
        c = input("Enter State/Province (can be left blank if not applicable): ")
        c = c.strip().lower()
        c_z = c.replace(" ", "")
        if not c_z.isalpha() and len(c) > 0:
            print("State/Province field can only contain letters")
        else:
            if len(c) == 0:
                State_or_province = "NULL"
                break
            elif len(c) > 100:
                print("State/Province field cannot exceed 100 characters.")
            else:
                State_or_province = "\'" + c + "\'"
                break

    while True:
        c = input("Enter ZIP: ")
        c = c.strip().lower()
        if not c.isalnum():
            print("ZIP field can only contain letters and numbers.")
        else:
            if len(c) == 0:
                print("City field cannot be left blank.")
            elif len(c) > 15:
                print("ZIP field cannot exceed 15 characters.")
            else:
                ZIP = "\'" + c + "\'"
                break
    while True:
        c = input("Enter Address Line 1: ")
        c = c.strip()

        if len(c) == 0:
            print("Address Line 1 field cannot be left blank.")
        elif len(c) > 200:
            print("ZIP field cannot exceed 200 characters.")
        else:
            Addressline1 = "\'" + c + "\'"
            break

    while True:
        c = input("Enter Address Line 2 (can be left blank).: ")
        c = c.strip()
        if len(c) == 0:
            Addressline2 = "NULL"
            break
        elif len(c) > 50:
            print("Address Line 2field cannot exceed 200 characters.")
        else:
            Addressline2 = "\'" + c + "\'"
            break
    return Country, City, State_or_province, ZIP, Addressline1, Addressline2


def update_phone_number(con, customer_id):
    while True:
        phone = input("Enter new PhoneNumber: ")
        phone = phone.strip()
        if len(phone) > 80:
            print("Phone Number cannot exceed 80 characters.")
        else:
            phone = "\'" + phone + "\'"
            break
    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable;"
                   "UPDATE PERSON "
                   "SET phone_number = " + phone + " WHERE user_id IN (SELECT p.user_id FROM person p, customer c "
                                                   " WHERE p.user_id = c.user_id AND c.customer_id = " + str(
        customer_id) + ");")
    con.commit()
    print("Phone number updated successfully.")
    run_customer_services(con, customer_id)


def register_customer(con):
    print("Registering new customer")

    while True:
        Country, City, State_or_province, ZIP, Addressline1, Addressline2 = get_address_info()
        first_name, last_name, SIN_or_SSN, Email, Phone_Number, password = get_person_info(con)
        break

    cursor = con.cursor()
    cursor.execute(" SELECT setval('locations_location_id_seq', (SELECT MAX(location_id) FROM locations));"  # no + 1
                   )
    con.commit()

    location_value = "(" + "DEFAULT, " + Country + ',' + City + ',' + State_or_province + ',' + ZIP + ',' + Addressline1 + ',' + Addressline2 + ")"
    # print(location_value)
    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable;"
                   "INSERT INTO Locations VALUES " + location_value + " ;")
    con.commit()

    '''
    "SELECT setval('person_user_id_seq', (SELECT MAX(user_id) FROM person) + 1);"
                   "SELECT setval('customer_customer_id_seq', (SELECT MAX(customer_id) FROM customer) + 1);"
  
    '''
    cursor.execute("SET search_path = project_deliverable;"
                   "SELECT MAX(location_id) FROM locations;")

    location_id = cursor.fetchall()
    location_id = location_id[0][0]
    location_id = str(location_id)

    first_name = "\'" + first_name + "\'"
    last_name = "\'" + last_name + "\'"
    SIN_or_SSN = "\'" + SIN_or_SSN + "\'"
    Email = "\'" + Email + "\'"
    Phone_Number = "\'" + Phone_Number + "\'"
    password = "\'" + password + "\'"

    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable;"
                   "SELECT MAX(user_id) + 1 FROM person;")
    user_id = cursor.fetchall()
    user_id = str(user_id[0][0])

    person_value = "(" + user_id + ',' + first_name + ',' + last_name + ',' + SIN_or_SSN + ',' + Email + ',' + Phone_Number + ',' + location_id + ',' \
                   + password + ")"

    # print(person_value)

    cursor.execute("SET search_path = project_deliverable;"
                   "INSERT INTO Person VALUES " + person_value + " ;")
    con.commit()

    today = datetime.date.today()
    m1 = str(today.month)
    if today.month < 10:
        m1 = '0' + m1
    d1 = str(today.day)
    if today.day < 10:
        d1 = '0' + d1
    y1 = str(today.year)

    cursor.execute("SET search_path = project_deliverable;"
                   "SELECT MAX(customer_id) + 1 FROM customer;")
    customer_id = cursor.fetchall()
    customer_id = str(customer_id[0][0])

    registration_date = "'" + m1 + d1 + y1 + "'"
    customer_value = "(" + customer_id + "," + user_id + ',' + registration_date + ")"
    # print(customer_value)
    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable;"
                   "INSERT INTO Customer VALUES " + customer_value + " ;")
    con.commit()
    print("Registered successfully.")
    main_program(con)


def login_customer(con):  # as employee or customer

    print("Logging in as Customer: ")

    invalid_login = True
    customer_id, first_name, last_name = None, None, None
    while invalid_login:

        email = input("Enter your email (case-insensitive): ")
        email = email.lower()  # Case insensitive
        password = input("Enter your password: ")
        cursor = con.cursor()
        cursor.execute("SET search_path = project_deliverable; SELECT c.customer_id, p.first_name, p.last_name "
                       "FROM customer c, person p "
                       "WHERE p.user_id = c.user_id AND lower(p.Email) = '" + email + "' AND  "
                                                                                      "p.password = '" + password + "';")
        result = cursor.fetchall()
        if result:

            customer_id = result[0][0]
            first_name = result[0][1]
            last_name = result[0][2]
            invalid_login = False
        else:
            print("Invalid email or password for customer account.")

    print("Logged in as customer.")
    print("Hello " + first_name + last_name + "!")
    print("Customer id: " + str(customer_id))
    return customer_id


def run_customer_services(con, customer_id):
    print("Would you like to: ")
    selection = input("Book a room                      Press (1)\n"
                      "View your Booked/Rented rooms    Press (2)\n"
                      "Update Phone Number              Press (3)\n"
                      "Quit                             Press (q)\n")

    if selection == '1':
        found_room = False
        book_room(con, customer_id)

    elif selection == '2':
        view_booked_or_rented_rooms(con, customer_id)

    elif selection == '3':
        update_phone_number(con, customer_id)


def view_booked_or_rented_rooms(con, customer_id):
    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable;"
                   "SELECT room_id, number_of_occupants, start_date, end_date from bookings WHERE bookings.customer_id = "
                   " " + str(customer_id) + " AND bookings.archived = False;")

    all_bookings = cursor.fetchall()
    print("Your bookings: ")
    print()

    if not all_bookings:
        print("You have no current bookings.")
    else:
        for booking in all_bookings:
            room_id = booking[0]
            occupants = booking[1]
            cursor.execute("SET search_path = project_deliverable;"
                           "SELECT r.room_number, r.capacity, r.price, r.mountain_view, r.sea_view, r.extendable from room r WHERE "
                           "r.room_id = " + str(room_id) + " ;")
            room_info = cursor.fetchall()

            cursor.execute("SET search_path = project_deliverable;"
                           "SELECT h.name from hotels h, room r WHERE r.hotel_id = h.hotel_id AND r.room_id = " + str(
                room_id) + " ;")

            hotel_name = cursor.fetchall()

            cursor.execute("SET search_path = project_deliverable;"
                           "SELECT a.Amenities_name FROM Amenities a, has_room_amenities h, room r WHERE "
                           "r.room_id = " + str(room_id) + " AND h.room_id = " + str(
                room_id) + " AND h.amenities_id = a.amenities_id;")

            amenities = cursor.fetchall()
            amenities_string = ""

            if amenities[0]:
                for a in amenities[0]:
                    amenities_string += str(a) + ', '

            # print(room_info)
            print("Hotel Name: " + str(hotel_name[0][0]))
            print("Room number: " + str(room_info[0][0]))
            print("Start date: " + str(booking[2]))
            print("End date: " + str(booking[3]))
            print("Capacity: " + str(room_info[0][1]))
            print("Price: " + str(room_info[0][2]))
            print("Mountain View: " + str(room_info[0][3]))
            print("Sea View: " + str(room_info[0][4]))
            print("Extendable: " + str(room_info[0][5]))
            print("Number of guests: " + str(occupants))
            if amenities_string:
                print("Amenities: " + amenities_string[:-2])
            else:
                print("No Amenities")
            print("------------------------------------------------------")

    print()
    print("*****************************************************")
    print()
    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable;"
                   "SELECT room_id, number_of_occupants, start_date, end_date from rentings WHERE rentings.customer_id = "
                   " " + str(customer_id) + " AND rentings.archived = False;")

    all_rentings = cursor.fetchall()
    print("Your rentings: ")
    print()
    if not all_rentings:
        print("You have no current rentings.")
    else:
        for renting in all_rentings:
            room_id = renting[0]
            occupants = renting[1]
            cursor.execute("SET search_path = project_deliverable;"
                           "SELECT r.room_number, r.capacity, r.price, r.mountain_view, r.sea_view, r.extendable, r.type from room r WHERE "
                           "r.room_id = " + str(room_id) + " ;")
            room_info = cursor.fetchall()

            cursor.execute("SET search_path = project_deliverable;"
                           "SELECT h.name from hotels h, room r WHERE r.hotel_id = h.hotel_id AND r.room_id = " + str(
                room_id) + " ;")

            hotel_name = cursor.fetchall()

            cursor.execute("SET search_path = project_deliverable;"
                           "SELECT a.Amenities_name FROM Amenities a, has_room_amenities h, room r WHERE "
                           "r.room_id = " + str(room_id) + " AND h.room_id = " + str(
                room_id) + " AND h.amenities_id = a.amenities_id;")

            amenities = cursor.fetchall()
            amenities_string = ""
            if amenities[0]:
                for a in amenities[0]:
                    amenities_string += str(a) + ', '

            print("Hotel Name: " + str(hotel_name[0][0]))
            print("Room number: " + str(room_info[0][0]))
            print("Start date: " + str(renting[2]))
            print("End date: " + str(renting[3]))
            print("Capacity: " + str(room_info[0][1]))
            print("Price: " + str(room_info[0][2]))
            print("Mountain View: " + str(room_info[0][3]))
            print("Sea View: " + str(room_info[0][4]))
            print("Extendable: " + str(room_info[0][5]))
            print("Room type: " + str(room_info[0][6]))
            print("Number of guests: " + str(occupants))
            if amenities_string:
                print("Amenities: " + amenities_string[:-2])
            else:
                print("No Amenities")
            print("------------------------------------------------------")
    run_customer_services(con, customer_id)


def view_all_hotels(con):
    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable; SELECT * FROM Hotels;")
    result = cursor.fetchall()
    print("Displaying " + str(len(result)) + " Hotels.")
    count = 1
    for res in result:
        print("Hotel Name: " + res[2] + "    (" + str(count) + ")")
        print("Number of Rooms: " + str(res[3]))
        print("Email Address: " + res[4])
        print("Phone Number: " + res[5])
        print("Star Category: " + str(res[7]))
        print("-----------------------------------------------------")
        count += 1
    while True:
        hotel_selected = input("Enter number of hotel you want to book at: ")
        hotel_selected = hotel_selected.strip()

        try:
            h = int(hotel_selected)
            if h in range(count):
                break
            else:
                print("Number not in range.")
        except ValueError:
            print("Not a number.")
    return result[h - 1][0], result[h - 1][2]


def book_room(con, customer_id):
    # display_all_hotels(con)
    while True:
        print("View All Hotels:                     (1)")
        print("Enter city, hotel name or address    (2)")
        selection = input("Enter the number of the option you want: ")
        if int(selection) in range(1, 3):
            break
        else:
            print("Not a valid selection.")

    hotel_id_selected, hotel_name_selected = None, None

    if int(selection) == 2:

        hotel_id_selected, hotel_name_selected = get_hotel_id_by_location(con)

    elif int(selection) == 1:
        print(hotel_id_selected, hotel_name_selected)
        hotel_id_selected, hotel_name_selected = view_all_hotels(con)

    if hotel_id_selected:
        while True:
            selected_price = input("Enter maximum price for room : ")
            selected_price = selected_price.strip()
            selected_price = selected_price.replace(",", "")
            if not selected_price.isdigit():
                print("You can only enter in a number")
            else:
                try:

                    selected_price = float(selected_price)
                    break
                except ValueError:
                    print("Not a valid number.")

        while True:
            selected_capacity = input("Enter number of occupants, e.g. 2  : ")
            selected_capacity = selected_capacity.strip()
            if not selected_capacity.isdigit():
                print("You can only enter in an Integer")
            else:
                try:
                    selected_capacity = int(selected_capacity)
                    break
                except ValueError:
                    print("Not a valid number.")

        print("Finding rooms with a price equal to or below: " + str(selected_price))
        print("And a capacity of at least : " + str(selected_capacity))

        cursor = con.cursor()
        cursor.execute("SET search_path = project_deliverable;"
                       "SELECT room_id, Room_Number,  capacity, price, mountain_view, sea_view, extendable "
                       "FROM room WHERE room_ID IN (SELECT DISTINCT r.room_id FROM Room r, Hotels h WHERE "
                       "r.hotel_id = " + str(hotel_id_selected) + " AND (r.capacity >= "
                       + str(selected_capacity) + " OR (r.extendable = True AND r.capacity + 1 >= " + str(
            selected_capacity) + " )"
                                 ") AND r.price <= " + str(selected_price) + " );")

        hotel_rooms = cursor.fetchall()
        room_ids = [r[0] for r in hotel_rooms]
        room_numbers = [r[1] for r in hotel_rooms]
        room_num_to_id_dict = dict()
        for r in hotel_rooms:
            room_num_to_id_dict[r[1]] = r[0]

        print("room ids")
        print(room_ids)
        dictionary = dict()

        for room in hotel_rooms:

            cursor = con.cursor()
            cursor.execute("SET search_path = project_deliverable;"
                           "SELECT booking_id, room_id, start_date, end_date FROM Bookings WHERE booking_ID IN ("
                           "SELECT DISTINCT b.booking_id FROM room r, Bookings b WHERE "
                           "r.hotel_id = " + str(hotel_id_selected) + " AND  b.room_id  = " + str(
                room[0]) + " AND b.Archived = False);")

            all_bookings_for_room = cursor.fetchall()
            # print(all_bookings_for_room)
            bookings_and_rentings = []
            all_dates = []
            for booking in all_bookings_for_room:
                bookings_and_rentings.append(
                    ('b', booking[0], booking[1], booking[2],
                     booking[3]))  # (booking, booking_id, room_id, start date, end date)
                all_dates.append((convert_to_date(booking[2]), convert_to_date(booking[3])))

            cursor.execute("SET search_path = project_deliverable;"
                           "SELECT renting_id, room_id, start_date, end_date FROM Rentings WHERE Renting_ID IN ("
                           "SELECT DISTINCT f.renting_ID FROM room r, Rentings f WHERE r.hotel_id =" + str(
                hotel_id_selected) +
                           " AND f.room_id = " + str(room[0]) + " AND f.booking_ID IS NULL"
                                                                " AND f.Archived = False);")

            all_rentings_for_room = cursor.fetchall()

            for renting in all_rentings_for_room:
                bookings_and_rentings.append(('r', renting[0], renting[1], renting[2], renting[3]))
                all_dates.append((convert_to_date(renting[2]), convert_to_date(renting[3])))

            # print(bookings_and_rentings)
            # print("all dates")
            # print(all_dates)
            today = datetime.date.today()
            date_range = set()
            for i in range(BOOK_ADVANCE):
                date_range.add(today + timedelta(i))

            invalid_dates = set()
            for elem in date_range:
                for d in all_dates:
                    if d[0] <= elem <= d[1]:
                        invalid_dates.add(elem)
            # print("invalid dates")
            # print(invalid_dates)
            # print(len(invalid_dates))

            available_dates = list(date_range - invalid_dates)
            available_dates.sort()
            # print(available_dates)
            dictionary[room[1]] = available_dates.copy()  # dictionary of room number to available dates
            l = get_consecutive_ranges(available_dates)

            print("Available date ranges (of at least 2 days) within 31 days from today for room number " + str(
                room[1]) + " :")
            dates_output = format_consecutive(l)
            if dates_output:
                for elem in dates_output:
                    print(elem)
                print("Room details: ")
                print("Room price: " + str(room[3]))
                print("Room capacity: " + str(room[2]))
                print("Extendable:  " + str(room[6]))
                print("Sea view: " + str(room[5]))
                print("Mountain view: " + str(room[4]))
                print("-------------------------------------------------------")

            else:
                room_numbers.remove(room[1])  # Can't book this room.
                print("None available for next 31 days.")

        while True:

            want_to_book = input("Would you like to book one of these rooms at this hotel? (y/n)")
            want_to_book = want_to_book.lower().strip()

            if want_to_book == 'y':
                break

            elif want_to_book == 'n':
                return
            else:
                print("Please enter the keys y or n.")
        # room_selection = None
        # room_dates = None
        while True:

            room_selection = input("Enter the room number you want to book: ")
            room_selection = room_selection.strip()
            try:
                room_selection = int(room_selection)
                if room_selection in room_numbers:
                    room_dates = dictionary[room_selection]
                    break
                else:
                    print("No room with this number.")
            except ValueError:
                print("Not a valid number")

        invalid_chosen_dates = True
        while invalid_chosen_dates:
            chosen_start_date, chosen_end_date = choose_dates()  # Have to check if these dates now are in available ranges
            # print(chosen_start_date, type(chosen_start_date))
            '''
            dif = (chosen_end_date - chosen_start_date).days
            chosen_dates = set()
            for i in range(dif):
                chosen_dates.add(chosen_start_date)
            '''
            #print("ROOM DATES")
            #print(room_dates)

            if chosen_start_date in room_dates and chosen_end_date in room_dates:

                cursor.execute("SET search_path = project_deliverable;"
                               "SELECT MAX(booking_id)+ 1 FROM bookings;")
                booking_id = cursor.fetchall()
                booking_id = str(booking_id[0][0])
                room_id = room_num_to_id_dict[room_selection]
                format_start = format_to_display_date(chosen_start_date)
                format_end = format_to_display_date(chosen_end_date)
                format_start = format_start.replace("/", "")
                format_end = format_end.replace("/", "")
                format_start = "\'" + format_start + "\'"
                format_end = "\'" + format_end + "\'"

                booking_value = ("(" + booking_id + ", " + str(customer_id) + ", " + str(
                    room_id) + ", " + "FALSE," + format_start + "," + format_end + ","
                                 + str(selected_capacity))
                cursor = con.cursor()
                print(booking_value)

                cursor.execute("SET search_path = project_deliverable;"
                               "INSERT INTO Bookings VALUES " + booking_value + " );")
                con.commit()

                print("Booked successfully")
                print("You booked room: " + str(room_selection))
                print("At: " + hotel_name_selected)
                print("For: " + str(selected_capacity) + " people.")
                print("For dates:")
                start = format_to_display_date(chosen_start_date)
                end = format_to_display_date(chosen_end_date)
                print(start + " to " + end)
                break

            else:
                print("Invalid dates given for this room. Check if your start and end dates overlap the available ranges"
                      "given for each room.")

    run_customer_services(con, customer_id)

def format_to_db_date(s):
    m1 = str(s.month)
    if s.month < 10:
        m1 = '0' + m1
    d1 = str(s.day)
    if s.day < 10:
        d1 = '0' + d1
    y1 = str(s.year)
    return m1 + d1 + y1


def format_to_display_date(s):
    m1 = str(s.month)
    if s.month < 10:
        m1 = '0' + m1
    d1 = str(s.day)
    if s.day < 10:
        d1 = '0' + d1
    y1 = str(s.year)
    return m1 + "/" + d1 + "/" + y1


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


def get_address_from_id(con, id):
    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable; "
                   "SELECT * FROM Locations WHERE Location_ID = " + str(id) + " ;")
    result = cursor.fetchall()
    s = ''
    for elem in result:
        for i in range(1, 7):
            if elem[i]:
                s += elem[i] + ","
    return s[:-1]


def get_hotel_id_by_location(con):
    result = None
    not_at_least_one_found = True
    while not_at_least_one_found:
        location = input("Enter location: ")
        print("Displaying hotels given: " + location)
        result = display_hotels_with_location(con, location)

        if result:
            not_at_least_one_found = False

        else:
            print("No hotels found with that location.")
            go_back = input("Retry with a different location? (y/n)")
            if go_back.strip().lower() == 'n':
                return None  #####################################################
    count = 1
    for res in result:
        print(res[2] + "    " + "(" + str(count) + ")")
        print("Address : " + get_address_from_id(con, res[7]))
        print()
        count += 1

    invalid_hotel_select = True
    hotel_selection = None
    while invalid_hotel_select:
        hotel_selection = int(input("Enter the corresponding number on the right of each hotel name (1 - "
                                    + str(count - 1) + ") to select that hotel: "))
        if hotel_selection not in range(1, count):
            print("Invalid selection.")
        else:
            invalid_hotel_select = False

    if hotel_selection:  # needed?
        selected_hotel_name = result[int(hotel_selection) - 1][2]
        print("You have selected " + selected_hotel_name)
        hotel_id_selected = result[int(hotel_selection) - 1][0]
        print("Hotel ID: " + str(hotel_id_selected))
        return hotel_id_selected, selected_hotel_name


def convert_to_date(date):
    y = int(date[-4:])
    d = int(date[2:4])
    m = int(date[:2])
    return datetime.date(y, m, d)


def choose_dates():
    today = datetime.date.today()
    invalid_start_date = True
    chosen_start = None
    start_date, end_date = None, None
    print("Note: You can only book a date up to a maximum of one month (31 days) in advance.")
    while invalid_start_date:

        chosen_start = input("Please enter the start date of your desired booking in the format (MM/DD/YYYY)"
                             ", e.g. 11/30/2030 : ")
        chosen_start_r = chosen_start.replace("/", "")
        if len(chosen_start_r) != 8 or not chosen_start_r.isdigit():
            print("Invalid format or non-numeric characters given.")

        else:
            try:

                start_date = convert_to_date(chosen_start_r)
                if start_date < today:
                    print("You cannot book a room in the past.")
                elif (start_date - today).days > 31:
                    print("You can only book a date up to a maximum of 31 days in advance.")
                else:
                    invalid_start_date = False
            except ValueError:
                print("Not a valid date.")

    if chosen_start:
        print("Your chosen start date is : " + chosen_start)

    chosen_end = None
    while True:
        print("Note: You can only book a room in advance for a maximum of 40 days and a minimum of 2 days.")
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
                    break
            except ValueError:
                print("Not a valid date.")

    if chosen_end:
        print("Your chosen end date is : " + chosen_end)

    return start_date, end_date


def display_hotels_with_location(con, location):
    location = location.strip().lower()
    cursor = con.cursor()
    cursor.execute("SET search_path = project_deliverable; "
                   "SELECT * FROM Hotels WHERE Hotel_ID IN "
                   "(SELECT DISTINCT h.Hotel_ID FROM Hotels h, Locations l WHERE (lower(l.State_or_Province) ='" + location +
                   "' OR lower(l.Country) ='" + location + "' OR lower(l.City) ='" + location + "' OR lower(l.Address_Line1) ='" +
                   location + "') AND l.Location_ID = h.Location_ID);")
    result = cursor.fetchall()
    return result


if __name__ == '__main__':
    start_connection()
