# Zar atmak için rastgele sayı üretmemiz gerekiyor.
import random

# Ortak sabitleri common klasöründen alıyoruz.
# FINAL_SQUARE: son hedef kare
# SNAKES: yılanların baş ve kuyruk eşleşmeleri
# LADDERS: merdivenlerin alt ve üst eşleşmeleri
from common.constants import FINAL_SQUARE, SNAKES, LADDERS


# Bu sınıf Yılanlar ve Merdivenler oyununun tüm kurallarını yönetecek.
class GameLogic:
    # Sınıf oluşturulduğunda ilk çalışan fonksiyon.
    def __init__(self):
        # Oyun ilk başta sıfırdan başlasın diye reset_game çağırıyoruz.
        self.reset_game()

    # Oyunu ilk haline döndüren fonksiyon.
    def reset_game(self):
        # Oyuncu 1 ve oyuncu 2'nin başlangıç pozisyonlarını 0 yapıyoruz.
        self.player_positions = {
            1: 0,
            2: 0
        }

        # Oyuna ilk olarak oyuncu 1 başlasın.
        self.current_turn = 1

        # Oyun başlangıçta bitmiş değil.
        self.game_over = False

        # Başlangıçta kazanan yok.
        self.winner = None

        # Henüz zar atılmadı.
        self.last_roll = None

        # Son olay mesajı; istemcilere bilgi vermek için tutuyoruz.
        self.last_message = "Game started. Player 1 begins."

    # Bu fonksiyon oyuncunun zar atma isteğini işler.
    def roll_for_player(self, player_id):
        # Eğer oyun bittiyse artık zar atılamaz.
        if self.game_over:
            return {
                "success": False,
                "message": "Game is already over."
            }

        # Eğer zar atmak isteyen oyuncu, sırası gelen oyuncu değilse reddediyoruz.
        if player_id != self.current_turn:
            return {
                "success": False,
                "message": f"It is not Player {player_id}'s turn."
            }

        # 1 ile 6 arasında rastgele zar değeri üretiyoruz.
        dice_value = random.randint(1, 6)

        # Son atılan zarı saklıyoruz.
        self.last_roll = dice_value

        # Oyuncuyu zar kadar ilerletiyoruz.
        move_message = self.move_player(player_id, dice_value)

        # Eğer oyun bitmediyse sırayı diğer oyuncuya geçiriyoruz.
        if not self.game_over:
            self.switch_turn()

        # Başarılı sonucu sözlük şeklinde döndürüyoruz.
        return {
            "success": True,
            "dice": dice_value,
            "message": move_message
        }

    # Bu fonksiyon oyuncunun taşını hareket ettirir.
    def move_player(self, player_id, steps):
        # Oyuncunun mevcut konumunu alıyoruz.
        current_position = self.player_positions[player_id]

        # Yeni gitmek istediği kareyi hesaplıyoruz.
        new_position = current_position + steps

        # Eğer oyuncu son kareyi aşarsa hareket etmiyor.
        if new_position > FINAL_SQUARE:
            # Açıklama mesajını güncelliyoruz.
            self.last_message = (
                f"Player {player_id} rolled {steps}, "
                f"but needs exact number to reach {FINAL_SQUARE}."
            )

            # Hareket olmadı, mesajı geri dönüyoruz.
            return self.last_message

        # Oyuncuyu yeni kareye taşıyoruz.
        self.player_positions[player_id] = new_position

        # İlk hareket mesajını hazırlıyoruz.
        message = f"Player {player_id} rolled {steps} and moved to square {new_position}."

        # Oyuncu yılan veya merdivene denk geldiyse kontrol ediyoruz.
        final_position, extra_message = self.apply_snake_or_ladder(new_position)

        # Eğer pozisyon değiştiyse son konumu güncelliyoruz.
        self.player_positions[player_id] = final_position

        # Eğer ekstra mesaj varsa ana mesajın sonuna ekliyoruz.
        if extra_message != "":
            message += " " + extra_message

        # Eğer oyuncu son kareye ulaştıysa oyun biter.
        if final_position == FINAL_SQUARE:
            self.game_over = True
            self.winner = player_id
            message += f" Player {player_id} wins the game!"

        # Son mesajı saklıyoruz.
        self.last_message = message

        # Mesajı geri döndürüyoruz.
        return message

    # Bu fonksiyon oyuncunun geldiği karede yılan veya merdiven var mı diye bakar.
    def apply_snake_or_ladder(self, position):
        # Eğer oyuncu bir yılanın başına geldiyse aşağı iner.
        if position in SNAKES:
            # Yılanın götürdüğü yeni kareyi alıyoruz.
            new_position = SNAKES[position]

            # Bilgilendirme mesajı hazırlıyoruz.
            message = f"Player landed on a snake and moved down to square {new_position}."

            # Yeni pozisyonu ve mesajı döndürüyoruz.
            return new_position, message

        # Eğer oyuncu bir merdivenin altına geldiyse yukarı çıkar.
        if position in LADDERS:
            # Merdivenin çıkardığı yeni kareyi alıyoruz.
            new_position = LADDERS[position]

            # Bilgilendirme mesajı hazırlıyoruz.
            message = f"Player climbed a ladder and moved up to square {new_position}."

            # Yeni pozisyonu ve mesajı döndürüyoruz.
            return new_position, message

        # Yılan veya merdiven yoksa aynı pozisyonu döndür.
        return position, ""

    # Bu fonksiyon sırasını diğer oyuncuya geçirir.
    def switch_turn(self):
        # Eğer sıra 1'deyse 2'ye, 2'deyse 1'e geçiyoruz.
        if self.current_turn == 1:
            self.current_turn = 2
        else:
            self.current_turn = 1

    # Bu fonksiyon istemcilere gönderilecek güncel oyun durumunu döndürür.
    def get_state(self):
        return {
            "player_positions": self.player_positions,
            "current_turn": self.current_turn,
            "game_over": self.game_over,
            "winner": self.winner,
            "last_roll": self.last_roll,
            "last_message": self.last_message
        }