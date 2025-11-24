# ImgToFont
이미지를 이용해 한글 11,172자를 포함하는 TTF 폰트를 생성하는 Python 기반 폰트 제작 프로그램

---
## 1. 개요
해당 프로그램은 PNG -> SVG -> TTF 를 기반으로<br>
한글(U+AC00-U+D7A3)의 모든 11,172개 음절과 자모(U+3131-)를 자동 조합하여 TTF 폰트를 생성한다.<br>
규칙에 맞게 준비된 PNG 파일을 이용하여 누구나 자신만의 폰트를 생성할 수 있다.

<br>

## 2. 데이터 규칙
### 기본
| 항목 | 내용 |
|------|------|
| 형식 | PNG |
| 캔버스 | 1000 x 1000px |
| 글자색 | 검정(#000) |

### 파일 명명
> `{종류}_{인덱스}_{타입}.png`

#### 종류
* 초성 : L
* 중성 : V
* 종성 : T

#### 인덱스
한글 분해 인덱스
* 초성: 0-18
    | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
    |---|---|---|---|---|---|---|---|
    | ㄱ | ㄲ | ㄴ | ㄷ | ㄸ | ㄹ | ㅁ | ㅂ |   

    | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
    |---|---|----|----|----|----|----|----|
    | ㅃ | ㅅ | ㅆ | ㅇ | ㅈ | ㅉ | ㅊ | ㅋ |    

    | 16 | 17 | 18 |
    |----|----|----|
    | ㅌ | ㅍ | ㅎ |
    
* 중성: 0-20
    | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
    |---|---|---|---|---|---|---|---|
    | ㅏ | ㅐ | ㅑ | ㅒ | ㅓ | ㅔ | ㅕ | ㅖ |
  
    | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
    |---|---|----|----|----|----|----|----|
    | ㅗ | ㅘ | ㅙ | ㅚ | ㅛ | ㅜ | ㅝ | ㅞ |
  
    | 16 | 17 | 18 | 19 | 20 |
    |----|----|----|----|----|
    | ㅟ | ㅠ | ㅡ | ㅢ | ㅣ |
    
* 종성: 0, 1-27
    | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
    |---|---|---|---|---|---|---|---|
    | (없음) | ㄱ | ㄲ | ㄳ | ㄴ | ㄵ | ㄶ | ㄷ |
  
    | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
    |---|---|----|----|-----|-----|-----|-----|
    | ㄹ | ㄺ | ㄻ | ㄼ | ㄽ | ㄾ | ㄿ | ㅀ |
  
    | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
    |----|----|----|----|----|----|----|----|
    | ㅁ | ㅂ | ㅄ | ㅅ | ㅆ | ㅇ | ㅈ | ㅊ |
  
    | 24 | 25 | 26 | 27 |
    |----|----|----|----|
    | ㅋ | ㅌ | ㅍ | ㅎ |    

#### 타입
글자 조합의 레이아웃 유형 (총 7가지)

| 타입 | 구조 | 예시 | 예시위치 |
|------|------|------|------|
| jamo | 한글 자모 (초성 및 중성) | ㄱ, ㄴ | <img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/425d394e-fd9a-4b99-8a8f-904ce603085e" /> |
| type1 | 초성 + 중성(세로 모음) | 가, 나 | <img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/2ca92691-d64d-4103-a1dc-4aee9e3a95eb" /> | 
| type2 | 초성 + 중성(가로 모음) | 고, 노 | <img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/050d9458-c906-4b24-9640-bc0fda0f819c" /> |
| type3 | 초성 + 중성(복합 모음) | 과, 괘 | <img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/118b15b5-02d5-473c-a7a4-ee475a762319" /> |
| type4 | 초성 + 중성(세로 모음) + 종성 | 각, 객 | <img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/1d068869-d5d9-4f6b-81e3-0ca04c5ab4ff" /> |
| type5 | 초성 + 중성(가로 모음) + 종성 | 곡, 극 | <img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/bec668df-73f5-4ecf-9e18-5ce288a2148a" /> |
| type6 | 초성 + 중성(복합 모음) + 종성 | 곽, 괙 | <img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/56c2afc8-87b1-4d33-aac2-b95f6567321a" /> |

```
세로 모음 (ㅏ, ㅐ, ㅑ, ㅒ, ㅓ, ㅔ, ㅕ, ㅖ, ㅣ)
가로 모음 (ㅗ, ㅛ, ㅜ, ㅠ, ㅡ)
복합 모음 (ㅘ, ㅙ, ㅚ, ㅝ, ㅞ, ㅟ, ㅢ)
```
<br>
    
## 3. 프로그램 사용
### ! 주의
> 해당 프로그램은 [potrace]를 사용하여 구현하였습니다.<br>
> 윈도우 사용자는 'potrace.exe'를 직접 다운로드하여 루트 폴더에 넣어주세요.
>  1. [potrace 공식 다운로드 페이지](http://potrace.sourceforge.net/#downloading) 접속
>  2. Windows - zip 파일 다운로드
>  3. zip 파일의 압축을 풀고 potrace.exe 파일을 루트 폴더에 복사

### USAGE
`python src/main.py [-h] [-i IMAGE_DIR] [-s SVG_DIR] [-o FONT_PATH] [-n FONT_NAME]`

| 옵션 | 설명 | Default |
|------|------|------|
| -i or --input IMAGE_DIR | PNG 이미지 폴더 경로 | ImgToFont/image/png/ |
| -s or --svg SVG_DIR | SVG 저장 폴더 경로 | ImgToFont/image/svg/ | 
| -o or --output FONT_PATH | 생성될 폰트 파일 경로 | ImgToFont/font/Font.ttf |
| -n or --name FONT_NAME | 폰트 패밀리 이름 | Font |

<br>

## 4. 프로그램 설계
### 기능
타입에 따른 초성, 중성, 종성을 그린 이미지로 각 한글 음절을 조합하여 한글 폰트 파일을 생성한다. 
- [x] 한글 자모, 음절 규칙 정의
- [x] PNG -> SVG 변환 기능
- [x] 글리프 생성 기능
- [x] 폰트 파일 생성 기능
- [x] 기본 데이터 구축

### 입출력
#### 입력
- [x] PNG 폴더 경로
- [x] SVG 폴더 경로
- [x] Font 경로
- [x] Font 이름 지정

#### 출력
- [x] 폰트 빌드 단계별 진행 상황 출력
- [x] 예외 상황 시 에러 문구를 출력

### 예외 처리
- [x] 폰트 빌드 오류 출력
- [x] 글리프 빌드 오류 출력
- [x] PNG -> SVG 변환 오류 출력

<br>

## 5. 결과
<img width="300" alt="Image" src="https://github.com/user-attachments/assets/51fa918c-2b43-45a8-b8b7-8eb8f5a9585c" />
<br>

> <img width="600" alt="Image" src="https://github.com/user-attachments/assets/28424756-0b16-4d2b-a7ff-04bb4ec1a9dc" />
