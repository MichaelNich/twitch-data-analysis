import ibm_db
import os
import json
import logging

# set up logging config
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DatabaseManager:
    def __init__(self):
        self.conn = None
        # creates logging object to monitor the results.
        self.logger = logging.getLogger(__name__)

    def connect_to_db(self):
        # Connect to the db2 database
        with open("config.json") as config_file:
            config = json.load(config_file)

        dsn_hostname = config["dsn_hostname"]
        dsn_uid = config["dsn_uid"]
        dsn_pwd = config["dsn_pwd"]
        dsn_driver = config["dsn_driver"]
        dsn_database = config["dsn_database"]
        dsn_port = config["dsn_port"]
        dsn_protocol = config["dsn_protocol"]
        dsn_security = config["dsn_security"]

        dsn = (
            "DRIVER={0};"
            "DATABASE={1};"
            "HOSTNAME={2};"
            "PORT={3};"
            "PROTOCOL={4};"
            "UID={5};"
            "PWD={6};"
            "SECURITY={7};"
        ).format(
            dsn_driver,
            dsn_database,
            dsn_hostname,
            dsn_port,
            dsn_protocol,
            dsn_uid,
            dsn_pwd,
            dsn_security,
        )

        try:
            self.conn = ibm_db.connect(dsn, "", "")
            self.logger.info(
                "Connected to database: %s as user: %s on host: %s",
                dsn_database,
                dsn_uid,
                dsn_hostname,
            )
        except Exception as e:
            self.logger.warning("Unable to connect: %s", str(e))

    def insert_streamers_to_db(self, streamers: dict):
        """ "Inserts streamer's data into the STREAMERS table in the DB2 database."

        This method allows inserting data for multiple streamers into the database.

        Args:
            streamers (dict): A dictionary containing streamer data.
                Each key represents the streamer's name, and the corresponding value is a dictionary
                with the following structure:
                {
                    "views": "1.1k spectators",  # (str) The number of viewers for the streamer.
                    "category": "FPS",           # (str) The category/genre of the streamer's content.
                    "date": date,                # (str) The date of data recording with format "%d/%m/%Y %H:%M".
                    "lang": language,            # (str) The language used by the streamer.
                }
        Example:
            streamers_data = {
                "Streamer1": {
                    "views": "1.1k spectators",
                    "category": "FPS",
                    "date": datetime.date(2023, 7, 24),
                    "lang": "English",
                },
                "Streamer2": {
                    "views": "2.3k spectators",
                    "category": "RPG",
                    "date": datetime.date(2023, 7, 24),
                    "lang": "Spanish",
                },
            }
            insert_streamers_to_db(streamers_data)
        """
        if self.conn is None:
            print("Not connected to the database. Please connect first.")
            return
        # create list to count sucess and fail when inserting (index 0 = sucess, index 1 = fail)
        self.result = [0, 0]

        # Insert values into the db2 database
        for key, value in streamers.items():
            views = value["views"]
            name = key.replace("'", "")
            categories = value["category"].replace("'", "")
            date = value["date"]
            lang = value["lang"]
            # print(views, name, categories)

            insertQuery = (
                "INSERT INTO STREAMERS (streamer_names, streamer_views, category_names, lang, date) VALUES ('"
                + name
                + "', '"
                + views
                + "', '"
                + categories
                + "', '"
                + lang
                + "', TIMESTAMP_FORMAT('"
                + date
                + "', 'DD/MM/YYYY HH24:MI'))"
            )

            # execute the insert statement
            try:
                insertStmt = ibm_db.exec_immediate(self.conn, insertQuery)
                # increment 1 to the result[sucess]
                self.result[0] += 1
                # print("Inserted streamer values to the STREAMERS table")
            except Exception as e:
                # increment 1 to the result[fail]
                self.result[1] += 1
                # create dictionary with the data that failed to be inserted into the database
                data = {
                    name: {
                        "views": views,
                        "category": categories,
                        "date": date,
                        "lang": lang,
                    }
                }
                print("An error occurred during database insertion:", e)
                self.save_to_backup_folder(data)
        # Print the result only if there were fails when trying to insert
        if self.result[1] > 0:
            print(
                f"There were a total of {self.result[0]} Sucesses, And {self.result[1]} fails when trying to insert into the database. Lang: {lang}"
            )

    def save_to_db(self, twitch):
        if self.conn is None:
            print("Not connected to the database. Please connect first.")
            return
        # Insert values into the db2 database
        for key, value in twitch.items():
            views = value["views"]
            name = key
            categories = value["category"]
            date = value["date"]

            # INSERT INTO DB
            # insertQuery = ("INSERT INTO GAMES (NAME, VIEWS) VALUES ('"+ name+ "', "+ str(views)+ ")")
            insertQuery = (
                "INSERT INTO GAMES (NAME, VIEWS, DATE) VALUES ('"
                + name
                + "', '"
                + views
                + "', TIMESTAMP_FORMAT('"
                + date
                + "', 'DD/MM/YYYY HH24:MI'))"
            )

            # execute the insert statement
            insertStmt = ibm_db.exec_immediate(self.conn, insertQuery)
            # print("Inserted games values to the GAMES table")

            # Check if values exists and insert into categories
            for cat in categories:
                game_categories_name = "SELECT category FROM CATEGORIES WHERE game_name = ? AND category = ?"
                game_stmt = ibm_db.prepare(self.conn, game_categories_name)
                ibm_db.bind_param(game_stmt, 1, name)
                ibm_db.bind_param(game_stmt, 2, cat)
                ibm_db.execute(game_stmt)
                game_category_name = ibm_db.fetch_assoc(game_stmt)
                if game_category_name:
                    pass
                    # print("Game Category already inside the categories table!")
                else:
                    categories_query = (
                        "INSERT INTO CATEGORIES (game_name, category) VALUES (?, ?)"
                    )
                    categories_stmt = ibm_db.prepare(self.conn, categories_query)
                    ibm_db.bind_param(categories_stmt, 1, name)
                    ibm_db.bind_param(categories_stmt, 2, cat)
                    ibm_db.execute(categories_stmt)
                    # print("Inserted category values to the CATEGORIES table")

    def save_to_backup_folder(self, data):
        backup_folder = "fails_storage"
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        # check if the lang value exists, if it exists then save as streamers data
        game_name = next(iter(data))
        if "lang" in data[game_name]:
            # create filename named streamers
            filename = f"{backup_folder}/streamers.txt"
        else:
            # create filename named games.txt
            filename = f"{backup_folder}/games.txt"
        # Write the data to the appropriate file
        with open(filename, "a", encoding="utf-8") as file:
            file.write(json.dumps(data) + "\n")

    def insert_backup_files(self):
        backup_folder = "fails_storage"
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        if self.conn is None:
            print("Not connected to the database. Please connect first.")
            return
        # check if games.txt is empty, in case it is not, we procede to insert the data.
        files_path = ["fails_storage/streamers.txt", "fails_storage/games.txt"]
        # creates for loop to insert data first into streamers.txt and last in the games.txt
        for n_file in range(2):
            _path = files_path[n_file]
            # check if files exists, if not then creates it
            if not os.path.exists(_path):
                with open(_path, "w") as create_file:
                    create_file.write("")
            failed_rows = []
            # check if the streamers.txt or games.txt are empty
            if os.path.getsize(_path) == 0:
                print("File: ", _path, " is empty!")
            else:
                with open(_path, "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        data = json.loads(line)
                        try:
                            if n_file == 0:
                                self.insert_streamers_to_db(data)
                            else:
                                self.save_to_db(data)
                        except Exception as e:
                            failed_rows.append(data)
                with open(_path, "w") as write_file:
                    # if failed_rows is empty tries to clear the streamers.txt by writing a empty text
                    if failed_rows:
                        write_file.writelines(json.dumps(failed_rows) + "\n")
                    else:
                        write_file.write("")
                print("Finished inserting streamers from the file into the database.")

    def close_connection(self):
        if self.conn is not None:
            ibm_db.close(self.conn)
            self.conn = None
            print("Connection closed!")
        else:
            print("No active connection to close.")
