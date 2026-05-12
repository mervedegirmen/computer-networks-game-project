import json  # Python sözlüklerini JSON metnine, JSON metinlerini de tekrar Python sözlüklerine çevirmek için kullanılır.


ASSIGN_PLAYER = "assign_player"  # Server'ın client'a oyuncu numarası atadığını belirten mesaj tipidir.
WAITING = "waiting"  # Bir oyuncu bağlandığında diğer oyuncunun beklenmesini belirten mesaj tipidir.
GAME_START = "game_start"  # İki oyuncu bağlandığında veya oyun yeniden başladığında gönderilen mesaj tipidir.
ROLL_DICE = "roll_dice"  # Client'ın server'dan zar atma işlemi istemesini belirten mesaj tipidir.
GAME_STATE = "game_state"  # Server'ın güncel oyun durumunu client'lara göndermesini belirten mesaj tipidir.
GAME_OVER = "game_over"  # Oyunun bittiğini ve kazananın belirlendiğini belirten mesaj tipidir.
ERROR = "error"  # Hatalı durumlarda server'ın client'a hata mesajı göndermesi için kullanılan mesaj tipidir.
RESTART_REQUEST = "restart_request"  # Client'ın oyunu yeniden başlatmak istediğini server'a bildiren mesaj tipidir.
OPPONENT_LEFT = "opponent_left"  # Rakip oyuncunun bağlantıdan ayrıldığını bildiren mesaj tipidir.
RESTART_WAITING = "restart_waiting"  # Bir oyuncu tekrar oynamak istediğinde diğer oyuncunun onayının beklendiğini belirten mesaj tipidir.


def encode_message(data: dict) -> bytes:  # Python sözlüğü şeklindeki mesajı socket ile gönderilecek byte verisine çevirir.
    message = json.dumps(data)  # Python sözlüğünü JSON formatında string'e dönüştürür.
    return (message + "\n").encode("utf-8")  # Mesaj sonuna satır sonu ekler ve UTF-8 byte formatına çevirir.


def decode_message(message: str) -> dict:  # Socket'ten gelen JSON string mesajı Python sözlüğüne çevirir.
    return json.loads(message)  # JSON formatındaki string'i Python dict veri tipine dönüştürür.