from utils.functions import get_env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_env("MYSQL_NAME"),
        'USER': get_env("MYSQL_USERNAME"),
        'PASSWORD': get_env("MYSQL_PASSWORD"),
        'HOST': '127.0.0.1',
        'POST': 3306,
    }
}
