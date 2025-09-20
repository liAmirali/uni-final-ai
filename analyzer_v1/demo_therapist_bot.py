#!/usr/bin/env python3
"""
Mental Health Assessment Demo
A presentation-ready CLI for the Therapist Bot
"""

import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from therapist_bot import TherapistBot
except ImportError as e:
    print(f"❌ Error importing therapist bot: {e}")
    print("Make sure you're running this from the correct directory and have all dependencies installed.")
    sys.exit(1)
 
# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Persian-friendly colors
    QUESTION = '\033[96m'  # Cyan
    USER = '\033[92m'      # Green
    SYSTEM = '\033[94m'    # Blue
    ANALYSIS = '\033[93m'  # Yellow


def print_banner():
    """Print welcome banner"""
    banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    🧠 سیستم تحلیل سلامت روان سالمندان - Mental Health AI         ║
║                                                                  ║
║    🎯 ارزیابی سلامت روان با هوش مصنوعی                          ║
║    📊 تحلیل جامع بر اساس پاسخ‌های شما                           ║
║    🔬 طراحی شده برای دوران سالمندی                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)


def print_instructions():
    """Print usage instructions"""
    instructions = f"""
{Colors.OKBLUE}📋 راهنمای استفاده:{Colors.ENDC}

{Colors.OKGREEN}✓{Colors.ENDC} سیستم چندین سوال از شما خواهد پرسید
{Colors.OKGREEN}✓{Colors.ENDC} هر پاسخ توسط هوش مصنوعی تحلیل می‌شود
{Colors.OKGREEN}✓{Colors.ENDC} برای خروج از برنامه "خروج" یا "exit" تایپ کنید
{Colors.OKGREEN}✓{Colors.ENDC} پاسخ‌های صادقانه دقت تحلیل را بالا می‌برد
"""
    print(instructions)


def check_environment():
    """Check if all required environment variables and files are present"""
    required_env_vars = ['AVALAI_API_KEY']
    required_files = [
        'knowledge_base/mindmap.json',
        'knowledge_base/mental_health_subjects.json'
    ]
    
    missing_env = []
    missing_files = []
    
    # Check environment variables
    for var in required_env_vars:
        if not os.getenv(var):
            missing_env.append(var)
    
    # Check required files
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_env or missing_files:
        print(f"{Colors.FAIL}❌ پیکربندی ناقص:{Colors.ENDC}")
        
        if missing_env:
            print(f"{Colors.WARNING}متغیرهای محیطی مفقود:{Colors.ENDC}")
            for var in missing_env:
                print(f"  • {var}")
        
        if missing_files:
            print(f"{Colors.WARNING}فایل‌های مفقود:{Colors.ENDC}")
            for file_path in missing_files:
                print(f"  • {file_path}")
        
        print(f"\n{Colors.OKBLUE}💡 لطفاً .env فایل را بررسی کنید و فایل‌های مورد نیاز را اضافه کنید{Colors.ENDC}")
        return False
    
    return True


def create_session_log():
    """Create a log file for this session"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("demo_sessions")
    log_dir.mkdir(exist_ok=True)
    
    return log_dir / f"session_{timestamp}.log"


def print_typing_effect(text, delay=0.03):
    """Print text with typing effect for dramatic presentation"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def run_demo():
    """Run the therapist bot demo"""
    
    print_banner()
    time.sleep(1)
    
    print_instructions()
    time.sleep(1)
    
    # Check environment
    print(f"{Colors.SYSTEM}🔍 بررسی پیکربندی سیستم...{Colors.ENDC}")
    if not check_environment():
        return False
    
    print(f"{Colors.OKGREEN}✅ سیستم آماده است{Colors.ENDC}")
    time.sleep(1)
    
    # Create session log
    log_file = create_session_log()
    print(f"{Colors.SYSTEM}📝 جلسه در فایل {log_file} ثبت می‌شود{Colors.ENDC}")
    
    try:
        # Initialize the therapist bot
        print(f"\n{Colors.SYSTEM}🚀 راه‌اندازی سیستم هوش مصنوعی...{Colors.ENDC}")
        
        bot = TherapistBot()
        
        print(f"{Colors.OKGREEN}✅ سیستم آماده است! شروع ارزیابی...{Colors.ENDC}")
        print("=" * 80)
        
        # Log session start
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Mental Health Assessment Session\n")
            f.write(f"Started: {datetime.now().isoformat()}\n")
            f.write("=" * 50 + "\n\n")
        
        # Run the bot
        bot.run()
        
        # Log session end
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n" + "=" * 50 + "\n")
            f.write(f"Ended: {datetime.now().isoformat()}\n")
        
        print("=" * 80)
        print(f"{Colors.OKGREEN}✅ جلسه ارزیابی به پایان رسید{Colors.ENDC}")
        print(f"{Colors.SYSTEM}📊 گزارش کامل در فایل {log_file} ذخیره شد{Colors.ENDC}")
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  برنامه توسط کاربر متوقف شد{Colors.ENDC}")
        return False
        
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ خطا در اجرای سیستم: {e}{Colors.ENDC}")
        print(f"{Colors.SYSTEM}لطفاً پیکربندی و اتصال اینترنت را بررسی کنید{Colors.ENDC}")
        return False


def main():
    """Main entry point"""
    try:
        success = run_demo()
        if success:
            print(f"\n{Colors.OKGREEN}🎉 دمو با موفقیت به پایان رسید{Colors.ENDC}")
        else:
            print(f"\n{Colors.WARNING}⚠️  دمو زودتر از موعد متوقف شد{Colors.ENDC}")
            
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ خطای غیرمنتظره: {e}{Colors.ENDC}")
        sys.exit(1)
    
    finally:
        print(f"\n{Colors.SYSTEM}تشکر از استفاده از سیستم تحلیل سلامت روان{Colors.ENDC}")


if __name__ == "__main__":
    main()
