import schedule
import time
import threading

class BackgroundScheduler:
    def __init__(self, callback, get_users_cb):
        """
        callback(user_id, text): Triggered to make JARVIS act
        get_users_cb(): Returns a list of telegram user IDs to broadcast to
        """
        self.callback = callback
        self.get_users_cb = get_users_cb
        self.running = False
        self.thread = None

    def start(self):
        if self.running: return
        
        self.running = True
        
        # Schedule the proactive routines (Time is based on local system time / WSL)
        schedule.every().day.at("07:00").do(self.trigger_morning)
        schedule.every().day.at("12:00").do(self.trigger_afternoon)
        schedule.every().day.at("17:00").do(self.trigger_evening)
        schedule.every().day.at("20:00").do(self.trigger_night)
        
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("[Scheduler] Proactive background thread started successfully!")

    def _run(self):
        while self.running:
            schedule.run_pending()
            time.sleep(30) # Check every 30 seconds to save CPU
            
    def broadcast_event(self, event_text):
        users = self.get_users_cb()
        if not users:
            print("[Scheduler] No users found in database to broadcast to.")
            return
            
        for user_id in users:
            print(f"[Scheduler] Triggering proactive event for user {user_id}")
            self.callback(user_id, event_text)

    def trigger_morning(self):
        prompt = "[SYSTEM_EVENT] Saat ini pukul 07:00 pagi. Ini adalah saatnya Anda (J.A.R.V.I.S) berinisiatif menghubungi Bos. Baca jadwal kalender hari ini, ringkas email terbaru yang masuk semalaman, dan cek cuaca. Kemudian buatlah pesan sapaan selamat pagi yang proaktif, bersemangat, dan informatif kepada Bos beserta hasil temuan tersebut!"
        self.broadcast_event(prompt)
        
    def trigger_afternoon(self):
        prompt = "[SYSTEM_EVENT] Saat ini pukul 12:00 siang. J.A.R.V.I.S, berinisiatiflah menyapa Bos. Ingatkan Bos untuk istirahat dan makan siang. Cek email terbaru dan sampaikan jika ada pesan atau tugas mendesak yang butuh perhatian."
        self.broadcast_event(prompt)
        
    def trigger_evening(self):
        prompt = "[SYSTEM_EVENT] Saat ini pukul 17:00 sore. J.A.R.V.I.S, hubungi Bos! Ingatkan bahwa ini waktu yang tepat untuk bersiap mengakhiri pekerjaan hari ini. Evaluasi sekilas jika ada target/jadwal yang belum diselesaikan."
        self.broadcast_event(prompt)
        
    def trigger_night(self):
        prompt = "[SYSTEM_EVENT] Saat ini pukul 20:00 malam. J.A.R.V.I.S, berikan laporan penutup hari. Rangkum peristiwa hari ini secara singkat dan perintahkan Bos untuk bersantai dan istirahat penuh energi untuk esok hari."
        self.broadcast_event(prompt)
