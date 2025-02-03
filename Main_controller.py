# ngrok config add-authtoken 2qST9poZanC10BOXETNk9eqstgG_4wHeZBFcV9Y6gbZwpWysX
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db.dbase as db
import helpers.helper as helper

app = FastAPI()

inprocess_orders = {}

@app.post('/')
async def handled_request(request : Request):
    payload = await request.json()
    intents = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = helper.extract_session_id(output_contexts[0]['name'])

    all_intents_dict = {
        "track.order-context : ongoing-track": track_order,
        "add.order -context : ongoing-order": add_order,
        "order.complete : ongoing-order": complete_order,
        "remove.order-context: ongoing-order": remove_order,
        "new.order": new_order
    }
    

    return await all_intents_dict[intents](parameters, session_id)
   
async def track_order(parameters: dict, session_id):
        order_id = parameters['number']
        result = db.get_order_status(order_id)
       
        if result:
            # Return the status if found
           return JSONResponse(
                content= {
                    "fulfillmentText": f"La commande numéro {int(order_id)} est : {result[0]}\n"
                                        f"=========================================================="
                                        f"Merci, de garder votre patience😊"
                }
            )
        else:
            return JSONResponse(
                    content={ 
                        "fulfillmentText" : f"La commande {int(order_id)} de la commande fourni n'a pas été trouvé"
                    }
                )
        
async def add_order(parameters: dict, session_id: str):
            
            foods = parameters['plat']
            quantities = parameters['number']

            if len(foods) != len(quantities):
                fulfillmentText = "s'il vous plait pouviez-vous spécifier la quantité des plats!"
            else:
                new_food_dict = dict(zip(foods, quantities))
                
                if session_id in inprocess_orders:
                    
                    current_food_dict = inprocess_orders[session_id]
                    current_food_dict.update(new_food_dict)
                    inprocess_orders[session_id] = current_food_dict

                else:
                    inprocess_orders[session_id] = new_food_dict
                

                order_str = helper.getFoodList(inprocess_orders[session_id])


                fulfillmentText = f"Jusqu'à présent, vous avez {order_str}. Avez-vous besoin d'autre chose (plat)?"

            return JSONResponse(content={

                "fulfillmentText": fulfillmentText
            })
          
async def complete_order(parameters: dict, session_id: str):
    if session_id in inprocess_orders:
        order_id, total_amount = db.create_order(inprocess_orders[session_id],session_id)
        if order_id:
            return JSONResponse(
                content={
                    "fulfillmentText": f"Commande placéé  avec succès!. \nVoici le numéro de votre commane 👉: {order_id}       \n"\
                                    f"Total à payer 💰💵: {total_amount} $                                                       \n"\
                                    f"Montant à payer après livraison de la commande.👩‍🍳"
                })
        
            del inprocess_orders[session_id]
        else:
            return JSONResponse(
                content={
                    "fulfillmentText": f"Désolé, vôtre commande n'a pas été enregistrer si possible d'en soumettre encore"
                }
            )
    else:
         return JSONResponse(
                content={
                    "fulfillmentText": f"Désolé, vôtre commande n'a pas été trouvée veuillez en soumettre encore."
                }
            )
    
async def remove_order(parameters: dict, session_id: str):

    if session_id in inprocess_orders:
        removed_items = []
        no_removed_items = []
        current_orders = inprocess_orders[session_id]
        removed_foods = parameters['plat']

        for item in removed_foods:
            if item in current_orders:
                removed_items.append(item)
                del current_orders[item]
            else:
                no_removed_items.append(item)
                
  
        if len(removed_items) > 0:
            fulfillmentText = f"Le(s) plat(s) ci-après : {', '.join(removed_items)} a (ont) été supprimé(s) de votre commande "

        if len(no_removed_items) > 0:
            fulfillmentText = f"le plat {' ,'.join(no_removed_items)} n'a pas été trouvé dans la commande"

        if len(current_orders.keys())==0:
            fulfillmentText += " Votre commande n'a plus des plats. Veuillez en enregistrer."
            
        else:
            orders = helper.getFoodList(current_orders)
            fulfillmentText += f" Voici le(s) plat(s) restant(s) dans votre commande : {orders}"

        return JSONResponse(content={
            "fulfillmentText": fulfillmentText
        })

    else:
        return JSONResponse(content={
            "fulfillmentText": "Ouuups, Malheureusement je n'ai pas pu trouver votre commande😓. Veuillez en soumettre une autre."
        })

async def new_order(parameters: dict, session_id: str):
        if session_id in inprocess_orders:
            if len(inprocess_orders[session_id]) > 0:
               previous_order = inprocess_orders[session_id]
               del inprocess_orders[session_id]
               fulfillmentText = f"Ce(s) plat(s) {', '.join(previous_order)} ne font plus partie de votre commande, car elle a été réinitialisée. Veuillez enregistrer une nouvelle commande 😊"
            else:
                 pass
            return JSONResponse(content={
                 "fulfillmentText": fulfillmentText
            })
        
if __name__=="__main__":
    for i , u in inprocess_orders.items():
         print(f"{i} : {u}")