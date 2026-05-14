DEFAULT_HOST = "56.228.5.62"  # Client başlangıç ekranında varsayılan olarak gösterilecek server IP adresidir.
DEFAULT_PORT = 5000  # Client ve server iletişimi için kullanılacak varsayılan port numarasıdır.

MAX_PLAYERS = 2  # Oyuna bağlanabilecek maksimum oyuncu sayısını belirler.
BOARD_SIZE = 10  # Tahtanın 10x10 kareden oluştuğunu belirtir.
FINAL_SQUARE = 100  # Oyunun kazanılması için ulaşılması gereken son kare numarasıdır.

PLAYER_1 = 1  # Birinci oyuncuyu temsil eden sabit değerdir.
PLAYER_2 = 2  # İkinci oyuncuyu temsil eden sabit değerdir.

SNAKES = {  # Yılanların başlangıç ve bitiş karelerini tutan sözlüktür.
    16: 6,  # 16. kareye gelen oyuncu yılan nedeniyle 6. kareye iner.
    47: 26,  # 47. kareye gelen oyuncu 26. kareye iner.
    49: 11,  # 49. kareye gelen oyuncu 11. kareye iner.
    56: 53,  # 56. kareye gelen oyuncu 53. kareye iner.
    62: 19,  # 62. kareye gelen oyuncu 19. kareye iner.
    64: 60,  # 64. kareye gelen oyuncu 60. kareye iner.
    87: 24,  # 87. kareye gelen oyuncu 24. kareye iner.
    93: 73,  # 93. kareye gelen oyuncu 73. kareye iner.
    95: 75,  # 95. kareye gelen oyuncu 75. kareye iner.
    98: 78,  # 98. kareye gelen oyuncu 78. kareye iner.
}

LADDERS = {  # Merdivenlerin başlangıç ve bitiş karelerini tutan sözlüktür.
    1: 38,  # 1. kareye gelen oyuncu merdivenle 38. kareye çıkar.
    4: 14,  # 4. kareye gelen oyuncu 14. kareye çıkar.
    9: 31,  # 9. kareye gelen oyuncu 31. kareye çıkar.
    21: 42,  # 21. kareye gelen oyuncu 42. kareye çıkar.
    28: 84,  # 28. kareye gelen oyuncu 84. kareye çıkar.
    36: 44,  # 36. kareye gelen oyuncu 44. kareye çıkar.
    51: 67,  # 51. kareye gelen oyuncu 67. kareye çıkar.
    71: 91,  # 71. kareye gelen oyuncu 91. kareye çıkar.
    80: 100,  # 80. kareye gelen oyuncu merdivenle doğrudan 100. kareye çıkar.
}