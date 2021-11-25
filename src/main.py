from data.client_store import ClientStore
from data.store import StoreException
from models.client_dto import ClientDto
from models.file_dto import FileDto


if __name__ == "__main__":
    try:
        with ClientStore() as client_store:
            # client_store.create_tables()
            client = ClientDto('test-user-2', '127.0.0.13', 1111, 4321)

            files = ["file_a.txt", "file_b.txt", "file_c.txt"]
            files2 = ["file_d.txt", "file_e.txt", "file_f.txt"]
            fileDto = FileDto("test-user-2", files2)
            # client_store.add_client(client)
            # client_store.update_client(client)
            # client_store.delete_client(client)
            # client_store.publish_files(fileDto)
            # client_store.remove_files(fileDto)
            print(client_store.retrieve_all())
            # print(client_store.retrieve_info("test-user"))
            client_store.complete()

    except StoreException as e:
        print(e, e.errors)
