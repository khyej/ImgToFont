import os
import argparse

from view.output_view import OutputView
from model.font_builder import FontBuilder


def main():
    view = OutputView()
    view.display_welcome()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 절대 경로

    args = _setup_args(base_dir)
    potrace_execute = _setup_potrace(base_dir)

    try:
        builder = FontBuilder(
            image_dir=args.image_dir,
            svg_dir=args.svg_dir,
            font_path=args.font_path,
            potrace_path=potrace_execute,
            font_name=args.font_name,
            callback=view.display_message
        )
        builder.build_all()
        view.display_suceess(args.font_path)
    except Exception as e:
        view.display_error(f"Font Build : {e}")


def _setup_args(base_dir):
    parser = argparse.ArgumentParser()

    parser.add_argument(  # 기본 png 폴더 경로 : ImgToFont/image/png/
        "-i", "--input",
        dest="image_dir",
        default=os.path.join(base_dir, "image", "png"),
        help="PNG 폴더"
    )

    parser.add_argument(  # 기본 svg 폴더 경로 : ImgToFont/image/svg/
        "-s", "--svg",
        dest="svg_dir",
        default=os.path.join(base_dir, "image", "svg"),
        help="SVG 폴더"
    )

    parser.add_argument(  # 기본 ttf 저장 경로 : ImgToFont/font/Font.ttf
        "-o", "--output",
        dest="font_path",
        default=os.path.join(base_dir, "font", "Font.ttf"),
        help="Font 폴더"
    )

    parser.add_argument(  # 기본 Font 이름 : Font
        "-n", "--name",
        dest="font_name",
        default="Font",
        help="Font Name"
    )

    args = parser.parse_args()

    os.makedirs(args.image_dir, exist_ok=True)
    os.makedirs(args.svg_dir, exist_ok=True)
    os.makedirs(os.path.dirname(args.font_path), exist_ok=True)

    return args


def _setup_potrace(base_dir):
    potrace_execute = "potrace"  # 리눅스 환경

    if os.name == "nt":  # 윈도우 환경
        potrace_execute = os.path.join(base_dir, "potrace.exe")

    return potrace_execute


if __name__ == "__main__":
    main()
