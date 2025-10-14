from flask import Flask, Response
from twilio.twiml.voice_response import VoiceResponse, Dial

app = Flask(__name__)

@app.route("/transfer", methods=["POST", "GET"])
def transfer():
    # numero_principal = "+525554800970"  # Número que pide extensión
    # extension = "600543#"                 # Extensión que quieres marcar

    numero_principal = "+525644191365"  # Número que pide extensión

    response = VoiceResponse()
    # dial = Dial()
    response.say("Transfiriendo su llamada ahora, por favor espere")
    response.dial(numero_principal)
    # dial.number(numero_principal, send_digits=extension)
    # response.append(dial)

    print("TwiML que envío:", str(response))
    return Response(str(response), mimetype="application/xml")


# if __name__ == "__main__":
#     app.run(port=5001, debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)


