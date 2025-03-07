import hashlib
import psycopg2
from psycopg2 import errors
from db import Database


class AuthService:
    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def hash_password(password):
        """Hash the password for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, full_name, username, email, password, industry, role_name="User"):
        """Register a new user."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT id FROM roles WHERE name = %s', (role_name,))
                role = cur.fetchone()
                if not role:
                    raise ValueError(f"Role '{role_name}' not found. Ensure roles are initialized.")

                hashed_password = self.hash_password(password)

                try:
                    cur.execute(
                        '''
                        INSERT INTO users (full_name, username, email, password, industry, role_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ''',
                        (full_name, username, email, hashed_password, industry, role[0])
                    )
                    conn.commit()
                except errors.UniqueViolation as e:
                    conn.rollback()
                    if "users_username_key" in str(e):
                        raise ValueError("The username is already taken. Please choose another.")
                    if "users_email_key" in str(e):
                        raise ValueError("The email is already registered. Please use a different email.")
                    raise e

    def update_user(self, account_id, full_name, email, password=None, industry=None):
        """Update user details by their ID."""
        allowed_industries = ["Software", "Finance", "Healthcare", "Education"]
    
        if not self.is_valid_email(email):
            raise ValueError("Invalid email format.")
    
        if industry and industry not in allowed_industries:
            raise ValueError("Invalid industry value.")
    
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                update_fields = []
                update_values = []
    
                if full_name:
                    update_fields.append("full_name = %s")
                    update_values.append(full_name)
                if email:
                    update_fields.append("email = %s")
                    update_values.append(email)
                if password:
                    update_fields.append("password = %s")
                    update_values.append(self.hash_password(password))
                if industry is not None:
                    update_fields.append("industry = %s")
                    update_values.append(industry)
    
                update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
                update_values.append(account_id)
    
                cur.execute(update_query, tuple(update_values))
    
                if cur.rowcount == 0:
                    raise ValueError("User not found or no changes detected.")
    
                conn.commit()
    
    def get_hr_details(self, hr_id):
        """Retrieve HR details by ID."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    SELECT full_name, email
                    FROM users
                    WHERE id = %s
                    ''',
                    (hr_id,)
                )
                row = cur.fetchone()
                if row:
                    return {"full_name": row[0], "email": row[1]}
                else:
                    raise ValueError("HR details not found.")

    def get_user_id(self, username):
        """Retrieve the user ID based on the username."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                result = cur.fetchone()
                if result:
                    return result[0]
                else:
                    raise ValueError(f"No user found with username: {username}")
    
    def authenticate_user(self, identifier, password):
        """Authenticate a user using either username or email."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                hashed_password = self.hash_password(password)
                cur.execute(
                    '''
                    SELECT users.id, users.full_name, users.username, users.email, roles.name AS role
                    FROM users
                    INNER JOIN roles ON users.role_id = roles.id
                    WHERE (users.username = %s OR users.email = %s) AND users.password = %s
                    ''',
                    (identifier, identifier, hashed_password)
                )
                return cur.fetchone()
    
    def check_username_exists(self, username):
        """Check if a username already exists in the database."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username FROM users WHERE username = %s", (username,))
                return cur.fetchone() is not None

    def check_email_exists(self, email):
        """Check if an email already exists in the database."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT email FROM users WHERE email = %s", (email,))
                return cur.fetchone() is not None

    def get_all_hr_accounts(self):
        """Retrieve all HR accounts ordered by registration date (newest first)."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    SELECT users.id AS user_id, users.full_name, users.username, users.email, users.registered_at
                    FROM users
                    INNER JOIN roles ON users.role_id = roles.id
                    WHERE roles.name = 'HR'
                    ORDER BY users.registered_at DESC
                    '''
                )
                return cur.fetchall()

    def get_all_user_accounts(self):
        """Retrieve all User accounts including industry and registration date, ordered by registration date (newest first)."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    SELECT users.id AS user_id, users.full_name, users.username, users.email, users.industry, users.registered_at
                    FROM users
                    INNER JOIN roles ON users.role_id = roles.id
                    WHERE roles.name = 'User'
                    ORDER BY users.registered_at DESC
                    '''
                )
                return cur.fetchall()

    def delete_user(self, user_id):
        """Delete a user by their ID."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
  
    @staticmethod
    def is_valid_email(email):
        """Validate email format."""
        import re
        email_regex = (
            r"^(?!\.)"
            r"[a-zA-Z0-9_.+-]+"
            r"(?<!\.)@"
            r"[a-zA-Z0-9-]+"
            r"(\.[a-zA-Z]{2,})+$"
        )
        return bool(re.match(email_regex, email)) and ".." not in email

    @staticmethod
    def is_valid_password(password):
        """Validate password strength."""
        import re
        if len(password) < 8:
            return False
        if not re.search(r"[a-zA-Z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[@$!%*?&#]", password):
            return False
        return True