from security.security_utils import SecurityUtils

security_utils = SecurityUtils("your-secret-key")

password1 = "123321"  # stuff
password2 = "123456"  # admin

hashed_password_1 = security_utils.hash_password(password1)
hashed_password_2 = security_utils.hash_password(password2)

print(f"Hashed password: {hashed_password_1}")

print(f"Hashed password: {hashed_password_2}")