from libs.db_models import User, Admin

def test_set_password_user():
    User.create("test_user")
    test_user = User('test_user')
    test_user.set_password("password")
    assert test_user.validate_password('incorrect') == False
    assert test_user.validate_password('password') == True
    test_user.remove()
    
def test_set_password_admin():
    Admin.create('test_admin', 'password')
    assert Admin.check_password('test_admin', 'something_wrong') == False
    assert Admin.check_password('test_admin', 'password') == True
    Admin('test_admin').remove()