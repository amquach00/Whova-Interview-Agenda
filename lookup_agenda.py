import sys
import sqlite3

class AgendaLookup:
    DB_NAME = "interview_test.db"
    
    def __init__(self):
        """
        Initialize AgendaLookup object and establish a connection to the SQLite database.
        """
        self.conn = sqlite3.connect(self.DB_NAME)
        self.cursor = self.conn.cursor()
        
    def execute_query(self, query, params=None):
        """
        Execute a SQL query on the database.

        Parameters:
        - query (str): The SQL query to be executed.
        - params (tuple, optional): The parameters to be used in the query.

        Returns:
        - list: A list of rows returned by the query.
        """
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def lookup_agendas(self, column, value):
        """
        Find and print agenda information based on the specified column and value.

        Parameters:
        - column (str): The column to search for.
        - value (str): The value to search for in the specified column.
        """
        #1 Find sessions based on the column and value
        if column == "speakers":
            query = "SELECT * FROM agendas WHERE speakers LIKE ?"
            sessions = self.execute_query(query, ('%' + value + '%',))
        else:
            query = f"SELECT * FROM agendas WHERE {column} LIKE ?"
            sessions = self.execute_query(query, (value,))
            sub_sessions = []
            for session in sessions:
                if session[4] == "Session":
                    sub_session_query = "SELECT * FROM agendas WHERE session_type = 'Sub' AND parent_id = ?"
                    self.cursor.execute(sub_session_query, (session[0],))
                    sub_sessions.extend(self.cursor.fetchall())
            sessions.extend(sub_sessions)
        
        #2 Print session details    
        self.print_session_details(sessions)
        
    def print_session_details(self, sessions):
        """
        Print the details of agenda sessions.

        Parameters:
        - sessions (list): A list of agenda sessions.
        """
        if (sessions.count == 0):
            print("No sessions found!")
            return
        
        count = 1
        session_headers = ["Date", "Time Start", "Time End", "Session Type", "Session Title", "Location", "Description", "Speakers"]
        for session in sessions:
            print("-" * 50)
            print("Event #", count)
            count += 1
            for header, value in zip(session_headers, session[1:]):
                print(f"{header}: {value}")
        print("-" * 50)

    def close_connection(self):
        """
        Close the connection to the SQLite database.
        """
        self.conn.close()

if __name__ == "__main__":
    if (len(sys.argv) == 3):
        column, value = sys.argv[1], sys.argv[2]
        if column not in ["date", "time_start", "time_end", "session_title", "location", "description", "speakers"]:
            print("Invalid column name!")
            print("Valid column choices: date, time_start, time_end, session_title, location, description, speakers")
            sys.exit()
        else: 
            lookup_tool = AgendaLookup()
            lookup_tool.lookup_agendas(column, value)
            lookup_tool.close_connection()
    else:
        print("Incorrect number of arguments!")
        print("./lookup_agenda.py <column> <value>")
        print("Valid column choices: date, time_start, time_end, session_title, location, description, speakers")