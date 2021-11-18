import sqlite3


def get_connection():
    """Return an open connection to the SQLite database."""
    return sqlite3.connect('clients.db')


class StoreException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors


class Store():
    def __init__(self):
        try:
            self.connection = get_connection()
        except Exception as e:
            raise StoreException(*e.args, **e.kwargs)
        self._complete = False

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def close(self):
        if self.connection:
            try:
                if self._complete:
                    self.connection.commit()
                else:
                    self.connection.rollback()
            except Exception as e:
                raise StoreException(*e.args)
            finally:
                try:
                    self.connection.close()
                except Exception as e:
                    raise StoreException(*e.args)
