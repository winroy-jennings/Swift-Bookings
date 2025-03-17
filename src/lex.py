import json
import sys

import ply.lex as lex
import ply.yacc as yacc
import os

import psycopg
from google import genai
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")
gemini_api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=f"{gemini_api_key}")

# Neon db connection
neon_db: psycopg.connection.Connection

# Reserved words
reserved = {
    # Commands
    "Book": "KEYWORD_BOOK",
    "Confirm": "KEYWORD_CONFIRM",
    "Pay": "KEYWORD_PAY",
    "Cancel": "KEYWORD_CANCEL",
    "List": "KEYWORD_LIST",
    "View": "KEYWORD_VIEW",
    "History": "KEYWORD_HISTORY",
    "Help": "KEYWORD_HELP",
    "Exit": "KEYWORD_EXIT",

    # Reserved words
    "available": "AVAILABLE",

    # Keyword identifiers
    "ticket": "TICKET",
    "tickets": "TICKETS",
    "concert": "CONCERT",
    "accommodation": "ACCOMMODATION",
    "accommodations": "ACCOMMODATIONS",
    "room": "ROOM",
    "rooms": "ROOMS",
    "event": "EVENT",

    # Others
    "reservation": "RESERVATION",
    "reservations": "RESERVATIONS",
    "schedule": "SCHEDULE",
    "schedules": "SCHEDULES",

    # Details
    "from": "FROM",
    "to": "TO",
    "on": "ON",
    "at": "AT",
    "for": "FOR",
    "in": "IN",
    ".": "SYM_END",
}

# Token list
tokens = [
             # Time/date values
             "DATE",
             "TIME",
             # Numeric values
             "INTEGER",
             "STRING",
             "FLOAT",
             # Identifiers
             "IDENTIFIER",
         ] + list(reserved.values())


# Comments (ignored)
def t_comment(t):
    r"""\#.*"""
    pass


# Date values (Month, Day, Year)
def t_date(t):
    r"""(January|February|March|April|May|June|July|August|September|October|November|December)\s?\d{1,2},\s?\d{4}"""
    t.type = "DATE"
    return t


# Time values (12-hour time with AM/PM, 24-hour time)
def t_time(t):
    r"""((0?[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM))|(([01]?[0-9]|2[0-3]):[0-5][0-9])"""
    t.type = "TIME"
    return t


# Dot at the end of a statement
def t_end(t):
    r"""\.$"""
    t.type = "SYM_END"
    return t


# Float values
def t_float(t):
    r"""\d+\.\d+"""
    t.value = float(t.value)
    return t


# Integer values
def t_integer(t):
    r"""-?\d+"""
    t.value = int(t.value)
    t.type = "INTEGER"
    return t


# String values
def t_string(t):
    r"""(\".*?\")|('.*?')"""
    t.value = t.value[1:-1]  # Remove quotes
    t.type = "STRING"
    return t


# Identifiers (including reserved words)
def t_identifier(t):
    r"""[a-zA-Z_][a-zA-Z_0-9]*"""
    t.type = reserved.get(t.value, "IDENTIFIER")  # Check for reserved words
    return t


# Newline tracking
def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


# Ignore whitespace and tabs
t_ignore = " \t"


# Error handling
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Map of months to their corresponding numbers
months = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


# --- Parser ---


# Grammar rules
def p_command(p):
    """
    command : book_command
            | confirm_command
            | pay_command
            | cancel_command
            | list_command
            | view_command
            | history_command
            | help_command
            | exit_command
    """

    print("Valid command:", p[1])


def p_identifier_list(p):
    """
    identifier_list : IDENTIFIER identifier_list
                    | IDENTIFIER
                    | STRING
                    | identifier_list '-' identifier_list
    """

    if len(p) == 3:
        p[0] = f"{p[1]} {p[2]}"
    else:
        p[0] = p[1]

    #   Example commands
    #       Transportation Services (Trains, Buses, Airlines)
    #           Book ticket for Knutsford Express from Montego Bay to Kingston on February 17,
    #           2025 at 8:30 AM for Joy Reynolds.

    #           Book 2 tickets for Knutsford Express from Montego Bay to Kingston on February 17,
    #           2025 at 8:30 AM for Joy Reynolds.
    #           Book ticket for Knutsford Express from Montego Bay to Kingston on February 17, 2025 at 4:00 PM for Joy Reynolds.

    #       Concert Tickets

    #       Testing the date validation
    #           Book 2 tickets for Knutsford Express from Montego Bay to Kingston on February 29,
    #           2025 at 8:30 AM for Joy Reynolds.

    #       Testing the number validation
    #           Book -2 tickets for Knutsford Express from Montego Bay to Kingston on February 17,
    #           2025 at 8:30 AM for Joy Reynolds.


def p_book_command(p):
    """
    book_command : KEYWORD_BOOK TICKET FOR identifier_list SYM_END
                | KEYWORD_BOOK INTEGER TICKETS FOR identifier_list SYM_END

                | KEYWORD_BOOK TICKET FOR identifier_list FROM identifier_list TO identifier_list SYM_END
                | KEYWORD_BOOK INTEGER TICKETS FOR identifier_list FROM identifier_list TO identifier_list SYM_END

                | KEYWORD_BOOK TICKET FOR CONCERT identifier_list IN identifier_list FOR identifier_list SYM_END
                | KEYWORD_BOOK INTEGER TICKETS FOR CONCERT identifier_list IN identifier_list FOR identifier_list SYM_END

                | KEYWORD_BOOK TICKET FOR CONCERT identifier_list AT identifier_list ON DATE AT TIME FOR identifier_list SYM_END
                | KEYWORD_BOOK INTEGER TICKETS FOR CONCERT identifier_list AT identifier_list ON DATE AT TIME FOR identifier_list SYM_END

                | KEYWORD_BOOK TICKET FOR EVENT identifier_list IN identifier_list SYM_END
                | KEYWORD_BOOK INTEGER TICKETS FOR EVENT identifier_list IN identifier_list SYM_END

                | KEYWORD_BOOK TICKET FOR EVENT identifier_list AT identifier_list SYM_END
                | KEYWORD_BOOK INTEGER TICKETS FOR EVENT identifier_list AT identifier_list SYM_END

                | KEYWORD_BOOK TICKET FOR EVENT identifier_list AT identifier_list ON DATE AT TIME FOR identifier_list SYM_END
                | KEYWORD_BOOK INTEGER TICKETS FOR EVENT identifier_list AT identifier_list ON DATE AT TIME FOR identifier_list SYM_END

                | KEYWORD_BOOK ACCOMMODATION FOR identifier_list IN identifier_list ON DATE TO DATE FOR identifier_list SYM_END

                | KEYWORD_BOOK TICKET FOR identifier_list AT identifier_list SYM_END
                | KEYWORD_BOOK INTEGER TICKETS FOR identifier_list AT identifier_list SYM_END

                | KEYWORD_BOOK TICKET FOR identifier_list ON DATE AT TIME FOR identifier_list SYM_END
                | KEYWORD_BOOK INTEGER TICKETS FOR identifier_list ON DATE AT TIME FOR identifier_list SYM_END

                | KEYWORD_BOOK TICKET FOR identifier_list FROM identifier_list TO identifier_list ON DATE AT TIME FOR identifier_list SYM_END
                | KEYWORD_BOOK INTEGER TICKETS FOR identifier_list FROM identifier_list TO identifier_list ON DATE AT TIME FOR identifier_list SYM_END
    """

    try:
        cur = neon_db.cursor()

        system_prompt = f"""
        Tone and style instructions for the model:
            When responding to user queries about booking tickets for various events (e.g., events, transportation, accommodations, concert, tickets).
            
            These are the criteria:
            
            Then, check to see if the booking details are correct.
            i.e: If the user entered - "Book ticket for Knutsford Express from Montego Bay to Kingston on February 17, 2025 at 1:15 PM for Joy Reynolds."
            
            Check Knutsford Express schedule if there is a Departure Time for Montego Bay to Kingston on February 17, 2025 at 1:15 PM
            
            Also validate the DATE if a date was provided: If the user enter a date that is not valid then return a string instead of a JSON object
            Saying: "Error: Invalid date format"
            
            IF 
            
            CHeck the user user enter a name to whom the tickets are being booked for.
            i.e: Book ticket for Knutsford Express from Montego Bay to Kingston on February 17, 2025 at 2:13 AM for Joy Reynolds.
            
            Here the tickets are being booked for "Joy Reynolds"
            
            Else, return a string instead of a JSON object saying: "Error: A name was not entered to whom the tickets should be booked for."
            
            If there exist a bus for this information,
            then return a JSON object of all the available information that is required for the service in question
            add the users' name and type of ticket. Such as:
            
            For the keys in the JSON object. Return, if:
                For "General Event"
                    Customer Name
                    Event Name
                    Venue
                    Date
                    Time
                    Ticket Type
                    Price
                    Available Tickets
                    
                For "Transportation Ticket"
                    Customer Name
                    Transportation Company
                    Departure Location
                    Arrival Location
                    Departure Time
                    Date
                    Ticket Type
                
                For "Concert Ticket"
                    Customer Name
                    Event Name
                    Venue
                    Location
                    Date
                    Time
                    Ticket Type
                    Seat Number
                    Price
                
                For "Accommodations" (Assign a room that is available and matches the user specification)
                    Customer Name
                    Property Name
                    Location
                    Room number
                    Check In Date
                    Check Out Date
                    Room Type Unit Type
                    Price Per Night
                    Available Rooms Units
                    Ticket Type
                
                For "Sports Ticket"
                    Customer Name
                    Teams
                    Stadium
                    Date
                    Start Time
                    Seat Location
                    Price
                    Seat Number
                    Ticket Type
            
            Ticket Type should be one of the following Types:
                General Event
                Transportation Ticket (Trains, Buses, Airlines)
                Concert Ticket
                Accommodations
                Sports Ticket
                Other Event
            
            That they are booking to the JSON object.
            
            If the booking details are incorrect, then return an empty JSON object. 
            
            Based on the availability of the tickets.
            return a response based on the following criteria:
            
            Please adhere to the following guidelines:
            Return just the JSON object of all the available information that is required for the service in question.
            Remove the ```json ``` form the JSON object. 
            No explanation needed.
            
            If no schedules or events are found then JUST return an empty JSON object.
            Capitalize the first letter of each word in the key. Remove underscore if visible then space each word.
        """

        s = ' '.join(p[1:])

        full_prompt = f"{system_prompt}\n\n{s}."

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=full_prompt
        )

        query = response.text.replace("```json", "").replace("```", "").strip("\n").strip()

        if query == "Error: Invalid date format":
            print("DATABASE QUERY")
        elif query == "Error: A name was not entered to whom the tickets should be booked for.":
            print("Error: Name missing")
        else:
            print("Processing...")
            booking_data: json = json.loads(query)

            # Insert into booking table
            cur.execute("""
                       INSERT INTO bookings (customer_name, ticket_type, ticket_status)
                       VALUES (%s, %s, %s)
                       RETURNING booking_id;
                   """, (booking_data['Customer Name'],
                         booking_data['Ticket Type'],
                         'Booked'))

            booking_id = cur.fetchone()[0]

            if booking_data["Ticket Type"] == "General Event":
                cur.execute("""
                    INSERT INTO general_events (booking_id, event_name, venue, event_date, start_time, price, available_tickets)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """, (booking_id,
                          booking_data['Event Name'],
                          booking_data['Venue'],
                          booking_data['Date'],
                          booking_data['Time'],
                          booking_data['Price'],
                          booking_data['Available Tickets'],
                          ))

                neon_db.commit()

            elif booking_data["Ticket Type"] == "Transportation Ticket":
                cur.execute("""
                    INSERT INTO transportation_tickets (booking_id, transportation_company, departure_location, arrival_location, departure_time, departure_date)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """, (booking_id,
                          booking_data['Transportation Company'],
                          booking_data['Departure Location'],
                          booking_data['Arrival Location'],
                          booking_data['Departure Time'],
                          booking_data['Date'],
                          ))

                neon_db.commit()

            elif booking_data["Ticket Type"] == "Concert Ticket":
                cur.execute("""
                    INSERT INTO concert_tickets (booking_id, event_name, venue, location, event_date, start_time, seat_number, price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """, (booking_id,
                          booking_data['Event Name'],
                          booking_data['Venue'],
                          booking_data['Location'],
                          booking_data['Date'],
                          booking_data['Time'],
                          booking_data['Seat Number'],
                          booking_data['Price'],
                          ))

                neon_db.commit()

            elif booking_data["Ticket Type"] == "Accommodations":
                cur.execute("""
                    INSERT INTO accommodations (booking_id, property_name, location, room_number, check_in_date, check_out_date, room_type_unit_type, price_per_night, available_rooms_units)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (booking_id,
                          booking_data['Property Name'],
                          booking_data['Location'],
                          booking_data['Room Number'],
                          booking_data['Check In Date'],
                          booking_data['Check Out Date'],
                          booking_data['Room Type Unit Type'],
                          booking_data['Price Per Night'],
                          booking_data['Available Rooms Units'],
                          ))

                neon_db.commit()

            elif booking_data["Ticket Type"] == "Sports Ticket":
                cur.execute("""
                    INSERT INTO sports_tickets (booking_id, teams, stadium, event_date, start_time, seat_location, price, seat_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """, (booking_id,
                          booking_data['Teams'],
                          booking_data['Stadium'],
                          booking_data['Date'],
                          booking_data['Start Time'],
                          booking_data['Seat Location'],
                          booking_data['Price'],
                          booking_data['Seat Number'],
                          ))

                neon_db.commit()

        p[0] = s
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
    except psycopg.DatabaseError as e:
        neon_db.rollback()
        print(f"Error inserting data: {e}")
        return None
    except Exception as e:
        neon_db.rollback()
        print(f"Error: {e}")
        return None
    finally:
        cur = neon_db.cursor()

        if cur:
            cur.close()


#   Examples:
#       Confirm reservation for Knutsford Express for Joy Reynolds.
#       Confirm 3 reservations for Knutsford Express for Joy Reynolds.

#   Testing error handling
#       Confirm -3 reservations for Knutsford Express for Joy Reynolds.


def p_confirm_command(p):
    """
    confirm_command : KEYWORD_CONFIRM RESERVATION FOR identifier_list FOR identifier_list SYM_END
                    | KEYWORD_CONFIRM INTEGER RESERVATIONS FOR identifier_list FOR identifier_list SYM_END
    """

    if type(p[2]) is int:
        if p[2] < 1:
            print(
                "Error: The number of reservations MUST be a positive number. Great than 0!"
            )
        else:
            p[0] = f"Confirm {p[2]} reservations for {p[5]} for {p[7]}."
    else:
        p[0] = f"Confirm reservation for {p[4]} for {p[6]}."


#   Examples:
#       Pay reservation for Knutsford Express for Joy Reynolds.
#       Pay 3 reservations for Knutsford Express for Joy Reynolds.

#   Testing error handling
#       Pay -3 reservations for Knutsford Express for Joy Reynolds.


def p_pay_command(p):
    """
    pay_command : KEYWORD_PAY RESERVATION FOR identifier_list FOR identifier_list SYM_END
                | KEYWORD_PAY INTEGER RESERVATIONS FOR identifier_list FOR identifier_list SYM_END
    """

    if type(p[2]) is int:
        if p[2] < 1:
            print(
                "Error: The number of reservations MUST be a positive number. Great than 0!"
            )
        else:
            p[0] = f"Pay {p[2]} reservations for {p[5]} for {p[7]}."
    else:
        p[0] = f"Pay reservation for {p[4]} for {p[6]}."


#   Examples:
#       Cancel reservation for Knutsford Express for Joy Reynolds.
#       Cancel 3 reservations for Knutsford Express for Joy Reynolds.

#   Testing error handling
#       Cancel -3 reservations for Knutsford Express for Joy Reynolds.


# Cancel reservations for a particular person.
def p_cancel_command(p):
    """
    cancel_command : KEYWORD_CANCEL RESERVATION FOR identifier_list FOR identifier_list SYM_END
                    | KEYWORD_CANCEL INTEGER RESERVATIONS FOR identifier_list FOR identifier_list SYM_END
    """

    if type(p[2]) is int:
        if p[2] < 1:
            print(
                "Error: The number of reservations MUST be a positive number. Great than 0!"
            )
        else:
            p[0] = f"Cancel {p[2]} reservations for {p[5]} for {p[7]}."
    else:
        p[0] = f"Cancel reservation for {p[4]} for {p[6]}."


#   Examples:
#       Transportation (Trains, Buses, Airlines):

#       List available schedule for Knutsford Express.
#       List available schedule for Knutsford Express from Montego Bay to Kingston.

#       List available tickets for Taylor Swift schedule.
#       List available tickets for bus from Ocho Rios to Negril.


# List all the available schedules from a hotel/company.
def p_list_command(p):
    """
    list_command : KEYWORD_LIST AVAILABLE SCHEDULE FOR identifier_list SYM_END
                | KEYWORD_LIST AVAILABLE SCHEDULE FOR identifier_list FROM identifier_list TO identifier_list SYM_END
                | KEYWORD_LIST AVAILABLE TICKETS FOR identifier_list FROM identifier_list TO identifier_list SYM_END

                | KEYWORD_LIST AVAILABLE TICKETS FOR CONCERT identifier_list IN identifier_list SYM_END
                | KEYWORD_LIST AVAILABLE TICKETS FOR CONCERT identifier_list AT identifier_list SYM_END

                | KEYWORD_LIST AVAILABLE TICKETS FOR identifier_list SYM_END
                | KEYWORD_LIST AVAILABLE TICKETS FOR identifier_list AT identifier_list SYM_END

                | KEYWORD_LIST AVAILABLE ACCOMMODATIONS IN identifier_list SYM_END
                | KEYWORD_LIST AVAILABLE ROOMS FOR identifier_list IN identifier_list SYM_END

                | KEYWORD_LIST AVAILABLE TICKETS FOR EVENT identifier_list IN identifier_list SYM_END
                | KEYWORD_LIST AVAILABLE TICKETS FOR EVENT identifier_list AT identifier_list SYM_END
    """

    try:
        system_prompt = f"""
        Tone and style instructions for the model:
            When responding to user queries about reservable resources (e.g., events, transportation, accommodations, concert, tickets).
            
            Please adhere to the following guidelines:
                Return just the JSON list of all the available information that is required for the service in question.
                Remove the ```json ``` form the JSON list. 
                No explanation needed.
                If no schedules or events are found then return an empty JSON list.
                Capitalize the first letter of each word in the key. Remove underscore if visible then space each word.
                
                In the JSON, list the dates in this format: February 17, 2025
            
            For Transportation Services (Trains, Buses, Airlines):
                In the list return only name of provider, route, departure time, arrival time, duration, price and available seats
                
            For Concert Tickets
                In the list, return only artist/band, venue, date, start time, ticket type, price, and available tickets.
            
            For Football Match Tickets:
                In the list, return only teams, stadium, date, start time, seat location, price, and available tickets.
            
            For Accommodation (Hotels, Rentals):
                In the list, return only property name, location, room number, check-in date, check-out date, room type/unit type, price per night, and available rooms/units.
            
            For General Events (Theater, Shows, etc.):
                In the list, return only event name, venue, date, start time, ticket type, price, and available tickets.
            
            For the price, also state the currency. i.e: $350 (JMD) or $350 (USD) 
        """

        s = ' '.join(p[1:])

        full_prompt = f"{system_prompt}\n\n{s}."

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=full_prompt
        )

        query = response.text.replace("```json", "").replace("```", "").strip("\n").strip()

        result = json.loads(query)

        if len(result) == 0:
            print(f"No schedules found for {p[5]}.")
        else:
            for item in result:
                keys = list(item.keys())

                for key, value in item.items():
                    print(f'{key}: {value}', end=",\n" if key != keys[-1] else "\n")

                if item != result[-1]:
                    print("\n")

        p[0] = s
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


#   Examples:
#       View schedule for Joy Reynolds.
#       View schedules for Joy Reynolds.


# Displays all the current schedules for a person.
def p_view_command(p):
    """
    view_command : KEYWORD_VIEW SCHEDULE FOR identifier_list SYM_END
                | KEYWORD_VIEW SCHEDULES FOR identifier_list SYM_END
    """

    if p[2] == "schedule":
        p[0] = f"View schedule for {p[4]}."
    else:
        p[0] = f"View schedules for {p[4]}."


#   Examples:
#       History for Joy Reynolds.


# Views all the schedules for a person.
def p_history_command(p):
    """
    history_command : KEYWORD_HISTORY FOR identifier_list SYM_END
    """

    p[0] = f"History for {p[3]}."


def p_help_command(p):
    """
    help_command : KEYWORD_HELP SYM_END
    """

    if len(p) == 3:
        p[0] = f"""
        Displaying available commands:

        book_command:
            Book ticket for <service> from <location> to <location> on <date> at <time> for <person>.
            Book <number> tickets for <service> from <location> to <location> on <date> at <time> for <person>.

        confirm_command:
            Confirm reservation for <service> for <person>.
            Confirm <number> reservations for <service> for <person>.

        pay_command:
            Pay <number> reservations for <identifiers> for <identifiers>.

        cancel_command:
            Cancel reservation for <identifiers> for <identifiers>.
            Cancel <number> reservations for <identifiers> for <identifiers>.

        list_command:
            List available schedule for <identifiers>.
            List available schedules for <identifiers>.

        view_command:
            View schedule for <identifiers>.
            View schedules for <identifiers>.

        history_command:
            History for <identifiers>.

        help_command:
            Display this help message.

        exit_command:
            Exit.

        clear_command:
            Clear.
            Cls.
        """


def p_exit_command(p):
    """exit_command : KEYWORD_EXIT SYM_END"""

    p[0] = "Exiting the system"
    exit()


# Error handling
def p_error(p):
    print(
        "Syntax error: Incorrect format. Please use one of the following command formats:"
    )

    command_formats = """
        Date format:
            <month> <day> <year>. Example: February 17, 2025

        ___________
        
        (12 hour time with AM/PM, 24 hour time)
        Time format:
            <hour>:<minute> AM/PM OR <hour>:<minute>. Example: 8:30 AM OR 20:30
            
        ___________

        Person format:
            <first_name> <last_name>. Example: Joy Reynolds
            "<first_name> <last_name>". Example: "Joy Reynolds"
            
        ___________

        Location format:
            <city>, <state>. Example: New York, NY
            "<city>, <state>". Example: "New York, NY"
        
        ___________
            
        Number format:
            <number>. Example: 2 (Should be greater than 0)

        ___________
        
        Book command:
            Book ticket for <service> from <location> to <location> on <date> at <time> for <person>.
            Book <number> tickets for <service> from <location> to <location> on <date> at <time> for <person>.
        
        ___________
            
        Confirm command:
            Confirm reservation for <service> for <person>.
            Confirm <number> reservations for <service> for <person>.
        
        ___________
            
        Pay command:
            Pay reservation for <service> for <person>.
            Pay <number> reservations for <service> for <person>.
        
        ___________
            
        Cancel command:
            Cancel reservation FOR <service> for <person>.
            Cancel <number> reservations for <service> for <person>.
        
        ___________

        List command:
            List <service> schedule.
            List <service> schedules.
        
        ___________
            
        View command:
            View schedule for <person>.
            View schedules for <person>.
        
        ___________

        History command:
            History for <person>.
        
        ___________
            
        Help command:
            Help.

        ___________
        
        Exit command:
            Exit.
        
        ___________

        Clear command:
            Clear.
            Cls.
    """

    print(command_formats)


# Build the parser
parser = yacc.yacc()


def connect_to_neon_psycopg3():
    global neon_db

    try:
        conn_string = os.getenv("DATABASE_URL")

        if not conn_string:
            raise ValueError("DATABASE_URL not found in .env file.")

        neon_db = psycopg.connect(conn_string)
        cur = neon_db.cursor()

        cur.execute("""
                    CREATE TABLE IF NOT EXISTS bookings (
                        booking_id SERIAL PRIMARY KEY,
                        customer_name VARCHAR(255) NOT NULL,
                        ticket_type VARCHAR(50) NOT NULL,
                        ticket_status VARCHAR(50) NOT NULL,
                        booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE TABLE IF NOT EXISTS general_events (
                        booking_id INTEGER PRIMARY KEY REFERENCES bookings(booking_id),
                        event_name VARCHAR(255) NOT NULL,
                        venue VARCHAR(255),
                        event_date DATE,
                        start_time TIME,
                        price VARCHAR(50),
                        available_tickets INTEGER
                    );
                    
                    CREATE TABLE IF NOT EXISTS transportation_tickets (
                        booking_id INTEGER PRIMARY KEY REFERENCES bookings(booking_id),
                        transportation_company VARCHAR(255),
                        departure_location VARCHAR(255),
                        arrival_location VARCHAR(255),
                        departure_time TIME,
                        departure_date DATE
                    );
                    
                    CREATE TABLE IF NOT EXISTS concert_tickets (
                        booking_id INTEGER PRIMARY KEY REFERENCES bookings(booking_id),
                        event_name VARCHAR(255) NOT NULL,
                        venue VARCHAR(255),
                        location VARCHAR(255),
                        event_date DATE,
                        start_time TIME,
                        seat_number VARCHAR(50),
                        price VARCHAR(50)
                    );
                    
                    CREATE TABLE IF NOT EXISTS accommodations (
                        booking_id INTEGER PRIMARY KEY REFERENCES bookings(booking_id),
                        property_name VARCHAR(255) NOT NULL,
                        location VARCHAR(255),
                        room_number VARCHAR(50),
                        check_in_date DATE,
                        check_out_date DATE,
                        room_type_unit_type VARCHAR(255),
                        price_per_night VARCHAR(50),
                        available_rooms_units VARCHAR(50)
                    );
                    
                    CREATE TABLE IF NOT EXISTS sports_tickets (
                        booking_id INTEGER PRIMARY KEY REFERENCES bookings(booking_id),
                        teams VARCHAR(255),
                        stadium VARCHAR(255),
                        event_date DATE,
                        start_time TIME,
                        seat_location VARCHAR(255),
                        price VARCHAR(50),
                        seat_number VARCHAR(50)
                    );
        """)

        neon_db.commit()

    except psycopg.OperationalError as e:
        print(f"Error: {e}")


def main():
    lexical_mode = False

    print("Welcome to APL Booking Project Language (APBL Version 1.0)\n")

    while True:
        try:
            s = input("APBL> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n")
            break
        if not s:
            continue
        elif s.lower() == "clear." or s.lower() == "cls.":
            os.system("clear")
            print("Welcome to APL Booking Project Language (APBL Version 1.0)\n")
            continue
        elif s.lower() == "exit.":
            print("Exiting the system...")
            neon_db.close()
            sys.exit()
        elif s.lower() == "stat lex_mode":
            if not lexical_mode:
                print("Compiler Status: Lexical analysis mode disabled.")
                print("Compiler Status: Syntax analysis mode enabled.\n")
                continue
            else:
                print("Compiler Status: Lexical analysis mode enabled.")
                print("Compiler Status: Syntax analysis mode disabled.\n")
                continue
        elif s.lower() == "set lex_mode=true":
            lexical_mode = True
            print("Compiler Status: Lexical analysis mode enabled.")
            print("Compiler Status: Syntax analysis mode disabled.\n")
            continue
        elif s.lower() == "set lex_mode=false":
            lexical_mode = False
            print("Compiler Status: Lexical analysis mode disabled.")
            print("Compiler Status: Syntax analysis mode enabled.\n")
            continue

        if lexical_mode:
            lexer.input(s)

            # Iterate through all tokens
            for tok in lexer:
                print(tok)
            print("\n")
        else:
            result = parser.parse(input=s, lexer=lexer, debug=False)

            print("\n")


if __name__ == "__main__":
    connect_to_neon_psycopg3()
    main()
