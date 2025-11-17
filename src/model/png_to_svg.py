import os
import subprocess
from PIL import Image


class PngToSvg:
    def __init__(self, potrace_path):
        self.potrace_path = potrace_path

    def convert_all(self, input_dir, output_dir):
        try:
            self._set_output_dir(output_dir)
            png_files = self._get_png_files(input_dir)

            for file in png_files:
                png_path = os.path.join(input_dir, file)
                svg_file = os.path.splitext(file)[0] + ".svg"
                svg_path = os.path.join(output_dir, svg_file)

                self._convert_file(png_path, svg_path)
        except Exception as e:
            raise Exception(f"PNG TO SVG : {e}")

    def _set_output_dir(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def _get_png_files(self, input_dir):
        png_files = []
        for filename in os.listdir(input_dir):
            if filename.endswith(".png"):
                png_files.append(filename)
        return png_files

    def _convert_file(self, input_path, output_path):
        bmp_path = os.path.splitext(output_path)[0] + ".temp.bmp"

        try:
            img = Image.open(input_path)
            img.convert("1").save(bmp_path)

            command = [
                self.potrace_path,
                bmp_path,
                "-s",
                "-o", output_path,
                "--unit", "1"
            ]

            subprocess.run(command, check=True, capture_output=True, text=True,
                           encoding="utf-8")
        except FileNotFoundError:
            error_msg = f"Potrace('{self.potrace_path}') 실행 불가, README.md를 확인해주세요."
            raise Exception(error_msg)
        except subprocess.CalledProcessError as e:
            error_msg = f"{input_path} 변환 실패 : {e.stderr}"
            raise Exception(error_msg)
