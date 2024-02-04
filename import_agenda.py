import xlrd
import sys
from db_table import db_table

# SQLite Database table schema
AGENDA_TABLE_SCHEMA = {
    "id": "integer PRIMARY KEY",
    "date": "text",
    "time_start": "text",
    "time_end": "text",
    "session_type": "text",
    "session_title": "text",
    "location": "text",
    "description": "text",
    "speakers": "text",
    "parent_id": "integer"
}

class Agenda:
    def __init__(self, date, time_start, time_end, session_type, session_title, location, description, speakers):
        """
        Initialize an Agenda object.

        Parameters:
        - date (str): The date of the agenda.
        - time_start (str): The start time of the agenda.
        - time_end (str): The end time of the agenda.
        - session_type (str): The type of session.
        - session_title (str): The title of the session.
        - location (str): The location of the session.
        - description (str): The description of the session.
        - speakers (str): The speakers for the session.
        """
        self.date = date
        self.time_start = time_start
        self.time_end = time_end
        self.session_type = session_type
        self.session_title = session_title
        self.location = location
        self.description = description
        self.speakers = speakers
        self.sub_sessions = []

    def add_sub_session(self, sub_session):
        """
        Add a sub-session to the list of sub-sessions.

        Parameters:
        - sub_session (Agenda): The sub-session to be added.
        """
        self.sub_sessions.append(sub_session)

def parse_excel(filename):
    """
    Parse an Excel file and extract agenda information.

    Parameters:
    - filename (str): The name of the Excel file.

    Returns:
    - list: A list of Agenda objects.
    """
    sheet = xlrd.open_workbook(filename).sheet_by_index(0)
    agendas, current_session = [], None
    
    for row_idx in range(16, sheet.nrows):
        row = sheet.row_values(row_idx)
        
        # Create agenda object
        agenda = Agenda(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])

        # If it's a session, update current session
        if row[3] == "Session":
            current_session = agenda
            agendas.append(current_session)
        # If it's a sub-session, add it under the current session
        elif current_session:
            current_session.add_sub_session(agenda)

    return agendas

def import_agenda(agendas):
    """
    Import agenda information into the database.

    Parameters:
    - agendas (list): A list of Agenda objects.
    """
    agenda_table = db_table("agendas", AGENDA_TABLE_SCHEMA)
    try:
        for agenda in agendas:
            # Insert session into the database
            agenda_item = {
                "date": agenda.date,
                "time_start": agenda.time_start,
                "time_end": agenda.time_end,
                "session_type": agenda.session_type,
                "session_title": agenda.session_title,
                "location": agenda.location,
                "description": agenda.description,
                "speakers": agenda.speakers,
                "parent_id": None
            }
            session_id = agenda_table.insert(agenda_item)

            # Insert sub-sessions under the session
            for sub_session in agenda.sub_sessions:
                sub_item = {
                    "date": sub_session.date,
                    "time_start": sub_session.time_start,
                    "time_end": sub_session.time_end,
                    "session_type": sub_session.session_type,
                    "session_title": sub_session.session_title,
                    "location": sub_session.location,
                    "description": sub_session.description,
                    "speakers": sub_session.speakers,
                    "parent_id": session_id
                }
                agenda_table.insert(sub_item)
        print("Import complete!")
    except Exception as e:
        print(f"Error during import: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        agendas = parse_excel(filename)
        import_agenda(agendas)
    else:
        print("Incorrect number of arguments!")
        print("import_agenda.py <filename>")