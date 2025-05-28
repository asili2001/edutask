from src.controllers.controller import Controller
from src.util.dao import DAO

import re
pattern = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
email_validator = re.compile(pattern)

class UserController(Controller):
    def __init__(self, dao: DAO):
        super().__init__(dao=dao)

    def get_user_by_email(self, email: str):
        """Given a valid email address of an existing account, return the user object contained in the database associated 
        to that user. For now, do not assume that the email attribute is unique. Additionally print a warning message containing the email
        address if the search returns multiple users.
        
        parameters:
            email -- an email address string 

        returns:
            user -- the user object associated to that email address (if multiple users are associated to that email: return the first one)
            None -- if no user is associated to that email address

        raises:
            ValueError -- in case the email parameter is not valid (i.e., conforming <local-part>@<domain>.<host>)
            Exception -- in case any database operation fails
        """

        if not re.fullmatch(email_validator, email):
            raise ValueError('Error: invalid email address')

        try:
            users = self.dao.find({'email': email})
            if len(users) == 0:
                print(f'Warning: no user found with mail {email}')
                return None
            return users[0]
        except Exception as e:
            raise

    def update(self, id, data):
        try:
            update_result = super().update(id=id, data={'$set': data})
            return update_result
        except Exception as e:
            raise