class OutputView:
    def display_welcome(self):
        print("=== IMAGE TO FONT ===")

    def display_message(self, message: str):
        print(f"[#] {message}")

    def display_suceess(self):
        print(f"=====================")
        print(f"     프로그램 종료     ")
        print(f"=====================")

    def display_error(self, error_message: str):
        print(f"[오류] {error_message}")
