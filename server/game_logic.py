import random  # Zar değeri üretmek için random modülünü içe aktarır.

from common.constants import FINAL_SQUARE, SNAKES, LADDERS, PLAYER_1, PLAYER_2  # Oyun sabitlerini, yılan/merdiven bilgilerini ve oyuncu numaralarını içe aktarır.


class GameLogic:  # Yılanlar ve Merdivenler oyununun server tarafındaki oyun mantığını yöneten sınıftır.
    def __init__(self):  # GameLogic nesnesi oluşturulduğunda çalışan kurucu metottur.
        self.reset_game()  # Oyunu başlangıç durumuna getirir.

    def reset_game(self):  # Oyunu sıfırlayan ve başlangıç değerlerini yeniden ayarlayan metottur.
        self.player_positions = {  # Oyuncuların tahta üzerindeki pozisyonlarını tutar.
            PLAYER_1: 0,  # 1. oyuncunun başlangıç pozisyonunu 0 yapar.
            PLAYER_2: 0,  # 2. oyuncunun başlangıç pozisyonunu 0 yapar.
        }

        self.extra_turn_used = {  # Oyuncuların 6 atınca verilen ekstra hakkı kullanıp kullanmadığını tutar.
            PLAYER_1: False,  # 1. oyuncunun ekstra hakkını başlangıçta kullanılmamış yapar.
            PLAYER_2: False,  # 2. oyuncunun ekstra hakkını başlangıçta kullanılmamış yapar.
        }


        self.current_turn = PLAYER_1  # Oyuna ilk olarak 1. oyuncunun başlamasını sağlar.
        self.game_over = False  # Oyunun başlangıçta bitmediğini belirtir.
        self.winner = None  # Başlangıçta kazanan oyuncu olmadığı için None olarak ayarlar.
        self.last_roll = None  # Başlangıçta henüz zar atılmadığı için son zar değerini boş bırakır.
        self.last_message = "Game started. Player 1 begins."  # Client ekranında gösterilecek ilk oyun mesajını belirler.

    def roll_for_player(self, player_id):  # Belirli bir oyuncu için zar atma ve hamle yapma işlemini yürütür.
        if self.game_over:  # Oyun bittiyse yeni hamle yapılmasını engeller.
            return {  # Başarısız işlem sonucunu sözlük olarak döndürür.
                "success": False,  # İşlemin başarısız olduğunu belirtir.
                "message": "Game is already over.",  # Oyunun zaten bittiğini açıklayan mesajdır.
            }

        if player_id != self.current_turn:  # Eğer zar atmak isteyen oyuncu sıradaki oyuncu değilse kontrol eder.
            return {  # Sıra dışı hamle için başarısız işlem sonucu döndürür.
                "success": False,  # İşlemin başarısız olduğunu belirtir.
                "message": f"It is not Player {player_id}'s turn.",  # Oyuncunun sırası olmadığını açıklayan mesajdır.
            }

        dice_value = random.randint(1, 6)  # 1 ile 6 arasında rastgele zar değeri üretir.
        self.last_roll = dice_value  # Atılan son zar değerini saklar.

        move_message = self.move_player(player_id, dice_value)  # Oyuncuyu zar değeri kadar hareket ettirir ve oluşan mesajı alır.

        if not self.game_over:  # Hamleden sonra oyun bitmediyse sıra/ekstra hak kontrolü yapar.
            if dice_value == 6 and not self.extra_turn_used[player_id]:  # Zar 6 geldiyse ve oyuncu ekstra hakkını daha önce kullanmadıysa kontrol eder.
                self.extra_turn_used[player_id] = True  # Oyuncunun ekstra hakkını kullandığını işaretler.
                self.last_message += f" Player {player_id} rolled 6 and gets one extra turn."  # Mesaja oyuncunun ekstra hak kazandığını ekler.
            else:  # Zar 6 değilse veya oyuncu ekstra hakkını zaten kullandıysa çalışır.
                self.extra_turn_used[player_id] = False  # Oyuncunun ekstra hak durumunu sıfırlar.
                self.switch_turn()  # Sırayı diğer oyuncuya geçirir.

        return {  # Zar atma işleminin başarılı sonucunu döndürür.
            "success": True,  # İşlemin başarılı olduğunu belirtir.
            "dice": dice_value,  # Atılan zar değerini döndürür.
            "message": move_message,  # Hamle sonucunda oluşan mesajı döndürür.
        }

    def move_player(self, player_id, steps):  # Oyuncuyu verilen adım sayısı kadar hareket ettirir.
        current_position = self.player_positions[player_id]  # Oyuncunun mevcut pozisyonunu alır.
        new_position = current_position + steps  # Zar sonucuna göre yeni pozisyonu hesaplar.

        if new_position > FINAL_SQUARE:  # Yeni pozisyon 100. kareyi geçerse kontrol eder.
            self.last_message = (  # 100'ü geçme durumunda gösterilecek mesajı hazırlar.
                f"Player {player_id} rolled {steps}, "  # Oyuncunun kaç attığını mesaja ekler.
                f"but needs exact number to reach {FINAL_SQUARE}."  # Oyuncunun tam sayı ile bitişe ulaşması gerektiğini belirtir.
            )
            return self.last_message  # Oyuncuyu hareket ettirmeden mesajı döndürür.

        self.player_positions[player_id] = new_position  # Oyuncunun pozisyonunu yeni kareye taşır.

        message = (  # Normal hareket mesajını hazırlar.
            f"Player {player_id} rolled {steps} "  # Oyuncunun attığı zar değerini belirtir.
            f"and moved to square {new_position}."  # Oyuncunun ulaştığı kareyi belirtir.
        )

        final_position, extra_message = self.apply_snake_or_ladder(new_position)  # Yeni pozisyonda yılan/merdiven varsa uygular.
        self.player_positions[player_id] = final_position  # Oyuncunun pozisyonunu yılan/merdiven sonrası son pozisyona günceller.

        if extra_message:  # Eğer yılan veya merdiven mesajı oluştuysa kontrol eder.
            message += " " + extra_message  # Bu mesajı normal hareket mesajına ekler.

        if final_position == FINAL_SQUARE:  # Oyuncu tam olarak 100. kareye ulaştıysa kontrol eder.
            self.game_over = True  # Oyunu bitmiş olarak işaretler.
            self.winner = player_id  # Kazanan oyuncuyu kaydeder.
            message += f" Player {player_id} wins the game!"  # Kazanma bilgisini mesaja ekler.

        self.last_message = message  # Son oyun mesajını saklar.
        return message  # Hamle mesajını döndürür.

    def apply_snake_or_ladder(self, position):  # Oyuncunun geldiği karede yılan veya merdiven olup olmadığını kontrol eder.
        if position in SNAKES:  # Eğer mevcut pozisyon bir yılanın başıysa kontrol eder.
            new_position = SNAKES[position]  # Yılanın indirdiği yeni pozisyonu alır.
            message = (  # Yılan mesajını hazırlar.
                f"Snake! Player moved down "  # Oyuncunun aşağı indiğini belirtir.
                f"from square {position} to square {new_position}."  # Başlangıç ve bitiş karelerini mesaja ekler.
            )
            return new_position, message  # Yeni pozisyonu ve mesajı döndürür.

        if position in LADDERS:  # Eğer mevcut pozisyon bir merdivenin alt ucuysa kontrol eder.
            new_position = LADDERS[position]  # Merdivenin çıkardığı yeni pozisyonu alır.
            message = (  # Merdiven mesajını hazırlar.
                f"Ladder! Player climbed up "  # Oyuncunun yukarı çıktığını belirtir.
                f"from square {position} to square {new_position}."  # Başlangıç ve bitiş karelerini mesaja ekler.
            )
            return new_position, message  # Yeni pozisyonu ve mesajı döndürür.

        return position, ""  # Yılan veya merdiven yoksa aynı pozisyonu ve boş mesajı döndürür.

    def switch_turn(self):  # Sırayı bir oyuncudan diğer oyuncuya geçirir.
        if self.current_turn == PLAYER_1:  # Eğer sıra 1. oyuncudaysa kontrol eder.
            self.current_turn = PLAYER_2  # Sırayı 2. oyuncuya verir.
        else:  # Eğer sıra 2. oyuncudaysa çalışır.
            self.current_turn = PLAYER_1  # Sırayı 1. oyuncuya verir.

    def get_state(self):  # Client'lara gönderilecek güncel oyun durumunu sözlük olarak oluşturur.
        return {  # Oyun durumunu dict formatında döndürür.
            "player_positions": self.player_positions,  # Oyuncuların güncel pozisyonlarını içerir.
            "current_turn": self.current_turn,  # Şu anda sıranın hangi oyuncuda olduğunu içerir.
            "game_over": self.game_over,  # Oyunun bitip bitmediği bilgisini içerir.
            "winner": self.winner,  # Kazanan oyuncu bilgisini içerir.
            "last_roll": self.last_roll,  # Son atılan zar değerini içerir.
            "last_message": self.last_message,  # Son oyun mesajını içerir.
            "snakes": SNAKES,  # Yılanların başlangıç ve bitiş konumlarını içerir.
            "ladders": LADDERS,  # Merdivenlerin başlangıç ve bitiş konumlarını içerir.
        }