import psycopg2


class Database:
    def __init__(self, host="localhost", database="hrms", user="openpg", password="openpgpwd"):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def connect(self):
        """Create and return a new database connection."""
        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def initialize(self):
        """Initialize tables and default roles."""
        with self.connect() as conn:
            with conn.cursor() as cur:
                self._create_tables(cur)
                self._initialize_roles(cur)
                self._initialize_admin(cur)
            conn.commit()

    def _create_tables(self, cur):
        """Create necessary tables if they don't exist."""
        cur.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE
            );
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                full_name TEXT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password TEXT,
                industry TEXT,
                role_id INTEGER REFERENCES roles(id),
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        cur.execute('''
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='registered_at'
                ) THEN
                    ALTER TABLE users ADD COLUMN registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                END IF;
            END $$;
        ''')
    

    def _initialize_roles(self, cur):
        """Initialize default roles."""
        roles = ["Admin", "HR", "User"]
        for role in roles:
            cur.execute(
                'INSERT INTO roles (name) VALUES (%s) ON CONFLICT (name) DO NOTHING',
                (role,)
            )

    def _initialize_admin(self, cur):
        """Create a default Admin account if it doesn't exist."""
        cur.execute('SELECT id FROM roles WHERE name = %s', ("Admin",))
        admin_role_id = cur.fetchone()[0]
        cur.execute(
            '''
            INSERT INTO users (full_name, username, email, password, industry, role_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
            ''',
            ("Super Admin", "admin", "admin@example.com", self._hash_password("admin123"), "Administration", admin_role_id)
        )

    @staticmethod
    def _hash_password(password):
        """Helper function to hash passwords."""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
