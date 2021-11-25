from data.client_store import ClientStore
from data.store import StoreException
from models.client_dto import ClientDto


if __name__ == "__main__":
    try:
        with ClientStore() as client_store:
            # client_store.create_tables()
            client = ClientDto('test-user-2', '127.0.0.13', 1111, 4321)
            files = ["file_a.txt", "file_b.txt", "file_c.txt"]
            # client_store.add_client(client)
            # print(client_store.get_all_clients())
            # client_store.update_client(client)
            # client_store.delete_client(client)
            client_store.add_files("test-user", files)
            print(client_store.get_all_clients())
            # print(client_store.get_all_files())
            client_store.complete()

    except StoreException as e:
        print(e, e.errors)
