import sqlite3
import backend




class EventKeys:
    user_email = "user_email"
    event_id = "event_id"
    title = "title"
    description = "description"
    color = "color"
    start = "start"
    end = "end"
    url = "url"


class User:
    def new_event(self, title: str, description: str, color: str, start: str, end: str, url: str):
        self.user_events.new_event(title, description, color, start, end, url)

    def del_event(self, event_id: int | str):
        self.user_events.del_event_by_id(event_id)

    def update_event(self, event_id: int | str, title: str, description: str, color: str, start: str, end: str, url: str):
        self.user_events.del_event_by_id(event_id, id_not_exist_ok=False)
        self.user_events.new_event(title, description, color, start, end, url)

    @property
    def events(self) -> list[dict[str, str]]:
        return self.user_events.to_list_for_html


class Events:
    def __init__(self, email: str):
        connection = sqlite3.connect(backend.PATH_TO_DBFILE)
        cursor = connection.cursor()
        cursor.execute(f"SELECT {EventKeys.event_id} FROM UserEvents WHERE {EventKeys.user_email}=?", (email,))
        temp_all_events_id = cursor.fetchall()
        self.all_event_keys: set[int] = set()
        for event_id in temp_all_events_id:
            self.all_event_keys.add(int(event_id[0]))
        connection.close()
        if len(temp_all_events_id) != len(self.all_event_keys):
            raise IndexError("Events id in table are not unic!")

        self.email = email

    @property
    def events_score(self) -> int:
        return len(self.all_event_keys)

    def get_all_event(self, event_id: int | str) -> dict[str, str]:
        try:
            event_id = int(event_id)
            if event_id not in self.all_event_keys:
                raise ValueError()
        except ValueError:
            raise KeyError(f"Event '{event_id}' not exists for user '{self.email}'")
        return {
            EventKeys.event_id: str(event_id),
            EventKeys.user_email: self.email,
            EventKeys.title: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id,
                                                                           key=EventKeys.title),
            EventKeys.description: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id,
                                                                                 key=EventKeys.description),
            EventKeys.color: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id,
                                                                           key=EventKeys.color),
            EventKeys.start: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id,
                                                                           key=EventKeys.start),
            EventKeys.end: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id,
                                                                         key=EventKeys.end),
            EventKeys.url: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id,
                                                                         key=EventKeys.url),
        }

    def del_event_by_id(self, event_id: int | str, id_not_exist_ok=True):
        try:
            event_id = int(event_id)
            if event_id not in self.all_event_keys:
                raise ValueError()
        except ValueError:
            if id_not_exist_ok:
                return
            raise KeyError(f"Event '{event_id}' not exists for user '{self.email}'")
        connection = sqlite3.connect(backend.PATH_TO_DBFILE)
        cursor = connection.cursor()
        cursor.execute(
            f"DELETE FROM UserEvents WHERE {EventKeys.user_email}=? AND {EventKeys.event_id}=?",
            (self.email, event_id)
        )
        connection.commit()
        connection.close()
        self.all_event_keys.remove(event_id)

    def get_event_for_html(self, event_id: int | str) -> dict[str, str]:
        try:
            event_id = int(event_id)
            if event_id not in self.all_event_keys:
                raise ValueError()
        except ValueError:
            raise KeyError(f"Event '{event_id}' not exists for user '{self.email}'")
        return {
            EventKeys.title: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id, key=EventKeys.title),
            EventKeys.description: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id, key=EventKeys.description),
            EventKeys.color: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id, key=EventKeys.color),
            EventKeys.start: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id, key=EventKeys.start),
            EventKeys.end: get_value_from_event_db_by_email_and_event_id(email=self.email, event_id=event_id, key=EventKeys.end),
            EventKeys.url: f"http://{backend.PROJECT_HOST}:{backend.PROJECT_PORT}/event/{event_id}",
        }

    def __get_free_event_id(self) -> int:
        i = 0
        while i in self.all_event_keys:
            i += 1
        return i

    def new_event(self, title: str, description: str, color: str, file: str, start: str, end: str, url: str):
        connection = sqlite3.connect(backend.PATH_TO_DBFILE)
        cursor = connection.cursor()
        new_event_id = self.__get_free_event_id()
        cursor.execute(
            f"INSERT INTO UserEvents ({EventKeys.user_email}, {EventKeys.event_id}, {EventKeys.title}, {EventKeys.description}, {EventKeys.color}, {EventKeys.start}, {EventKeys.end}, {EventKeys.url}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (self.email, new_event_id, title, description, color, start, end, url,)
        )
        connection.commit()
        connection.close()
        self.all_event_keys.add(new_event_id)

    @property
    def to_list_for_html(self) -> list[dict[str, str]]:
        result = []
        for event_id in self.all_event_keys:
            result.append(self.get_event_for_html(event_id))
        return result


init_connection = sqlite3.connect(backend.PATH_TO_DBFILE)
init_cursor = init_connection.cursor()
init_cursor.execute(f'''CREATE TABLE IF NOT EXISTS Users (
{UserKeys.email} TEXT PRIMARY KEY,
{UserKeys.encrypted_password} TEXT NOT NULL,
{UserKeys.username} TEXT
)''')
init_cursor.execute(
    f'CREATE INDEX IF NOT EXISTS idx_email ON Users ({UserKeys.email})'
)
init_cursor.execute(f'''CREATE TABLE IF NOT EXISTS UserEvents (
{EventKeys.user_email} TEXT NOT NULL,
{EventKeys.event_id} INTEGER NOT NULL,
{EventKeys.title} TEXT,
{EventKeys.description} TEXT,
{EventKeys.color} TEXT,
{EventKeys.start} TEXT,
{EventKeys.end} TEXT,
{EventKeys.url} TEXT,
FOREIGN KEY({EventKeys.user_email}) REFERENCES Users(rowid)
)''')
init_connection.commit()
init_connection.close()


def get_encrypt_string(input_string: str) -> str:
    return hashlib.sha256(input_string.encode()).hexdigest()
