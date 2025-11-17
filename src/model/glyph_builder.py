import os
import re
import xml.etree.ElementTree as ET

from xml.etree.ElementTree import XMLParser
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen


class GlyphBuilder:
    def __init__(self, upm: int = 1000):
        self.upm = upm
        self.PATH_REGEX = re.compile(r"([MLCZmlcz])([^MLCZmlcz]*)")
        self.current_x = 0
        self.current_y = 0
        self.svg_height = None
        self.y_flip = False

        self.path_transform = ""
        self.svg_transform = ""

    def build_svg_to_glyph(self, svg_path: str) -> TTGlyphPen:
        svg_info = self._extract_svg_info(svg_path)

        self.svg_height = svg_info.get("height", self.upm)
        self.y_flip = svg_info.get("y_flip", False)
        self.path_transform = svg_info.get("path_transform", "")
        self.svg_transform = svg_info.get("svg_transform", "")

        path_d = svg_info["path_d"]

        result_pen = TTGlyphPen(None)
        converter_pen = Cu2QuPen(result_pen, max_err=1)
        self._parse_path_to_pen(path_d, converter_pen)

        return result_pen

    def _extract_svg_info(self, svg_path: str) -> dict:
        if not os.path.exists(svg_path):
            raise FileNotFoundError(f"파일 X: {svg_path}")

        parser = XMLParser()
        tree = ET.parse(svg_path, parser=parser)
        root = tree.getroot()
        ns = {"svg": "http://www.w3.org/2000/svg"}

        svg_transform = root.get("transform") or ""
        g_el = root.find(".//svg:g", ns) or root.find(".//g")

        if g_el is not None:
            g_transform = g_el.get("transform") or ""
            if g_transform:
                svg_transform = f"{svg_transform} {g_transform}" if svg_transform else g_transform

        y_flip = "scale(1,-1)" in svg_transform.lower()

        search_root = g_el if g_el is not None else root
        path_el = search_root.find(".//svg:path", ns)

        if path_el is None:
            path_el = search_root.find(".//path")
        if path_el is None:
            raise Exception(f"SVG : <path> 태그 없음")

        d = path_el.get("d")
        if not d:
            raise Exception("SVG : <path> d 속성 없음.")

        path_transform = path_el.get("transform") or ""
        if "scale(1,-1)" in path_transform.lower():
            y_flip = True

        return {
            "path_d": d,
            "height": self.upm,
            "y_flip": y_flip,
            "svg_transform": svg_transform,
            "path_transform": path_transform,
        }

    # 평행 이동
    def _translate_point(self, x, y, tx, ty):
        return x + tx, y + ty

    # 확대 / 축소
    def _scale_point(self, x, y, sx, sy):
        return x * sx, y * sy

    def _transform_point(self, x, y, transform_str):
        if not transform_str:
            return x, y

        transform_re = re.compile(r"(\w+)\(([^)]*)\)")

        matches = transform_re.findall(transform_str)

        for name, args in reversed(matches):
            vals = [float(v) for v in re.split(r"[ ,]+", args.strip()) if v]

            if name == "translate":
                tx = vals[0]
                ty = vals[1] if len(vals) > 1 else 0
                x, y = self._translate_point(x, y, tx, ty)

            elif name == "scale":
                sx = vals[0]
                sy = vals[1] if len(vals) > 1 else sx
                x, y = self._scale_point(x, y, sx, sy)

        return x, y

    def _apply_transform(self, x, y):
        x, y = self._transform_point(x, y, self.path_transform)
        x, y = self._transform_point(x, y, self.svg_transform)

        if not self.y_flip:
            y = self.svg_height - y

        return x, y

    def _transform_pt(self, x, y):
        return self._apply_transform(x, y)

    def _parse_path_to_pen(self, path_d, pen: Cu2QuPen):
        self.current_x = 0
        self.current_y = 0

        for command in self.PATH_REGEX.finditer(path_d):
            cmd = command.group(1)
            args = command.group(2).strip()
            coords = self._get_coords(args)
            absolute = cmd.isupper()

            if cmd in "Mm":
                self._move_to(pen, coords, absolute)
            elif cmd in "Ll":
                self._line_to(pen, coords, absolute)
            elif cmd in "Cc":
                self._cubic(pen, coords, absolute)
            elif cmd in "Zz":
                pen.closePath()

    def _get_coords(self, args):
        if not args:
            return []

        args = re.sub(r'[MLCZmlcz]', '', args)
        args = re.sub(r'(?<=\d)-', r' -', args)
        coords = [float(x) for x in re.split(r'[\s,]+', args.strip()) if x]
        return coords

    def _resolve_abs(self, x, y, absolute):
        if not absolute:
            x += self.current_x
            y += self.current_y
        return x, y

    def _move_to(self, pen, coords, absolute):
        it = iter(coords)
        x, y = next(it), next(it)
        x, y = self._resolve_abs(x, y, absolute)

        self.current_x, self.current_y = x, y
        tx, ty = self._transform_pt(x, y)

        pen.moveTo((tx, ty))

        for x, y in zip(it, it):
            x, y = self._resolve_abs(x, y, absolute)
            self.current_x, self.current_y = x, y
            pen.lineTo(self._transform_pt(x, y))

    def _line_to(self, pen, coords, absolute):
        it = iter(coords)
        while True:
            try:
                x = next(it)
                y = next(it)
            except StopIteration:
                break

            x, y = self._resolve_abs(x, y, absolute)
            self.current_x, self.current_y = x, y
            pen.lineTo(self._transform_pt(x, y))

    def _cubic(self, pen, coords, absolute):
        it = iter(coords)
        while True:
            try:
                c1x = next(it)
                c1y = next(it)
                c2x = next(it)
                c2y = next(it)
                ex = next(it)
                ey = next(it)
            except StopIteration:
                break

            c1x, c1y = self._resolve_abs(c1x, c1y, absolute)
            c2x, c2y = self._resolve_abs(c2x, c2y, absolute)
            ex, ey = self._resolve_abs(ex, ey, absolute)

            t1 = self._transform_pt(c1x, c1y)
            t2 = self._transform_pt(c2x, c2y)
            te = self._transform_pt(ex, ey)

            pen.curveTo(t1, t2, te)
            self.current_x, self.current_y = ex, ey
