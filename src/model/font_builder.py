import os

from fontTools.fontBuilder import FontBuilder as TTFontBuilder
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.pens.ttGlyphPen import TTGlyphPen

from .png_to_svg import PngToSvg
from .glyph_builder import GlyphBuilder
from .syllable_layout import (
    LEADING_CONSONANTS, VOWELS, TRAILING_CONSONANTS, JAMO_MAP,
    VOWEL_TYPE_VERTICAL_IDX, VOWEL_TYPE_HORIZONTAL_IDX, VOWEL_TYPE_MIXED_IDX
)


class FontBuilder:
    def __init__(self, image_dir: str, svg_dir: str, font_path: str, potrace_path: str,
                 font_name: str = "Font", upm: int = 1000, fixed_width: int = 1000,
                 step_call=None, subtask_call=None, progress_call=None):

        self.image_dir = image_dir
        self.svg_dir = svg_dir
        self.font_path = font_path
        self.font_name = font_name
        self.upm = upm
        self.fixed_width = fixed_width
        self.step_call = step_call if step_call else lambda msg: None
        self.subtask_call = subtask_call if subtask_call else lambda  num, tot, msg : None
        self.progress_call = progress_call if progress_call else lambda cur, tot : None

        self.png_converter = PngToSvg(potrace_path, subtask_call=subtask_call, progress_call=self.progress_call)
        self.glyph_builder = GlyphBuilder()

        self.fb = TTFontBuilder(unitsPerEm=self.upm, isTTF=True)
        self.font = self.fb.font

        self.glyphs = {}
        self.metrics = {}
        self.cmap_data = {}
        self.glyph_order = [".notdef"]

        self.x_min, self.y_min = float("inf"), float("inf")
        self.x_max, self.y_max = -float("inf"), -float("inf")

    def build_all(self):
        try:
            self.step_call(1,6,"PNG → SVG 변환")
            self.png_converter.convert_all(self.image_dir, self.svg_dir)
            self.subtask_call("PNG → SVG 변환 완료")

            self.step_call(2,6,"필수 글리프 생성")
            self._build_notdef_glyph()
            self._build_null_glyph()
            self._build_nonmarkingreturn_glyph()
            self.subtask_call("필수 글리프 생성 완료")

            self.step_call(3,6,"부품 글리프 빌드")
            self._build_base_glyphs()
            self.subtask_call("부품 글리프 빌드 완료")

            self.step_call(4,6,"음절 글리프 빌드")
            self._build_syllable_glyphs()
            self.subtask_call("음절 글리프 빌드 완료")

            self.step_call(5,6,"폰트 테이블 설정")
            all_glyphs = list(self.glyphs.keys())
            if ".notdef" in all_glyphs:
                all_glyphs.remove(".notdef")

            self.glyph_order = [".notdef"] + sorted(all_glyphs)
            self.subtask_call(f"{len(self.glyph_order)}개 글리프 설정")
            self.fb.setupGlyphOrder(self.glyph_order)
            self._fill_tables()
            self.subtask_call("폰트 테이블 설정 완료")

            self.step_call(6,6,"폰트 파일 저장")
            self._save_font()
            self.subtask_call("폰트 파일 저장 완료")

        except Exception as e:
            raise Exception(f"Font Build : {e}")

    def _build_notdef_glyph(self):
        pen = TTGlyphPen(None)
        width, height = 600, 800
        lsb = (self.fixed_width - width) // 2

        pen.moveTo((lsb, 0))
        pen.lineTo((lsb + width, 0))
        pen.lineTo((lsb + width, height))
        pen.lineTo((lsb, height))
        pen.closePath()

        margin = 50
        pen.moveTo((lsb + margin, margin))
        pen.lineTo((lsb + margin, height - margin))
        pen.lineTo((lsb + width - margin, height - margin))
        pen.lineTo((lsb + width - margin, margin))
        pen.closePath()

        self._add_glyph_to_font(".notdef", pen)

    def _build_null_glyph(self):
        pen = TTGlyphPen(None)
        self._add_glyph_to_font(".null", pen, advance_width=0)

    def _build_nonmarkingreturn_glyph(self):
        pen = TTGlyphPen(None)
        self._add_glyph_to_font("nonmarkingreturn", pen, advance_width=0)

    def _add_glyph_to_font(self, glyph_name: str, pen: TTGlyphPen,
                           advance_width: int = None):
        glyph = pen.glyph()
        self.glyphs[glyph_name] = glyph

        width = advance_width if advance_width is not None else self.fixed_width

        self.metrics[glyph_name] = (width, 0)

        if hasattr(glyph, 'xMin') and glyph.xMin is not None:
            self.x_min = min(self.x_min, glyph.xMin)
            self.y_min = min(self.y_min, glyph.yMin)
            self.x_max = max(self.x_max, glyph.xMax)
            self.y_max = max(self.y_max, glyph.yMax)

    def _load_svg_as_glyph(self, file_name: str, unicode_val: int = None):
        if unicode_val:
            glyph_name = f"uni{unicode_val:04X}"
        else:
            glyph_name = file_name

        if glyph_name in self.glyphs:
            return True

        svg_path = os.path.join(self.svg_dir, file_name + ".svg")

        if not os.path.exists(svg_path):
            if unicode_val:
                self.subtask_call(f"{file_name}.svg 파일 X → .notdef")
                self.cmap_data[unicode_val] = ".notdef"
            return False

        try:
            pen = self.glyph_builder.build_svg_to_glyph(svg_path)
            self._add_glyph_to_font(glyph_name, pen)

            if unicode_val:
                self.cmap_data[unicode_val] = glyph_name
            return True
        except Exception as e:
            if unicode_val:
                self.cmap_data[unicode_val] = ".notdef"
            return False

    def _build_base_glyphs(self):
        total_jamo = len(JAMO_MAP)
        total_l = len(LEADING_CONSONANTS) * 6
        total_v = len(VOWELS) * 2
        total_t = (len(TRAILING_CONSONANTS) - 1) * 3

        self.subtask_call(f"자모 빌드 (U+3131~U+3163)")
        jamo_count = 0

        for unicode_val, glyph_name in JAMO_MAP.items():
            if self._load_svg_as_glyph(glyph_name, unicode_val):
                jamo_count += 1
                self.progress_call(jamo_count, total_jamo)

        self.subtask_call(f"부품 빌드")

        l_count = 0
        for l_idx in range(len(LEADING_CONSONANTS)):
            for layout_type in range(1, 7):
                glyph_name = f"L_{l_idx}_type{layout_type}"
                if self._load_svg_as_glyph(glyph_name):
                    l_count += 1
                    self.progress_call(l_count, total_l, "[초성]")

        v_count = 0
        for v_idx in range(len(VOWELS)):
            types_to_build = []
            if v_idx in VOWEL_TYPE_VERTICAL_IDX:
                types_to_build = [1, 4]
            elif v_idx in VOWEL_TYPE_HORIZONTAL_IDX:
                types_to_build = [2, 5]
            elif v_idx in VOWEL_TYPE_MIXED_IDX:
                types_to_build = [3, 6]

            for layout_type in types_to_build:
                glyph_name = f"V_{v_idx}_type{layout_type}"
                if self._load_svg_as_glyph(glyph_name):
                    v_count += 1
                    self.progress_call(v_count, total_v, "[중성]")

        t_count = 0
        for t_idx in range(1, len(TRAILING_CONSONANTS)):
            for layout_type in range(4, 7):
                glyph_name = f"T_{t_idx}_type{layout_type}"
                if self._load_svg_as_glyph(glyph_name):
                    t_count += 1
                    self.progress_call(t_count, total_t, "[종성]")

    def _build_syllable_glyphs(self):
        BASE_CODE = 0xAC00
        TOTAL = 11172

        success_count = 0

        for i in range(TOTAL):
            char_code = BASE_CODE + i

            t_idx = i % 28
            v_idx = (i // 28) % 21
            l_idx = (i // 28) // 21

            layout_type = self._get_layout_type(v_idx, t_idx)

            l_name = f"L_{l_idx}_type{layout_type}"
            v_name = f"V_{v_idx}_type{layout_type}"
            t_name = f"T_{t_idx}_type{layout_type}" if t_idx > 0 else None

            if self._add_composite_glyph(char_code, l_name, v_name, t_name):
                success_count += 1

            if i % 50 == 0 or i == TOTAL - 1:
                current_char = chr(char_code)
                self.progress_call(i+1, TOTAL, f"음절({current_char})")

        self.subtask_call(f"{success_count}/{TOTAL}개 음절 생성")

    def _get_layout_type(self, v_idx, t_idx) -> int:
        if t_idx == 0:
            if v_idx in VOWEL_TYPE_HORIZONTAL_IDX:
                return 2
            if v_idx in VOWEL_TYPE_MIXED_IDX:
                return 3
            return 1
        else:
            if v_idx in VOWEL_TYPE_HORIZONTAL_IDX:
                return 5
            if v_idx in VOWEL_TYPE_MIXED_IDX:
                return 6
            return 4

    def _create_component(self, glyph_name, x, y, flags):
        comp = GlyphComponent()
        comp.glyphName = glyph_name
        comp.x = x
        comp.y = y
        comp.flags = flags
        return comp

    def _add_composite_glyph(self, char_code, l_name, v_name, t_name) -> bool:
        glyph_name = f"uni{char_code:04X}"

        if l_name not in self.glyphs or v_name not in self.glyphs:
            self.cmap_data[char_code] = ".notdef"
            return False

        if t_name and t_name not in self.glyphs:
            self.cmap_data[char_code] = ".notdef"
            return False

        glyph = Glyph()
        glyph.numberOfContours = -1
        glyph.components = []

        flags = 0x0004  #  0x0002

        glyph.components.append(
            self._create_component(l_name, 0, 0, flags)
        )

        glyph.components.append(
            self._create_component(v_name, 0, 0, flags)
        )

        if t_name:
            glyph.components.append(
                self._create_component(t_name, 0, 0, flags)
            )

        try:
            glyph.recalcBounds(self.glyphs)
        except Exception:
            pass

        self.glyphs[glyph_name] = glyph
        self.metrics[glyph_name] = (self.fixed_width, 0)
        self.cmap_data[char_code] = glyph_name

        return True


    def _fill_tables(self):
        self.fb.setupGlyf(self.glyphs)
        self.fb.setupHorizontalMetrics(self.metrics)
        self.fb.setupCharacterMap(self.cmap_data)

        xMin = int(self.x_min) if self.x_min != float("inf") else 0
        yMin = int(self.y_min) if self.y_min != float("inf") else 0
        xMax = int(self.x_max) if self.x_max != -float("inf") else self.fixed_width
        yMax = int(self.y_max) if self.y_max != -float("inf") else 800

        # head 테이블
        self.fb.setupHead(
            unitsPerEm=self.upm,
            # xMin=xMin,
            # yMin=yMin,
            # xMax=xMax,
            # yMax=yMax,
            xMin=-100,
            yMin=-200,
            xMax = self.fixed_width + 100,
            yMax = 1400,
            indexToLocFormat=1
        )

        # hhea 테이블
        self.fb.setupHorizontalHeader(
            ascent=1300,
            descent=-500,
            lineGap=0,
            numberOfHMetrics=len(self.glyph_order),
            advanceWidthMax = self.fixed_width,
            xMaxExtent = self.fixed_width
        )

        # maxp 테이블
        self.fb.setupMaxp()

        # name 테이블
        self.fb.setupNameTable({
            1: self.font_name,
            2: "Regular",
            3: f"{self.font_name}-Regular; Version 1.0",
            4: f"{self.font_name}-Regular",
            5: "Version 1.0",
            6: self.font_name.replace(" ", "-")
        })

        # OS/2 테이블
        self.fb.setupOS2(
            version=4,
            usWeightClass=400,
            usWidthClass=5,
            fsType=0,
            sTypoAscender=800,
            sTypoDescender=-200,
            sTypoLineGap=200,
            usWinAscent=1300,
            usWinDescent=500,
            ulUnicodeRange1=(1 << 0) | (1 << 17),  # Basic Latin + Hangul Jamo
            ulUnicodeRange2=(1 << 28),  # Hangul Syllables
            ulUnicodeRange3=0,
            ulUnicodeRange4=0,
            ulCodePageRange1 = (1<<0) | (1<<19) | (1<<20),
            ulCodePageRange2 = 0,
            achVendID="HYEJ",
            fsSelection=(1 << 6) | (1 << 7),
            usFirstCharIndex=min(self.cmap_data.keys()) if self.cmap_data else 0,
            usLastCharIndex=max(self.cmap_data.keys()) if self.cmap_data else 0
        )

        # post 테이블
        self.fb.setupPost(
            isFixedPitch=1,
            underlinePosition=-75,
            underlineThickness=50
        )

    def _save_font(self):
        os.makedirs(os.path.dirname(self.font_path), exist_ok=True)
        self.fb.save(self.font_path)

        # self.subtask_call(f"파일 경로: {os.path.abspath(self.font_path)}")
        # self.subtask_call(f"파일 크기: {os.path.getsize(self.font_path) / 1024:.1f} KB")
