from data.client_store import ClientStore
from models.client_dto import ClientDto


if __name__ == "__main__":
    with ClientStore() as client_store:
        client_dto = ClientDto('test-name', '127.0.0.1', 6080, 8080)
    # client_store = ClientStore()
    # try:
    #     client_store.add_client(client)
    # except Exception as e:
    #     print("Exception caught", e.args)
    # print(client_store.get_all_clients())
    # client_store.delete_client(client)
    # client_store.drop_database()
        client_store.update_client(client_dto)
