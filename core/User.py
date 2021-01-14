class User():
    def __init__(self, driver):
        self.__driver = driver
        self.__user_id = None
        self.__user_name = None

    def from_db(self, user_id):
        data = users_rec = self.__driver.user_rd(user_id)
        self.__user_id = user_id
        self.__user_name = data[1]

    def get_name(self):
        return self.__user_name

    def get_id(self):
        return self.__user_id
