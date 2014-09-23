from libs.db_models import User

def test_set_password():
    User.create("test_user")
    test_user = User('test_user')
    test_user.set_password("password")
    assert test_user.validate_password('incorrect') == False
    assert test_user.validate_password('password') == True
    test_user.remove()