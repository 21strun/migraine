INSTALLED_APPS = ['polls']
SECRET_KEY = 'foo'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testapp.sqlite'
    }
}
