"""Apply the additive authentication migration without dropping existing data."""

from database import get_connection


def migrate():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(254) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id), UNIQUE KEY uq_users_email (email)
        ) ENGINE=InnoDB""")
        cursor.execute("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='users'")
        columns = {row[0] for row in cursor.fetchall()}
        if "password_hash" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '!disabled!'")
        if "updated_at" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
        cursor.execute("ALTER TABLE users MODIFY email VARCHAR(254) NOT NULL")
        cursor.execute("""INSERT IGNORE INTO users (id, name, email, password_hash)
            SELECT DISTINCT a.user_id, CONCAT('Legacy account ', a.user_id),
                CONCAT('legacy-', a.user_id, '@local.invalid'), '!disabled!'
            FROM activities a LEFT JOIN users u ON u.id=a.user_id WHERE u.id IS NULL""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS user_goals (
            user_id INT NOT NULL,
            goal_month CHAR(7) NOT NULL,
            target_kg DECIMAL(12,3) NOT NULL DEFAULT 100,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, goal_month)
        ) ENGINE=InnoDB""")
        cursor.execute("SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE CONSTRAINT_SCHEMA=DATABASE() AND TABLE_NAME='activities' AND COLUMN_NAME='user_id' AND REFERENCED_TABLE_NAME='users'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE activities ADD CONSTRAINT fk_activities_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE")
        cursor.execute("SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE CONSTRAINT_SCHEMA=DATABASE() AND TABLE_NAME='user_goals' AND COLUMN_NAME='user_id' AND REFERENCED_TABLE_NAME='users'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE user_goals ADD CONSTRAINT fk_goals_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE")
        # Older activity tables used DECIMAL(...,2), which silently rounded
        # the calculation engine's three-decimal CO2e values on persistence.
        # Widen scale in place; this preserves existing values and all rows.
        for table, column in (("activities", "value"), ("carbon_records", "co2e")):
            cursor.execute(
                """SELECT NUMERIC_SCALE FROM information_schema.COLUMNS
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s""",
                (table, column),
            )
            column_info = cursor.fetchone()
            if column_info and int(column_info[0] or 0) < 3:
                cursor.execute(f"ALTER TABLE `{table}` MODIFY `{column}` DECIMAL(12,3) NOT NULL")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    migrate()
    print("Authentication schema migration completed.")
