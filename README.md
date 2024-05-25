```
config = {
    "username": "<USERNAME>",
    "totp_key": "<TOTP_KEY>",
    "pin": "<PIN>",
    "client_id": "<CLIENT_ID>",
    "secret_key": "<SECRET_KEY>",
    "redirect_uri": "<REDIRECT_URL>",
}
```

## Install

```
pip install fyers-token-manager-3
```

## Fyers Token Generator

```
from fyers_token_manager_3 import FyersTokenManager

fyersTokenManager = FyersTokenManager(
    username=config["username"],
    totp_key=config["totp_key"],
    pin=config["pin"],
    client_id=config["client_id"],
    secret_key=config["secret_key"],
    redirect_url=config["redirect_url"],
)

print(fyersTokenManager.http_access_token)
print(fyersTokenManager.ws_access_token)
```

#### HTTP Client

- fyersTokenManager.http_client.get_profile()

#### WebSocket Client

- fyersTokenManager.ws_client.subscribe(payload)
