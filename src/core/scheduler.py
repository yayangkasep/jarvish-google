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
        prompt = "[SYSTEM_EVENT] Saat ini pukul 07:00 pagi. Ini adalah saatnya Anda (J.A.R.V.I.S) berinisiatif menghubungi Bos. WAJIB GUNAKAN TOOL (seperti CalendarTool, ReadRecentEmails, WebSearch) sekarang juga secara berurutan untuk membaca jadwal hari ini, meringkas email terbaru, dan mengecek cuaca! JANGAN berasumsi data sudah ada. Setelah mendapat data dari tool, buatlah pesan sapaan pagi yang proaktif kepada Bos."
        self.broadcast_event(prompt)
        
    def trigger_afternoon(self):
        prompt = "[SYSTEM_EVENT] Saat ini pukul 12:00 siang. J.A.R.V.I.S, berinisiatiflah menyapa Bos. WAJIB GUNAKAN TOOL ReadRecentEmails untuk mengecek pesan mendesak. Ingatkan Bos untuk istirahat dan makan siang berdasarkan data yang Anda temukan."
        self.broadcast_event(prompt)
        
    def trigger_evening(self):
        prompt = "[SYSTEM_EVENT] Saat ini pukul 17:00 sore. J.A.R.V.I.S, hubungi Bos! WAJIB GUNAKAN TOOL TaskTool atau CalendarTool untuk mengevaluasi apakah ada tugas hari ini yang terlewat. Ingatkan Bos untuk bersiap pulang."
        self.broadcast_event(prompt)
        
    def trigger_night(self):
        prompt = "[SYSTEM_EVENT] Saat ini pukul 20:00 malam. J.A.R.V.I.S, berikan laporan penutup hari. WAJIB GUNAKAN TOOL jika Anda butuh melihat rekapan, lalu perintahkan Bos untuk bersantai."
        self.broadcast_event(prompt)
