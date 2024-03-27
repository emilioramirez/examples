import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pywebpush import webpush, WebPushException

app = FastAPI()

directory = os.path.join(os.path.dirname(__file__))
app.mount("/static", StaticFiles(directory=directory), name="static")


# Claves de suscripción (solo para propósitos de demostración, en un caso real, estas claves serían almacenadas de forma segura)
VAPID_PUBLIC_KEY = "BH6KPku1zV97v5o8LXIXmejDpcIqlH9HDwX8Qre5ktweG2oMCdBcINyT_DufO1TNRAtQRkCfdPFrAvfIH4SsBXY"
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "you_must_define_this")


@app.get("/")
async def get_index():
    with open("frontend_app.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/save-subscription/")
async def save_subscription(subscription: dict):
    # el subcription es lo que deberiamos guardar asociado al user:browser para poder mandarle notificaciones push
    # subcription = {
    #      'endpoint': 'https://updates.push.services.mozilla.com/wpush/v2/gAAAAABmAwzNKibL8Mu0bz4uJOEb002qDf4LJsmNN3FXZoK_eivd9vWECzvdL0H9BMWEvEOESPPkpyJ1NK9nzqdP__x0bQlymv6G9e08UfIjXpf6t9r-2A1RIhHOArCJXrXUAZ4ZiqWZCUsIsSnRvQJccT30mkezMqw2n6Kk8Bww_YkJcrcUB20',
    #      'expirationTime': None,
    #      'keys': {'auth': 'cwPaJu5g1FRv4ybg9OTOHQ', 'p256dh': 'BOjQ6bQX13paDaJa_Dyt-sOkpCOz25nwTJ9TJNQkuQKScjdu7OS-75_nWMLSCzzpdLljVaZvyDb14wv5Gza6FdM'}}
    with open("subscription.json", "w") as file:
        json.dump(subscription, file)

    return JSONResponse(content={"message": "Subscripcion success"}, status_code=200)


@app.post("/send-notification/")
async def send_notification(message: dict):
    # Levantamos la data de la subscription que guardamos previamente
    try:
        with open("subscription.json", "r") as file:
            subscription = json.load(file)
    except:
        return JSONResponse(content={"message": "User not subscribed"}, status_code=400)

    try:
        webpush(
            subscription_info=subscription["subscription"],
            data=json.dumps(message["message"]),  # Tener cuidado, esto debe ser un json valido no un dict pelado
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": "mailto:tu_correo@example.com",
                # "aud": "http://example.com"
            }
        )
    except WebPushException as e:
        # raise e
        return JSONResponse(content={"message": "Notification fail: " + str(e)}, status_code=400)
        

    return JSONResponse(content={"message": "Notification success"})
