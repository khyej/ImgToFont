import sys

class OutputView:
    def display_welcome(self):
        print("=" * 40)
        print(f"{'IMAGE TO FONT CONVERTER':^40}")
        print("=" * 40)
        print()

    def display_message(self, message: str):
        print(f"[#] {message}")

    def display_progress(self, current, total, message=None):
        percent = int((current/total) * 100)
        bar_length = 20
        fill_length = int(bar_length * current // total)
        bar = "■" * fill_length + "□" * (bar_length - fill_length)

        sys.stdout.write(f"\r   -> {message} |  {bar}  | {percent}%_({current}/{total})")
        sys.stdout.flush()

        if current == total:
            print()

    def display_suceess(self):
        print(f"=====================")
        print(f"     프로그램 종료     ")
        print(f"=====================")

    def display_error(self, error_message: str):
        print(f"[오류] {error_message}")
