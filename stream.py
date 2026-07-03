import subprocess
import requests
import time
import os

# ====================================================
# 📝 بيانات البث (سيتم قراءتها من جيتهاب أولاً لحمايتك، أو من هنا مباشرة)
# ====================================================
PAGE_ID = os.environ.get("PAGE_ID", "122169831068820017")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "EAAfJqZBCYJQoBRyyzC6WV97UIDc6mthoZA9HBpb1JSVubvq3f0B9saGXzwKJJ5QikQqjoZBwBvieBr24nLOJyTIiVKAfQK436joZAESh3vt338vcqJKT5ZBqUPZBawUrybzbvYnQtfnv8QfixZCU5YKZCbidyJwZAJcYWXgakIwf8oK6SGDFtqEWP2hWSC8vZA")
INPUT_URL = "http://071024.com:88/live/02029921082595/02029921082595/2159447.m3u8"
STREAM_TITLE = "بث مباشر برو"
OUTPUT_FILE = "live_link.txt" 

def create_fb_live(page_id, token, title):
    url = f"https://graph.facebook.com/v19.0/{page_id}/live_videos"
    payload = {
        'status': 'UNPUBLISHED',
        'title': title,
        'description': f'Live stream: {title}',
        'access_token': token,
        'fields': 'stream_url,id,permalink_url'
    }
    try:
        res = requests.post(url, data=payload)
        data = res.json()
        if 'stream_url' in data:
            return data['stream_url'], data.get('permalink_url', '')
        else:
            print(f"❌ خطأ من فيسبوك: {data.get('error', {}).get('message', 'خطأ غير معروف')}")
            return None, None
    except Exception as e:
        print(f"❌ خطأ في الاتصال بالشبكة: {e}")
        return None, None

def main():
    if "ضع_هنا" in PAGE_ID or "ضع_هنا" in ACCESS_TOKEN or "ضع_هنا" in INPUT_URL:
        print("⚠️ تنبيه: يرجى استبدال القيم الافتراضية ببياناتك الحقيقية!")
        return

    print(f"🔄 جاري إنشاء البث على فيسبوك: [{STREAM_TITLE}]...")
    rtmp_url, direct_video_url = create_fb_live(PAGE_ID, ACCESS_TOKEN, STREAM_TITLE)
    
    if not rtmp_url:
        print("❌ فشل إنشاء البث. يرجى التحقق من التوكن أو الـ ID.")
        return
        
    print("\n" + "="*50)
    print(f"🚀 تم إنشاء البث بنجاح!")
    print(f"🔗 رابط الفيديو المباشر للمشاهدة: {direct_video_url}")
    print("="*50 + "\n")

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(direct_video_url)
        print(f"💾 تم حفظ الرابط بنجاح في ملف: {OUTPUT_FILE}")
    except Exception as e:
        print(f"⚠️ فشل حفظ الرابط في الملف: {e}")

    print("\n🎬 جاري تشغيل FFmpeg وضخ الستريم بجودة عالية مع الشعار...")
    
    # إعدادات الفلتر لإضافة نص "Neo IPTV PRO" أسفل المنتصف بخلفية شفافة
    # تم تحديد مسار الخط الافتراضي في سيرفرات لينكس (جيتهاب) لضمان عمله
    video_filter = (
        "drawtext=text='Neo IPTV PRO':"
        "x=(w-text_w)/2:y=h-th-40:"
        "fontcolor=white:fontsize=32:"
        "box=1:boxcolor=black@0.4:"
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    )

    # مصفوفة أوامر FFmpeg للبث بجودة عالية FHD/HD ثابته وممتازة لفيسبوك
    ffmpeg_cmd = [
        "ffmpeg", "-re", "-i", INPUT_URL,
        "-vf", video_filter,
        "-c:v", "libx264", "-preset", "veryfast", 
        "-b:v", "4000k", "-maxrate", "4000k", "-bufsize", "8000k",
        "-g", "60", "-pix_fmt", "yuv420p", # إعدادات توافق فيسبوك (Keyframe كل ثانيتين)
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
        "-f", "flv", rtmp_url
    ]

    try:
        proc = subprocess.Popen(ffmpeg_cmd)
        
        start_time = time.time()
        # 3 ساعات و 50 دقيقة = 13800 ثانية 
        # نغلق السكربت قبل الـ 4 ساعات بقليل ليقوم الـ Action القادم بفتح بث جديد تلقائياً دون تداخل
        max_duration = 13800 
        
        while proc.poll() is None:
            elapsed_time = time.time() - start_time
            if elapsed_time > max_duration:
                print("\n⏰ مرت 3 ساعات و50 دقيقة. يتم إغلاق البث الحالي لتجديده عبر GitHub Action...")
                proc.terminate()
                break
            time.sleep(5)
            
        if proc.poll() is not None and elapsed_time <= max_duration:
            print("\n🛑 توقف البث تلقائياً من المصدر (قد يكون رابط الـ m3u8 قد انتهى).")
            
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البث يدويًا.")
        if 'proc' in locals() and proc.poll() is None:
            proc.terminate()

if __name__ == "__main__":
    main()
