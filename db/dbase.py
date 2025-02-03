import mysql.connector
from fastapi import HTTPException

# Connect to MySQL database (replace with your actual credentials)
def get_connexion():
    return mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="smart_resto"
            )
# Function to get the status based on the order_id
def get_order_status(order_id):
    try:
        conn = get_connexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM tracking_orders WHERE order_id = %s", (order_id,))

        result = cursor.fetchone()

        return  result

    except mysql.connector.Error as e:
        return f"Error while fetching data: {e}"
    
    finally:
        # Close the databaseconn
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fonction pour obtenir l'id du plat à partir de son nom
def get_food_id(food_name: str):
    conn = get_connexion()
    cursor =  conn.cursor()
    query = "SELECT food_id, price FROM foods WHERE name = %s"
    cursor.execute(query, (food_name,))
    result =  cursor.fetchone()
    print("========================")
    print(f"{result}")
    return result  # (food_id, price) ou None si pas trouvé

# Fonction pour créer la commande et gérer les relations dans les tables
def create_order(food_items: dict, session_id):
    conn = get_connexion()
    cursor = conn.cursor()

    try:
       
        # Étape 1 : Créer la commande dans la table `orders`
        total_amount = 0
        insert_order_query = """
            INSERT INTO orders (customer_id, order_date, total_amount)
            VALUES (%s, NOW(), %s)
        """
        cursor.execute(insert_order_query, (session_id, total_amount))
        conn.commit()

        # Récupérer l'ID de la commande
        order_id = cursor.lastrowid

        # Étape 2 : Insérer les éléments de commande dans la table `food_order`
        for food_name, quantity in food_items.items():
            # Vérifier si le plat existe dans la table `foods`
            food =  get_food_id(food_name)
            if food is None:
                raise HTTPException(status_code=400, detail=f"Le plat '{food_name}' n'existe pas.")
            
            food_id, price = food
            food_order_query = """
                INSERT INTO food_order (order_id, food_id, quantity)
                VALUES (%s, %s, %s)
            """
            cursor.execute(food_order_query, (order_id, food_id, quantity))

            # Ajouter au montant total de la commande
            total_amount += float(price) * int(quantity)

        # Mettre à jour le montant total de la commande dans `orders`
        update_order_query = "UPDATE orders SET total_amount = %s WHERE order_id = %s"
        cursor.execute(update_order_query, (total_amount, order_id))
        conn.commit()

        # Étape 3 : Ajouter un suivi de la commande dans la table `tracking_orders`
        tracking_query = """
            INSERT INTO tracking_orders (order_id, status, updated_at)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(tracking_query, (order_id, 'prise'))
        conn.commit()

        return order_id , total_amount

    except Exception as e:
        # Si une erreur survient, on annule les transactions

        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

    finally:
        # Fermer la connexion à la base de données
        if conn.is_connected():
            cursor.close()
            conn.close()


if __name__=="__main__":
    print(create_order({"fufu":2,"poulet":3, "mbika":4}, "4gvdvh456gdvv8726gvyvyRXC72GV72Y98GC"))
