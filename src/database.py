import sqlite3


def create_database():
    conn = sqlite3.connect("main.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            sku TEXT,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES category (id)
        )
        """
    )
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS bus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT NOT NULL UNIQUE,
                tp TEXT NOT NULL UNIQUE,
                brand TEXT NOT NULL
            )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bon_number TEXT NOT NULL UNIQUE,
            bon_date TEXT NOT NULL

        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS article_bon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_quantity TEXT,
            product_price TEXT,
            bon_id INTEGER,
            FOREIGN KEY (bon_id) REFERENCES bon (id)
        )
        """
    )
    conn.commit()
    conn.close()


def get_total_by_category(bon_number):
    conn = sqlite3.connect("main.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM category")
    categories = [row[0] for row in cursor.fetchall()]
    result = []

    for c in categories:
        cursor.execute(
            f"""
                SELECT SUM(a.product_price) AS Price
                FROM article_bon a
                JOIN product p ON a.product_name = p.name  
                JOIN category c ON p.category_id = c.id 
                WHERE a.bon_id = (SELECT id FROM bon WHERE bon_number = '{bon_number}')
                AND c.name = '{c}'
                GROUP BY c.name; 
            """
        )

        res = cursor.fetchone()
        if res:
            result.append(res[0])
        else:
            result.append(0)
    return result


def get_rapport_dactivity(bon_number):
    conn = sqlite3.connect("main.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM category")
    categories = [row[0] for row in cursor.fetchall()]
    case_statements = [
        f"SUM(CASE WHEN category.name = '{cat}' THEN CAST(article_bon.product_price AS REAL) ELSE 0 END) AS `{cat}`"
        for cat in categories
    ]
    cursor.execute(
        f"""
        SELECT
            bus.tp,
            bus.brand,
            bus.matricule,
            {', '.join(case_statements)},
            SUM(CAST(article_bon.product_price AS REAL)) AS total
        FROM
            bus
        JOIN article_bon ON bus.matricule = article_bon.bus_id
        JOIN product ON article_bon.product_name = product.name
        JOIN category ON product.category_id = category.id
        WHERE
            article_bon.bon_id = (SELECT id FROM bon WHERE bon_number = ?)
        GROUP BY
            bus.matricule;

        """,
        (bon_number,),
    )
    result = cursor.fetchall()
    return result


create_database()
