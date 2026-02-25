# end_call_vapi.py
import time
import requests

try:
    from twilio.rest import Client as TwilioClient
    _HAS_TWILIO = True
except Exception:
    _HAS_TWILIO = False

VAPI_API_BASE = "https://api.vapi.ai"


def get_vapi_call(call_id: str, vapi_api_key: str, timeout=10):
    """Obtiene el objeto 'call' desde Vapi (/call/:id)."""
    url = f"{VAPI_API_BASE}/call/{call_id}"
    headers = {"Authorization": f"Bearer {vapi_api_key}"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()


def end_call_vapi_control_url(control_url: str, timeout=6, retries=2, backoff=0.5):
    """
    Envía POST { "type": "end-call" } al controlUrl de Vapi (Live Call Control).
    Devuelve dict con éxito y respuesta.
    """
    payload = {"type": "end-call"}
    headers = {"Content-Type": "application/json"}
    last_exc = None
    for attempt in range(retries + 1):
        try:
            r = requests.post(control_url, json=payload, headers=headers, timeout=timeout)
            # 2xx suele ser OK; la doc usa 200/204 en ejemplos.
            return {"ok vapi terminó la llamada": r.ok, "status_code": r.status_code, "text": (r.text or "")}
        except Exception as e:
            last_exc = e
            time.sleep(backoff * (2 ** attempt))
    return {"ok": False, "error": str(last_exc)}


def end_call_twilio(account_sid: str, auth_token: str, call_sid: str, use_sdk_first=True):
    """
    Fallback: forzar a Twilio a terminar la llamada (status=completed).
    Intenta con Twilio SDK si está instalado, si no usa requests con Basic Auth.
    """
    # 1) SDK attempt
    if use_sdk_first and _HAS_TWILIO:
        try:
            client = TwilioClient(account_sid, auth_token)
            call = client.calls(call_sid).update(status="completed")
            return {"ok": True, "via": "twilio-sdk", "sid": getattr(call, "sid", call_sid)}
        except Exception as e:
            # SDK fallo -> intentar REST directo
            sdk_err = str(e)
    else:
        sdk_err = None

    # 2) REST fallback
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls/{call_sid}.json"
    try:
        r = requests.post(url, auth=(account_sid, auth_token), data={"Status": "completed"}, timeout=8)
        return {"ok": r.ok, "via": "twilio-rest", "status_code": r.status_code, "text": (r.text or ""), "sdk_err": sdk_err}
    except Exception as e:
        return {"ok": False, "error": str(e), "sdk_err": sdk_err}


def end_call_with_fallback(call_id: str,
                           vapi_api_key: str = None,
                           twilio_account_sid: str = None,
                           twilio_auth_token: str = None,
                           prefer_vapi_first=True):
    """
    Flujo recomendado:
     1) Obtener call object desde Vapi
     2) Si existe monitor.controlUrl -> POST end-call (Vapi Live Call Control)
     3) Si no funciona y proveedor es twilio y tienes credenciales -> actualizar Twilio (status=completed)
    Devuelve dict con resultado y diagnósticos.
    """
    result = {"call_id": call_id, "steps": []}

    if not vapi_api_key:
        return {"ok": False, "error": "Se requiere vapi_api_key para leer el call y controlUrl."}

    # 1) obtener call object
    try:
        call_obj = get_vapi_call(call_id, vapi_api_key)
    except Exception as e:
        return {"ok": False, "error": f"Error obteniendo call desde Vapi: {e}"}

    result["call_object"] = call_obj
    monitor = call_obj.get("monitor", {}) or {}
    control_url = monitor.get("controlUrl")
    provider = call_obj.get("phoneCallProvider")
    provider_call_id = call_obj.get("phoneCallProviderId") or (call_obj.get("transport") or {}).get("callSid")

    # 2) intentar Vapi Live Call Control
    if control_url:
        ctrl_res = end_call_vapi_control_url(control_url)
        result["steps"].append({"method": "vapi_control_url", "control_url": control_url, "result": ctrl_res})
        if ctrl_res.get("ok"):
            result["ok"] = True
            return result
        # si falla, seguimos a fallback
    else:
        result["steps"].append({"method": "vapi_control_url", "result": "no controlUrl available"})

    # 3) fallback Twilio (si provider es twilio o tenemos provider_call_id y credenciales)
    if provider == "twilio" or (provider_call_id is not None):
        if twilio_account_sid and twilio_auth_token and provider_call_id:
            tw_res = end_call_twilio(twilio_account_sid, twilio_auth_token, provider_call_id)
            result["steps"].append({"method": "twilio_update_call", "call_sid": provider_call_id, "result": tw_res})
            if tw_res.get("ok"):
                result["ok"] = True
                return result
        else:
            result["steps"].append({"method": "twilio_update_call", "result": "missing twilio credentials or call_sid", "call_sid": provider_call_id})
    else:
        result["steps"].append({"method": "twilio_update_call", "result": f"not applicable (provider={provider})"})

    # 4) si llegamos aquí, no pudimos terminar la llamada
    result["ok"] = False
    return result


if __name__ == "__main__":
    account_sid = "019a1230-e990-7dd0-928a-4ef5c55e1149"
    auth_token = "aac22b3ca5030ccc982aa4d5f7e553dc"
    api_key= "bc2041b5-6464-4c37-b936-6fffcfa0c158"
    out = end_call_with_fallback("0199c58a-b917-7ccb-9a8e-a58a094df122", vapi_api_key=api_key,
                                twilio_account_sid=account_sid, twilio_auth_token=auth_token)
    print(out)
    
    pass