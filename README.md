# computer-networks-game-project
# Yılanlar ve Merdivenler - Bilgisayar Ağları Projesi

Python ve PyQt6 kullanılarak geliştirilmiş çok oyunculu bir Yılanlar ve Merdivenler oyunudur.

Bu proje, Bilgisayar Ağları dersi kapsamında geliştirilmiştir. Oyun, istemci-sunucu (client-server) mimarisi kullanılarak gerçek zamanlı olarak iki oyuncu arasında oynanabilmektedir.

---

# Proje Özeti

Bu projede TCP socket programlama kullanılarak çok oyunculu bir oyun sistemi geliştirilmiştir. Server uygulaması oyunun tüm mantığını yönetirken, client uygulamaları PyQt6 kullanılarak geliştirilen grafiksel arayüz üzerinden oyuncuların oyuna katılmasını sağlar.

Server ve client arasında veri iletişimi JSON tabanlı özel bir protokol ile gerçekleştirilmiştir.

---

# Özellikler

- Çok oyunculu istemci-sunucu mimarisi
- TCP socket tabanlı iletişim
- Gerçek zamanlı oyun senkronizasyonu
- PyQt6 grafik arayüzü
- Özel çizim kullanılan oyun tahtası
- Animasyonlu zar sistemi
- Yılan ve merdiven mekanikleri
- Sıra tabanlı oyun sistemi
- Oyun durumu senkronizasyonu
- Yeniden oynama sistemi
- Rakip bağlantı kopma kontrolü
- AWS üzerinde çalıştırılabilir server desteği
- JSON tabanlı mesajlaşma sistemi
- Çoklu thread kullanımı
- Platform bağımsız yapı

---

# Kullanılan Teknolojiler

- Python 3
- PyQt6
- TCP Socket Programming
- Multithreading
- JSON Protocol
- AWS EC2
- Object Oriented Programming (OOP)

---

# Sistem Mimarisi

Projede istemci-sunucu mimarisi kullanılmıştır.

## Server Tarafı

Server aşağıdaki görevlerden sorumludur:

- Client bağlantılarını kabul etmek
- Oyunculara player ID atamak
- Oyun kurallarını yönetmek
- Zar işlemlerini gerçekleştirmek
- Oyun durumunu senkronize etmek
- Tüm client'lara güncel state göndermek
- Oyun sonunu kontrol etmek
- Yeniden oynama sistemini yönetmek

Server tarafında her oyuncu için ayrı bir thread oluşturulmuştur. Böylece aynı anda birden fazla client bağlantısı yönetilebilmektedir.

---

## Client Tarafı

Client uygulaması aşağıdaki bileşenlerden oluşmaktadır:

### Start Window
- Server IP ve port bilgisi alma
- Server bağlantısı kurma

### Game Window
- Oyun tahtasını gösterme
- Zar animasyonu
- Oyuncu hareketleri
- Sıra kontrolü
- Oyun mesajları

### Board Widget
- Oyun tahtasının özel çizim ile oluşturulması
- Oyuncu taşlarının dinamik olarak hareket ettirilmesi

### Dice Widget
- Zar animasyonu
- Rastgele geçici zar görselleri
- Final zar sonucunun gösterilmesi

### Result Dialog
- Kazanma/kaybetme ekranı
- Tekrar oynama isteği gönderme

---

# Ağ Haberleşmesi

İstemci ve sunucu arasında TCP socket haberleşmesi kullanılmaktadır.

Tüm mesajlar JSON formatında gönderilmektedir.

Örnek mesaj:

```json
{
    "type": "ROLL_DICE"
}
```

Mesajlar UTF-8 formatında encode edilerek gönderilmektedir.

---

# Kullanılan Protokol Mesajları

| Mesaj Tipi | Açıklama |
|---|---|
| ASSIGN_PLAYER | Oyuncuya ID atanması |
| WAITING | İkinci oyuncunun beklenmesi |
| GAME_START | Oyunun başlatılması |
| GAME_STATE | Güncel oyun durumunun gönderilmesi |
| ROLL_DICE | Zar atma isteği |
| GAME_OVER | Oyunun bitmesi |
| ERROR | Hata mesajı |
| RESTART_REQUEST | Yeniden oynama isteği |
| RESTART_WAITING | Diğer oyuncunun beklenmesi |
| OPPONENT_LEFT | Rakibin oyundan ayrılması |

---

# Oyun Mantığı

Oyun mantığı tamamen server tarafında çalışmaktadır.

## Oyun Kuralları

- Oyun 2 oyuncu ile oynanır.
- Oyuncular sırayla zar atar.
- Oyuncu tam olarak 100. kareye ulaşmalıdır.
- 6 atan oyuncu bir ekstra hak kazanır.
- Aynı oyuncu arka arkaya sınırsız şekilde 6 atamaz.
- Merdivene gelen oyuncu yukarı çıkar.
- Yılana gelen oyuncu aşağı iner.
- 100. kareye ilk ulaşan oyuncu oyunu kazanır.

---

# Thread Yapısı

Projede çoklu thread kullanılmıştır.

## Client Side
- Ana GUI thread
- Server dinleme thread

## Server Side
- Ana bağlantı thread
- Her oyuncu için ayrı client thread

Bu yapı sayesinde GUI donmadan gerçek zamanlı iletişim sağlanabilmektedir.

---

# AWS Desteği

Server uygulaması AWS EC2 üzerinde çalıştırılabilir.

AWS üzerinde:
- TCP 5000 portu açılmıştır
- Client'lar public IP üzerinden bağlanmaktadır

---

# Kurulum

## Repository Klonlama

```bash
git clone https://github.com/mervedegirmen/computer-networks-game-project.git
```

---

## Sanal Ortam Oluşturma

```bash
python -m venv .venv
```

Aktifleştirme:

```bash
.venv\Scripts\activate
```

---

# Kütüphanelerin Kurulumu

```bash
pip install -r requirements.txt
```

---

# requirements.txt

```txt
PyQt6
requests
```

---

# Server Çalıştırma

```bash
python -m server.server
```

---

# Client Çalıştırma

```bash
python -m client.main
```

İkinci oyuncu için başka terminalden tekrar çalıştırılır.

---

# Lokal Test

| Ayar | Değer |
|---|---|
| IP | 127.0.0.1 |
| Port | 5000 |

---

# AWS Testi

Client uygulamalarında:
- Server IP kısmına AWS public IP adresi girilir
- Port olarak 5000 kullanılır

---

# Hata Yönetimi

Projede aşağıdaki hata durumları kontrol edilmektedir:

- Yanlış sıra ile zar atma
- Oyun dolu olması
- Bağlantı kopması
- Rakibin ayrılması
- Geçersiz port girişi
- Oyun bitmeden restart isteği

---

# Platform Bağımsızlık

Proje:
- Hardcoded dosya yolu içermemektedir
- Farklı bilgisayarlarda çalışabilecek şekilde hazırlanmıştır
- Virtual environment desteği ile bağımlılık yönetimi yapılmıştır

---

# English Version

# Snakes and Ladders - Computer Networks Project

A multiplayer Snakes and Ladders game developed using Python and PyQt6.

This project was developed for the Computer Networks course using a client-server architecture and TCP socket programming.

---

# Technical Features

- Multiplayer client-server architecture
- TCP socket communication
- Real-time game synchronization
- PyQt6 graphical interface
- Custom painted game board
- Animated dice system
- JSON-based communication protocol
- Multithreading support
- AWS EC2 server deployment
- Restart/play again system
- Opponent disconnect detection

---

# System Architecture

## Server Side
The server is responsible for:
- Managing client connections
- Assigning player IDs
- Running game logic
- Synchronizing game state
- Broadcasting updates
- Managing restart requests

Each client connection runs on a separate thread.

---

## Client Side

### Start Window
- Server IP/port input
- Connection management

### Game Window
- Board display
- Turn management
- Dice rolling
- Message display

### Board Widget
- Custom board rendering
- Dynamic pawn movement

### Dice Widget
- Dice animation
- Temporary random dice rendering
- Final dice visualization

### Result Dialog
- Win/Lose screen
- Replay request system

---

# Networking

The project uses TCP socket communication.

All data is transferred using JSON messages encoded with UTF-8.

Example:

```json
{
    "type": "ROLL_DICE"
}
```

---

# Threading Model

## Client
- Main GUI thread
- Server listening thread

## Server
- Main server thread
- One thread per client

This architecture prevents GUI freezing and supports real-time communication.

---

# AWS Support

The server can run on AWS EC2.

- TCP port 5000 is used
- Clients connect using the public AWS IP

---

# Dependencies

```txt
PyQt6
requests
```

---

# Run Server

```bash
python -m server.server
```

---

# Run Client

```bash
python -m client.main
```

---

# Error Handling

The project handles:
- Invalid turns
- Full server
- Disconnections
- Opponent leaving
- Invalid port inputs
- Invalid restart requests

---

# Platform Independence

The project:
- Does not use hardcoded file paths
- Supports multiple systems
- Uses virtual environment dependency management