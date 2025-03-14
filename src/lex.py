import json

import ply.lex as lex
import ply.yacc as yacc
import os
import calendar

from google import genai
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")
gemini_api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=f"{gemini_api_key}")

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
    "ticket": "KEYWORD_TICKET",
    "tickets": "KEYWORD_TICKETS",
    "reservation": "RESERVATION",
    "reservations": "RESERVATIONS",
    "schedule": "SCHEDULE",
    "schedules": "SCHEDULES",
    "from": "FROM",
    "to": "TO",
    "on": "ON",
    "at": "AT",
    "for": "FOR",
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


# Date values (Month Day, Year)
def t_date(t):
    r"""(January|February|March|April|May|June|July|August|September|October|November|December)\s?\d{1,2},\s?\d{4}"""
    t.type = "DATE"
    return t


# Time values (12 hour time with AM/PM, 24 hour time)
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
    r"""\".*?\" """
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
    """

    if len(p) == 3:
        p[0] = f"{p[1]} {p[2]}"
    else:
        p[0] = p[1]


# Example commands
# Book ticket for Knutsford Express from Montego Bay to Kingston on February 17, 2025 at 8:30 AM for Joy Reynolds.
# Book 2 tickets for Knutsford Express from Montego Bay to Kingston on February 17, 2025 at 8:30 AM for Joy Reynolds.

# Testing the date validation
# Book 2 tickets for Knutsford Express from Montego Bay to Kingston on February 29, 2025 at 8:30 AM for Joy Reynolds.
# Book 2 tickets for Knutsford Express from Montego Bay to Kingston on February 29, 2025 at 8:30 AM for Joy Reynolds.


def p_book_command(p):
    """
    book_command : KEYWORD_BOOK KEYWORD_TICKET FOR identifier_list FROM identifier_list TO identifier_list ON DATE AT TIME FOR identifier_list SYM_END
                 | KEYWORD_BOOK INTEGER KEYWORD_TICKETS FOR identifier_list FROM identifier_list TO identifier_list ON DATE AT TIME FOR identifier_list SYM_END
    """

    # Specific the numbers of tickets the user wants
    if type(p[2]) is int:

        # Validation for date
        month_day, year = p[11].split(",")
        month, day = month_day.split(" ")

        day = int(day)
        month = months[month]
        year = int(year)

        if p[2] < 1:
            print(
                "Error: The number of tickets MUST be a positive number. Great than 0!"
            )
        else:
            if day not in range(1, calendar.monthrange(year, month)[1] + 1):
                print(
                    f"Error: The day {day} does not exist in {calendar.month_name[month]} {year}."
                )
            else:
                p[0] = (
                    f"Book {p[2]} tickets for {p[5]} from {p[7]} to {p[9]} on {p[11]} at {p[13]} for {p[15]}."
                )
    # The user only wants on ticket
    else:
        # Validation for date
        month_day, year = p[10].split(",")
        month, day = month_day.split(" ")

        day = int(day)
        month = months[month]
        year = int(year)

        if day not in range(1, calendar.monthrange(year, month)[1] + 1):
            print(
                f"Error: The day {day} does not exist in {calendar.month_name[month]} {year}."
            )
        else:
            if day not in range(1, calendar.monthrange(year, month)[1] + 1):
                print(
                    f"Error: The day {day} does not exist in {calendar.month_name[month]} {year}."
                )
            else:
                p[0] = (
                    f"Book a ticket for {p[2]} from {p[4]} to {p[6]} on {p[8]} at {p[10]} for {p[12]}."
                )


# Examples:
#  Confirm reservation for Knutsford Express for Joy Reynolds.
#  Confirm 3 reservations for Knutsford Express for Joy Reynolds.

# Testing error handling
#  Confirm -3 reservations for Knutsford Express for Joy Reynolds.


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


# Examples:
#  Pay reservation for Knutsford Express for Joy Reynolds.
#  Pay 3 reservations for Knutsford Express for Joy Reynolds.

# Testing error handling
#  Pay -3 reservations for Knutsford Express for Joy Reynolds.


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


# Examples:
#  Cancel reservation for Knutsford Express for Joy Reynolds.
#  Cancel 3 reservations for Knutsford Express for Joy Reynolds.

# Testing error handling
#  Cancel -3 reservations for Knutsford Express for Joy Reynolds.


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


# Examples:
#  List Knutsford Express schedule.
#  List Taylor Swift schedule.


# List all the available schedules from a hotel/company.
def p_list_command(p):
    """
    list_command : KEYWORD_LIST identifier_list SCHEDULE SYM_END
    """

    try:
        system_prompt = f"""
        When responding to user queries about reservable resources (e.g., events, transportation, accommodations, concert, tickets).
        
        Please adhere to the following guidelines:
            Return just the JSON list of all the available information that is required for the service in question.
            Remove the ```json ``` form the JSON list. 
            No explanation needed.
            If no schedules or events are found then return an empty JSON list.
            Capitalize the first letter of each word in the key.
        
        For Transportation Services (Trains, Buses, Airlines):
            In the list return only route, departure time, arrival time, duration, price and available seats
            
        For Concert Tickets
            In the list, return only artist/band, venue, date, start time, ticket type, price, and available tickets.
        
        For Football Match Tickets:
            In the list, return only teams, stadium, date, start time, seat location, price, and available tickets.
        
        For Accommodation (Hotels, Rentals):
            In the list, return only property name, location, check-in date, check-out date, room type/unit type, price per night, and available rooms/units.
        
        For General Events (Theater, Shows, etc.):
            In the list, return only event name, venue, date, start time, ticket type, price, and available tickets.
        """

        full_prompt = f"{system_prompt}\n\nWhat are the available schedules for {p[2]}."

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=full_prompt
        )

        # print(response.text)

        query = response.text.replace("```json", "").replace("```", "").strip("\n").strip()
        # print(f"{query}")

        result = json.loads(query)

        if len(result) == 0:
            print(f"No schedules found for {p[2]}.")
        else:
            for item in result:
                keys = list(item.keys())

                for key, value in item.items():
                    print(f'{key}: {value}', end=",\n" if key != keys[-1] else "\n")

                if item != result[-1]:
                    print("\n")

        p[0] = f"List available schedule for {p[2]}."
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


# Examples:
#  View schedule for Joy Reynolds.
#  View schedules for Joy Reynolds.


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


# Examples:
#  History for Joy Reynolds.


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
    main()
