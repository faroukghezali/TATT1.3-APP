import sqlite3


def get_data(bon_id):
    with sqlite3.connect("main.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT product_name,product_quantity,product_price,bus_id FROM article_bon WHERE bon_id = (SELECT id FROM bon WHERE bon_number = ?)",
            (bon_id,),
        )
        result = cursor.fetchall()
        return result
