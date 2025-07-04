import time
import win32gui
import csv
from datetime import datetime
import os


def format_duration(seconds):
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {sec}s"
    elif minutes:
        return f"{minutes}m {sec}s"
    else:
        return f"{sec}s"


def get_active_window_title():
    window = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(window)
    return title


def log_to_csv(window_title, duration):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_exists = os.path.isfile('data/usage_log.csv')

    with open('data/usage_log.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists or os.stat('data/usage_log.csv').st_size == 0:
            writer.writerow(['app_name', 'duration', 'timestamp'])
        writer.writerow([window_title, duration, now])


def main():
    last_title = None
    active_time = 0
    check_interval = 1
    IGNORED_TITLES = ["", "Başlat", "Görev Yöneticisi"]

    try:
        while True:
            current_title = get_active_window_title()

            if current_title in IGNORED_TITLES:
                time.sleep(check_interval)
                continue

            if current_title == last_title:
                active_time += check_interval
            else:
                if last_title:
                    print(
                    f"'{last_title}' application was active for {active_time} seconds.")
                    log_to_csv(last_title, active_time)
                last_title = current_title
                active_time = check_interval

            time.sleep(check_interval)


    except KeyboardInterrupt:
        if last_title:
            print(
            f"\nExiting program. Last active window: {last_title} ({format_duration(active_time)})")
            log_to_csv(last_title, active_time)
        print("Exited.")

if __name__ == "__main__":
    main()
