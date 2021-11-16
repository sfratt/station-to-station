import sqlite3

from src.models.client import Client


class ClientStore():

    def __init__(self) -> None:
        # Connect to database
        self._connection = sqlite3.connect("clients.db")

        # Create a cursor
        self._cursor = self._connection.cursor()

        # Create a clients table
        clients_sql = """CREATE TABLE clients (
                        name TEXT,
                        ip_address TEXT,
                        udp_socket INTEGER,
                        tcp_socket INTEGER,
                        PRIMARY KEY (name)
                    )"""

        # Create a files table
        files_sql = """CREATE TABLE files (
                        client_name TEXT REFERENCES clients (name),
                        file_name TEXT,
                        PRIMARY KEY (client_name, file_name)
                    )"""
        try:
            self._cursor.execute(clients_sql)
            self._cursor.execute(files_sql)
            self._connection.commit()
        except Exception as e:
            print("The database was already created", e.args)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        print("Database connection closed")
        return self._connection.close()

    def get_all_clients(self) -> list[Client]:
        self._cursor.execute("SELECT * FROM clients")
        clients = self._cursor.fetchall()
        return clients

    def check_client_exists(self, client: Client) -> bool:
        sql = "SELECT * FROM clients WHERE name = (?)"
        self._cursor.execute(sql, (client.name,))
        if (self._cursor.fetchone()):
            return True
        else:
            return False
        # client = self._cursor.fetchone()
        # return client

    def add_client(self, client: Client) -> None:
        if (not self.check_client_exists(client)):
            self._cursor.execute("INSERT INTO clients VALUES (?, ?, ?, ?)", (
                client.name, client.ip_address, client.udp_socket, client.tcp_socket))
            self._connection.commit()
        else:
            raise Exception(
                f"The name {client.name} already exists in the database")

    def delete_client(self, client: Client) -> None:
        sql = "DELETE FROM clients WHERE name = (?)"
        self._cursor.execute(sql, (client.name,))
        self._connection.commit()

    def update_client(self, client: Client) -> None:
        sql = "UPDATE clients SET name = (?), ip_address = (?), udp_socket = (?), tcp_socket = (?) WHERE name = (?)"
        self._cursor.execute(
            sql, (client.name, client.ip_address, client.udp_socket, client.tcp_socket, client.name))
        self._connection.commit()

    # def drop_database(self):
    #     sql = "DROP DATABASE clients"
    #     self._cursor.execute(sql)
    #     self._connection.commit()


if __name__ == "__main__":
    with ClientStore() as client_store:
        client = Client('test-name', '127.0.0.1', 6080, 8080)
    # client_store = ClientStore()
    # try:
    #     client_store.add_client(client)
    # except Exception as e:
    #     print("Exception caught", e.args)
    # print(client_store.get_all_clients())
    # client_store.delete_client(client)
    # client_store.drop_database()
        client_store.update_client(client)
