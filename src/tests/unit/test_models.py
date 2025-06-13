
from models.users import SimpleUser


def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, and role fields are defined correctly
    """
    user = SimpleUser('patkennedy79@gmail.com', 'FlaskIsAwesome', 'user')
    assert user.email == 'patkennedy79@gmail.com'
    assert user.password == 'FlaskIsAwesome'
    assert user.role == 'user'
