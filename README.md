# Swift Bookings - AI Ticket Booking Simulator

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![AI](https://img.shields.io/badge/AI-Gemini-4285F4)
![Database](https://img.shields.io/badge/DB-Neon%20Postgres-24b1a4)

## Overview

Swift Bookings is a terminal-based Python application designed as an AI-powered ticket booking simulator[cite: 1]. It leverages Google's Gemini AI to understand and process booking requests phrased in a specific command language[cite: 1, 18, 35, 53]. The application uses the Neon Serverless Postgres platform to simulate the persistence of user and booking data [cite: 1, 36-41]. It features a custom command-line interface built using the PLY (Python Lex-Yacc) library for parsing user input[cite: 1, 4].

**Note:** This application is a simulator. While it uses a real AI model (Gemini) and connects to a real database platform (Neon), the booking validation, availability checks, and pricing are largely simulated based on the prompts sent to the AI model [cite: 19-34, 54-68, 88-102].

## Features

* **AI-Powered Command Processing:** Uses Google Gemini to interpret parsed commands, simulate data validation/availability, and structure booking information[cite: 1, 18, 35, 53].
* **Custom Command Language:** Implements a specific syntax for booking, confirming, paying, canceling, listing, and viewing tickets using PLY (Lex & Yacc) [cite: 1, 5, 8-18, 41-52, 75-86, 106-119].
* **Database Integration:** Connects to a Neon Serverless Postgres database using `psycopg` to store user details and booking records across various ticket types [cite: 1, 36-41, 70-75, 104-106].
* **Ticket Types Supported (Simulated):**
    * General Event Tickets [cite: 26, 61, 95]
    * Transportation Tickets (e.g., Buses) [cite: 26, 61, 95]
    * Concert Tickets [cite: 26, 61, 95]
    * Accommodation Bookings [cite: 27, 62, 96]
    * Sports Tickets [cite: 27, 62, 96]
* **Booking Lifecycle Simulation:** Allows users to `Book`, `Confirm`, `Pay`, and `Cancel` bookings, updating the status in the database [cite: 5, 8-18, 41-52, 75-86, 106-111].
* **Information Display:**
    * List available tickets/events (`List available ...`) [cite: 5, 111-114].
    * View details of a specific booked ticket (`View ticket ...`) [cite: 5, 114-117].
    * View user's booking history (`History for ...`) [cite: 5, 117-118].
    * Display results in formatted tables using `tabulate`[cite: 1, 111, 114].
* **Help Command:** Provides basic usage information [cite: 5, 118-119].
* **Debugging Modes:** Allows switching between lexical analysis mode (shows tokens) and syntax analysis/execution mode[cite: 120].

## Technologies Used

* **Language:** Python 3.x [cite: 1]
* **AI Model:** Google Gemini (via `google-generativeai` SDK) [cite: 1]
* **Database:** Neon Serverless Postgres (via `psycopg` library) [cite: 1]
* **Parsing:** PLY (Python Lex-Yacc) [cite: 1]
* **Output Formatting:** `tabulate` [cite: 1]
* **Other Libraries:** `json`, `os`, `sys`, `logging`, `platform` [cite: 1]

## Prerequisites

Before running the application, ensure you have the following:

1.  **Python 3:** Version 3.x recommended.
2.  **Google Gemini API Key:** Obtain an API key from Google AI Studio ([https://aistudio.google.com/](https://aistudio.google.com/)).
3.  **Neon Account & Database:**
    * Sign up for a Neon account ([https://neon.tech/](https://neon.tech/)).
    * Create a project and obtain the connection string (Database URL) for your Postgres database.

## Setup & Installation

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```
    *(Replace `<your-repository-url>` and `<your-repository-directory>`)*

2.  **Set up a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Python Dependencies:**
    Create a `requirements.txt` file with the following content:
    ```txt
    google-generativeai
    psycopg[binary] # Using binary for easier install, adjust if needed
    ply
    tabulate
    python-dotenv # Recommended for handling secrets
    ```
    Then install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Secrets (IMPORTANT):**
    * **SECURITY WARNING:** The provided code (`swift_bookings.py`) contains **hardcoded** secrets (Gemini API Key and Neon Database URL)[cite: 1]. **Do not commit this code with hardcoded secrets to version control.**
    * **Recommendation:** Use environment variables. Create a file named `.env.local` in the root directory of your project:
        ```dotenv
        # .env file
        GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
        DATABASE_URL="YOUR_NEON_DATABASE_URL"
        ```
        Replace `YOUR_GEMINI_API_KEY` and `YOUR_NEON_DATABASE_URL` with your actual credentials.
    * **Modify the Python Code:** Update the script (`swift_bookings.py` or your renamed file) to load these variables using `python-dotenv` and `os.getenv()` instead of using the hardcoded strings.
        * Add `from dotenv import load_dotenv` and `import os` at the top.
        * Call `load_dotenv()` after imports.
        * Replace the hardcoded lines with:
            ```python
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            DATABASE_URL = os.getenv("DATABASE_URL")

            if not GEMINI_API_KEY or not DATABASE_URL:
                print("Error: GEMINI_API_KEY or DATABASE_URL not found in environment variables/.env file.")
                sys.exit(1)

            # Initialize client and connect to DB using these variables
            client = genai.Client(api_key=GEMINI_API_KEY)
            # ... connect_to_neon_psycopg3 function likely needs modification ...
            ```
    * **Add `.env` to `.gitignore`:** Make sure your `.env` file is listed in your `.gitignore` file to prevent accidentally committing secrets.

5.  **Set up Database Schema:**
    * Connect to your Neon database using a tool like `psql` or a GUI client.
    * Execute SQL `CREATE TABLE` statements to create the necessary tables (`users`, `bookings`, `general_events`, `transportation_tickets`, `concert_tickets`, `accommodations`, `sports_tickets`) based on the schema inferred from the `INSERT` and `SELECT` statements within the Python code [cite: 36-41, 70-75, 104-106, 111-118]. See the "Database Schema (Conceptual)" section below.

## Running the Application

1.  Make sure you have configured your `.env` file correctly and modified the script to use it.
2.  Ensure your Neon database is ready and the schema is created.
3.  Navigate to the project directory in your terminal.
4.  Activate your virtual environment (if using one): `source venv/bin/activate` (or `venv\Scripts\activate` on Windows).
5.  Run the main Python script (assuming it's named `swift_bookings.py` after renaming):
    ```bash
    python swift_bookings.py
    ```
6.  The application will display `Swift Bookings >>>` prompt. Enter commands according to the defined syntax (e.g., `Book ticket for ... .`, `List available ... .`, `Help.`, `Exit.`). Remember to end commands with a period (`.`).

## How It Works (Conceptual Flow)

1.  **Initialization:** The script connects to the Neon database and initializes the Gemini client[cite: 1, 122].
2.  **User Input:** The application waits for user input at the prompt[cite: 120].
3.  **Lexical Analysis (Optional Mode):** If `lex_mode` is true, input is tokenized by PLY's lexer, and tokens are printed[cite: 120].
4.  **Syntax Analysis & Parsing:** If `lex_mode` is false (default), PLY's parser attempts to match the input tokens against the defined grammar rules (`p_book_command`, `p_confirm_command`, etc.).
5.  **AI Processing (within Parser Actions):**
    * For commands like `Book`, `Confirm`, `Pay`, `Cancel`, the matched parser function constructs a detailed prompt for Gemini, including instructions on how to validate/simulate the request and the desired JSON output format [cite: 18-35, 53-69, 87-103, 106].
    * Gemini processes the prompt and returns a response, ideally a JSON string containing simulated booking details or an error message[cite: 35, 69, 103].
6.  **Database Interaction:**
    * The application parses the JSON response from Gemini[cite: 35, 69, 103].
    * It interacts with the Neon database:
        * Checks for existing users or creates new ones[cite: 36].
        * Inserts new booking records and associated details into relevant tables (`bookings`, `general_events`, etc.) for `Book` commands.
        * Updates booking status (`Confirmed`, `Paid`, `Cancelled`) for `Confirm`, `Pay`, `Cancel` commands[cite: 71, 72, 73, 74, 75, 105, 106].
        * Retrieves data for `List`, `View`, `History` commands.
7.  **Output:** Confirmation messages, error messages, or formatted tables (using `tabulate`) are printed to the console[cite: 111, 114].
8.  **Loop/Exit:** The application loops back to wait for the next command or exits if the user types `Exit.`[cite: 120].

## Configuration

The application requires the following environment variables to be set (e.g., in a `.env` file):

* `GEMINI_API_KEY`: Your API key for the Google Gemini AI service.
* `DATABASE_URL`: The full connection string for your Neon Serverless Postgres database.

**Reminder:** Modify the Python script to load these variables securely instead of using the hardcoded values found in the original code[cite: 1].

## Database Schema (Conceptual)

Based on the code, the application expects a schema similar to this on your Neon Postgres database:

* **`users`**
    * `user_id` (SERIAL PRIMARY KEY)
    * `customer_name` (VARCHAR) - *Unique constraint might be useful*
* **`bookings`**
    * `booking_id` (SERIAL PRIMARY KEY)
    * `user_id` (INTEGER, REFERENCES users(user_id))
    * `ticket_type` (VARCHAR) - e.g., 'General Event', 'Transportation', 'Concert', 'Accommodation', 'Sports'
    * `ticket_status` (VARCHAR) - e.g., 'Booked', 'Confirmed', 'Paid', 'Cancelled'
    * `tickets_booked` (INTEGER)
* **`general_events`**
    * `event_booking_id` (SERIAL PRIMARY KEY)
    * `booking_id` (INTEGER, REFERENCES bookings(booking_id))
    * `event_name` (VARCHAR)
    * `venue` (VARCHAR)
    * `event_date` (DATE)
    * `start_time` (TIME)
    * `price` (VARCHAR or DECIMAL)
    * `available_tickets` (INTEGER) - *Simulated value from AI?*
* **`transportation_tickets`**
    * `transport_booking_id` (SERIAL PRIMARY KEY)
    * `booking_id` (INTEGER, REFERENCES bookings(booking_id))
    * `transportation_company` (VARCHAR)
    * `departure_location` (VARCHAR)
    * `arrival_location` (VARCHAR)
    * `departure_time` (TIME)
    * `departure_date` (DATE)
    * `arrival_time` (TIME) - *Simulated value from AI?*
    * `arrival_date` (DATE) - *Simulated value from AI?*
    * `seat_number` (VARCHAR) - *Simulated value from AI?*
* **`concert_tickets`**
    * `concert_booking_id` (SERIAL PRIMARY KEY)
    * `booking_id` (INTEGER, REFERENCES bookings(booking_id))
    * `event_name` (VARCHAR)
    * `venue` (VARCHAR)
    * `location` (VARCHAR)
    * `event_date` (DATE)
    * `start_time` (TIME)
    * `seat_number` (VARCHAR) - *Simulated value from AI?*
    * `price` (VARCHAR or DECIMAL)
* **`accommodations`**
    * `accom_booking_id` (SERIAL PRIMARY KEY)
    * `booking_id` (INTEGER, REFERENCES bookings(booking_id))
    * `property_name` (VARCHAR)
    * `location` (VARCHAR)
    * `room_number` (VARCHAR) - *Simulated value from AI?*
    * `check_in_date` (DATE)
    * `check_out_date` (DATE)
    * `check_in_time` (TIME)
    * `room_type_unit_type` (VARCHAR) - *Simulated value from AI?*
    * `price_per_night` (VARCHAR or DECIMAL)
    * `available_rooms_units` (INTEGER) - *Simulated value from AI?*
* **`sports_tickets`**
    * `sports_booking_id` (SERIAL PRIMARY KEY)
    * `booking_id` (INTEGER, REFERENCES bookings(booking_id))
    * `teams` (VARCHAR)
    * `stadium` (VARCHAR)
    * `event_date` (DATE)
    * `start_time` (TIME)
    * `seat_location` (VARCHAR) - *Simulated value from AI?*
    * `price` (VARCHAR or DECIMAL)
    * `seat_number` (VARCHAR) - *Simulated value from AI?*

*(Note: Data types like VARCHAR length, constraints, and exact simulation logic might need adjustment based on actual implementation details.)*
