# coding: utf-8

from .db.db_manager import DBManager
from .db.db_exception import (
    DBUserNotFound
)
from user_api_exception import (
    ApiConflict,
    ApiNotFound,
    ApiUnauthorized,
    ApiUnprocessableEntity
)
from .auth.auth_manager import AuthManager
from .adapter.flask_adapter import FlaskAdapter


class UserApi(object):

    def __init__(
        self,
        db_manager,
        authentication
    ):
        """
        Build the user API
        Args:
            db_manager (DBManager): Injected object to handle DB interaction.
            authentication (AuthManager): Injected object to handle Auth interactions.
        """
        self._db_manager = db_manager
        self._authentication = authentication

    def get_flask_adapter(self):
        """
        Get an adapter for the API.

        Returns:
            (FlaskAdapter): The adapter.
        """
        return FlaskAdapter(self)

    def update(self, payload, user_id):
        """
        Update a user.
        Args:
            payload (dict): The user to update.
            user_id (int): The ID of the user to update.

        Returns:
            (dict): The updated user.
        """
        user = self._db_manager.get_user_information(user_id)
        if user is None:
            raise ApiNotFound(u"User not found.")

        return user

    def authenticate(self, email, password):
        """
        Authenticate a user.
        Args:
            email (unicode): The user email.
            password (unicode): The user password.

        Returns:
            (dict): The user auth information.
        """
        try:
            salt = self._db_manager.get_user_salt(email=email)
        except DBUserNotFound:
            raise ApiNotFound(u"Can't find user {}.".format(email))

        hash = self._authentication.generate_hash(
            password,
            salt
        )
        valid = self._db_manager.is_user_hash_valid(
            email,
            hash=hash
        )
        if not valid:
            raise ApiUnauthorized(u"Wrong login or / and password.")

        payload = self._db_manager.get_user_information(email)
        token = self._authentication.generate_token(payload)
        return payload, token

    def reset_password(self, email, password):
        """
        Reset a user password.
        Args:
            email (unicode): The user email.
            password (unicode): The user new password.

        Returns:
            (dict): The user auth new information.
        """
        salt = self._authentication.generate_salt()
        hash = self._authentication.generate_hash(password, salt)

        self._db_manager.modify_hash_salt(email, hash, salt)
        payload = self._db_manager.get_user_information(email)

        if payload is None:
            raise ApiUnprocessableEntity(u"User '{}' doesn't exist.".format(email))

        return payload

    def register(self, email, name, password):
        """
        Register a new user.
        Args:
            email (unicode): The user email.
            name (unicode): The user name.
            password (unicode): The user password.

        Returns:
            (dict): The user auth new information.
        """
        salt = self._authentication.generate_salt()
        hash = self._authentication.generate_hash(password, salt)
        try:
            user = self._db_manager.save_new_user(
                email=email,
                name=name,
                hash=hash,
                salt=salt
            )
            return user
        except ValueError:
            raise ApiConflict(u"User already exists.")

    def get_token_data(self, token):
        """
        Decrypt token and return payload.
        Args:
            token (unicode): The JWT token.

        Returns:
            (dict): The payload contained in the token.
        """
        return self._authentication.get_token_data(token)

    def is_token_valid(self, token):
        """
        Check if a token is valid.
        Args:
            token (unicode): The token value.

        Returns:
            (boolean): Return True if valid, else False.
        """
        return self._authentication.is_token_valid(token)

    def list_users(self, limit=20, offset=0, email=None, name=None):
        """
        List the users from the API.
        Args:
            limit (int): The max number of returned users.
            offset (int): The cursor.
            email (unicode): An email to filter on.
            name (unicode): A name to filter on.

        Returns:
            (list of dict, boolean): A list of user representations. The boolean stands for if there is more to fetch.
        """
        users, has_next = self._db_manager.list_users(limit, offset, email, name)
        return {
            u"users": users,
            u"has_next": has_next
        }
