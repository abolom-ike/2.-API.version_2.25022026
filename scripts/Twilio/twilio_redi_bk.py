from flask import Flask, Response, request
from twilio.twiml.voice_response import VoiceResponse, Dial, Pause
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# numero_principal = "+525619915654"
# numero_principal = "+5554800970"  # Número Iké
# extension = "ww600543#"
# caller_id = "+525597635998"  # Número Twilio

# @app.route("/transfer", methods=["POST", "GET"])
# def transfer():
#     response = VoiceResponse()
#     # dial = Dial()
#     dial = Dial(callerId=caller_id)
#     # dial.number(numero_principal)# un solo número
#     dial.number(numero_principal, send_digits=extension) # número con extensión
#     response.say("Transfiriendo su llamada ahora, por favor espere")
#     response.append(dial)
#     logging.info("TwiML que envío: %s", str(response))
#     return Response(str(response), mimetype="application/xml")


@app.route("/transfer", methods=["POST", "GET"])
def transfer():
    """
    Endpoint que recibe la llamada de VAPI y transfiere
    automáticamente a un número PBX con extensión.
    Parámetros:
        - numero: número PBX destino (con prefijo +)
        - extension: extensión a marcar
        - caller_id: tu número Twilio
    """
    # Primero, obtenemos los parámetros dinámicos
    if request.method == "POST":
        data = request.json or {}
        numero_principal = data.get("numero") or "+5554800970"
        extension = data.get("extension") or "600543"
        caller_id = data.get("caller_id") or "+525597635998"
    else:
        numero_principal = request.args.get("numero", "+5554800970")
        extension = request.args.get("extension", "600543")
        caller_id = request.args.get("caller_id", "+525597635998")

    # Generamos el TwiML para la transferencia
    response = VoiceResponse()
    response.say("Transfiriendo su llamada ahora, por favor espere")

    dial = Dial(callerId=caller_id)
    dial.number(numero_principal, send_digits=f"ww{extension}#")
    response.append(dial)

    # Log para debugging en Azure
    logging.info("TwiML generado para transferencia:")
    logging.info(str(response))

    return Response(str(response), mimetype="application/xml")

@app.route("/join_conference", methods=["POST", "GET"])
def join_conference():
    response = VoiceResponse()
    dial = Dial()
    dial.conference(
        "VapiPBXConference",
        start_conference_on_enter=True,   # inicia conferencia al entrar
        end_conference_on_exit=False      # no corta la conferencia si alguien sale
    )
    response.append(dial)
    return Response(str(response), mimetype="application/xml")


@app.route("/")
def index():
    return "API de transferencia activa. Endpoint: /join_conference"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)