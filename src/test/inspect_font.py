from fontTools.ttLib import TTFont


def inspect_font(font_path):
    font = TTFont(font_path)

    # ttf - 테이블 목록
    check_tables = ["head", "hhea", "maxp", "OS/2", "hmtx", "cmap", "loca", "name",
                    "post", "glyf"]

    for tag in check_tables:
        if tag not in font:
            print(f"\nTable {tag} not found in font")
            continue

        table = font[tag]
        print(f"\n=== Table: {tag} ===")

        # __dict__ 필드 출력
        for field in table.__dict__:
            print(f"{field} = {getattr(table, field)}")


if __name__ == "__main__":
    inspect_font("../../font/Font.ttf")
