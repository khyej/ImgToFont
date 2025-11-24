import sys
import os

class OutputView:
    def display_welcome(self):
        print("=" * 40)
        print(f"{'IMAGE TO FONT CONVERTER':^40}")
        print("=" * 40)
        print()

    def display_step(self, step_num, total_step, message):
        print(f"[{step_num}/{total_step}] {message}")

    def display_subtask(self, message):
        print(f"    └─ {message}")

    # def display_message(self, message: str):
    #     print(f"[#] {message}")

    def display_progress(self, current, total, message=None):
        if total == 0: total = 1

        percent = int((current/total) * 100)
        bar_length = 20
        fill_length = int(bar_length * current // total)
        bar = "■" * fill_length + "□" * (bar_length - fill_length)

        msg = f"{message} " if message else ""
        sys.stdout.write(f"\r    └─ {msg}|  {bar}  | {percent}%_({current}/{total})")
        sys.stdout.flush()

        if current == total:
            print()

    def display_suceess(self, output_path):
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            size_kb = file_size / 1024
        else:
            size_kb = 0

        print()
        print(f"폰트가 성공적으로 만들어졌습니다.")
        self.display_subtask(f"경로 : {output_path}")
        self.display_subtask(f"크기 : {size_kb:.1f} KB")
        print("=" * 40)

    def display_error(self, error_message: str):
        print(f"[오류] {error_message}")
