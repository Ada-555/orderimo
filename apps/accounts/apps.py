from django.contrib.auth.apps import AuthConfig

class AccountsConfig(AuthConfig):
    name = "apps.accounts"
    default_auto_field = "django.db.models.BigAutoField"
