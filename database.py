import sqlite3


class Database:
    def __init__(self, db_path="data.sqlite"):
        """Initialization: path, connect to database, create required variables."""
        self.db_path = db_path
        self.connect()
        self.create_table()

    def connect(self):
        """Connection: connect to database, create cursor variable."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            exit(1)

    def create_table(self):
        """Create the only one table with columns - id, title, description, url, cost, date_posted, ai_description"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS kwork (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255),
                description VARCHAR(255),
                url VARCHAR(255),
                cost INTEGER,
                date_posted TIMESTAMP,
                ai_description VARCHAR(255)
            );
        """)

    def insert(self, title, description, url, card_cost, date_posted, ai_description):
        """Inserts user-provided values into the specified table(kwork)."""
        self.cursor.execute(
            """
            INSERT INTO kwork (
                title,
                description,
                url,
                cost,
                date_posted,
                ai_description
            )
            VALUES (?,?,?,?,?,?) 
        """,
            (title, description, url, card_cost, date_posted, ai_description),
        )

    def fetch_all(self):
        """Outputs all the values from the table `kwork`"""
        self.cursor.execute("""SELECT * FROM kwork""")
        return self.cursor.fetchall()

    def commit(self):
        """Commits the change to the table"""
        self.conn.commit()

    def close(self):
        """Closes connection"""
        self.cursor.close()
        self.conn.close()


def main():
    base = Database()
    for row in base.fetch_all():
        print(row)


if __name__ == "__main__":
    main()
