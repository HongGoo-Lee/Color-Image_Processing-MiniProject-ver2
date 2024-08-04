import os.path
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import *
import math
from tkinter.simpledialog import *
from PIL import Image   #필로우 라이브러리 중 Image 객체를 사용

## 함수선언
#####################################################################################################################################################
# 공통 함수
def OnMalloc3D(t, h, w, initValue=0):
    memory = None
    memory = [[[initValue for _ in range(w)] for _ in range(h)] for _ in range(t)]
    return memory

def OnOpenDocument():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    global sx, sy, ex, ey, mouseYN
    sx = sy = ex = ey = -1
    mouseYN.set(False)
    fileName = askopenfilename(parent=window, filetypes=(('컬러이미지', '*.png;*.jpg;*.bpm,*.tif'), ("모든 파일", "*.*")))
    ## 파일 크기 확인 + (중요)입력 영상 높이,폭 계산
    pillow = Image.open(fileName)   # 필로우 객체로 읽기
    m_oriH = pillow.height
    m_oriW = pillow.width

    ## 메모리 할당
    m_oriImage = OnMalloc3D(RGB, m_oriH, m_oriW)

    # 파일에서 메모리로 로딩
    pillowRGB = pillow.convert('RGB')   # RGB 모델로 변경
    for i in range(m_oriH):
        for j in range(m_oriW):
            r,g,b = pillowRGB.getpixel((j,i))
            m_oriImage[RR][i][j] = r
            m_oriImage[GG][i][j] = g
            m_oriImage[BB][i][j] = b

    ## equalImage() 호출
    equalImage()

def OnSaveDocument():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    if m_tarImage == None:
        return
    wfp = asksaveasfile(parent=window, mode="wb", defaultextension='*.png',
                        filetypes=(('png파일', '*.png'), ("모든 파일", "*.*")))

    pillow = Image.new('RGB',(m_tarW,m_tarH)) # 빈 필로우 객체 생성
    for i in range(m_tarH):
        for j in range(m_tarW):
            r = m_tarImage[RR][i][j]
            g = m_tarImage[GG][i][j]
            b = m_tarImage[BB][i][j]
            pillow.putpixel((j, i), (r, g, b))
    pillow.save(wfp.name)
    messagebox.showinfo('성공', wfp.name + '로 저장됨')

def OnDraw():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW, hop
    # 몰라 일단 설정
    MAXSIZE = 512
    tarH = m_tarH
    tarW = m_tarW
    hop = 1
    if (tarH > MAXSIZE or tarW > MAXSIZE):
        # hop을 계산.
        if (tarW > tarH):
            hop = tarH // MAXSIZE
        else:
            hop = tarH // MAXSIZE

        tarH = tarH // hop
        tarW = tarW // hop

    ## 기존의 파일을 연 적이 있다 == 캔버스가 이미 붙어있다
    if canvas != None:
        canvas.destroy()
    # 벽, 캔버스, 종이 설정
    window.geometry(str(tarW) + 'x' + str(tarH))
    canvas = Canvas(window, height=tarH, width=tarW, bg='gray')
    OnBindMouse()  # 새로운 캔버스에 마우스 바인드하기
    paper = PhotoImage(height=tarH, width=tarW)  # 종이
    canvas.create_image((tarW // 2, tarH // 2), image=paper, state='normal')



    # ## 메모리 --> 화면
    ## 더블 버퍼링 기법 적용 (모두 메모리에 load하고 한방에 종이에 붙이기)
    rgbString = ""  # 전체에 대한 16진수 문자열
    for i in range(tarH):
        oneLineStr = ""  # 1줄에 대한 16진수 문자열
        for j in range(tarW):
            r = m_tarImage[RR][i*hop][j*hop]
            g = m_tarImage[GG][i*hop][j*hop]
            b = m_tarImage[BB][i*hop][j*hop]
            oneLineStr += '#%02x%02x%02x ' % (r, g, b)
        rgbString += '{' + oneLineStr + '} '
    paper.put(rgbString)
    canvas.pack()
    # 상태바 변경
    fnames = fileName.split('/')
    sbar.config(text=str(m_tarW)+'x'+str(m_tarH)+' '+fnames[-1])

def OnBindMouse():
    global sx, sy, ex, ey
    sx = sy = ex = ey = -1
    if mouseYN.get():
        canvas.bind('<Button-1>', leftClick)  # 마우스 왼쪽 버튼을 클릭했을때
        canvas.bind('<B1-Motion>', leftDrag)  # 마우스 왼쪽 버튼을 클릭하고 드래그했을떄
        canvas.bind('<ButtonRelease-1>', leftDrop)  # 마우스 왼쪽 버튼을 뗐을떄
    else:
        canvas.unbind('<Button-1>')  # 마우스 왼쪽 버튼을 클릭했을때
        canvas.unbind('<B1-Motion>')  # 마우스 왼쪽 버튼을 클릭하고 드래그했을떄
        canvas.unbind('<ButtonRelease-1>')  # 마우스 왼쪽 버튼을 뗐을떄

def leftClick(event):
    global sx, sy, ex, ey, boxLine, hop
    if boxLine != None:
        canvas.delete(boxLine)
    sx = event.x * hop
    sy = event.y * hop

def leftDrag(event):
    global sx, sy, ex, ey, boxLine, hop
    ex = event.x*hop
    ey = event.y*hop
    if boxLine != None:
        canvas.delete(boxLine)
    boxLine = canvas.create_rectangle(sx//hop, sy//hop, ex//hop, ey//hop, width=1)

def leftDrop(event):
    global sx, sy, ex, ey, boxLine, hop
    ex = event.x*hop
    ey = event.y*hop
    if sx > ex:
        sx, ex = ex, sx
    if sy > ey:
        sy, ey = ey, sy
    if boxLine != None:
        canvas.delete(boxLine)
    boxLine = canvas.create_rectangle(sx//hop, sy//hop, ex//hop, ey//hop, width=1)

#####################################################################################################################################################
# 영상처리 함수

########################################################
# 화소점 처리 함수
def equalImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)
    # 진짜 영상처리
    for rgb in range(RGB):
        for i in range(m_oriH):
            for j in range(m_oriW):
                m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]
    ######################
    OnDraw()

def grayScaleImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    global sx, sy, ex, ey, boxLine
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)
    # 진짜 영상처리
    if sx == -1:    # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW-1
        ey = m_tarH-1
    for i in range(m_oriH):
        for j in range(m_oriW):
            if sx <= j <= ex and sy <= i <= ey: # 영상 처리할 좌표
                value = m_oriImage[RR][i][j] + m_oriImage[GG][i][j] + m_oriImage[BB][i][j]
                m_tarImage[RR][i][j] = m_tarImage[GG][i][j] = m_tarImage[BB][i][j] = value//3
            else:
                m_tarImage[RR][i][j] = m_oriImage[RR][i][j]
                m_tarImage[GG][i][j] = m_oriImage[GG][i][j]
                m_tarImage[BB][i][j] = m_oriImage[BB][i][j]

    ######################
    OnDraw()

def addImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    global sx,sy,ex,ey
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)
    # 진짜 영상처리
    if sx == -1:    # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW-1
        ey = m_tarH-1
    value = askinteger('밝게/어둡게', '값', minvalue=-255, maxvalue=255)
    for i in range(m_oriH):
        for j in range(m_oriW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    if m_oriImage[rgb][i][j] + value > 255:
                        m_tarImage[rgb][i][j] = 255
                    elif m_oriImage[rgb][i][j] + value < 0:
                        m_tarImage[rgb][i][j] = 0
                    else:
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j] + value
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()

def reverseImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)
    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:    # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW-1
        ey = m_tarH-1
    for i in range(m_oriH):
        for j in range(m_oriW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    m_tarImage[rgb][i][j] = 255 - m_oriImage[rgb][i][j]
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()

def bwImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)
    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW - 1
        ey = m_tarH - 1
    for i in range(m_oriH):
        for j in range(m_oriW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    if m_oriImage[rgb][i][j] > 127:
                        m_tarImage[rgb][i][j] = 255
                    else:
                        m_tarImage[rgb][i][j] = 0
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()

def gammaImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)
    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW - 1
        ey = m_tarH - 1
    gamma = askfloat('감마보정', '값')
    for i in range(m_oriH):
        for j in range(m_oriW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    if m_oriImage[rgb][i][j] ** (1.0 / gamma) > 255:
                        m_tarImage[rgb][i][j] = 255
                    elif m_oriImage[rgb][i][j] ** (1.0 / gamma) < 0:
                        m_tarImage[rgb][i][j] = 0
                    else:
                        m_tarImage[rgb][i][j] = int(m_oriImage[rgb][i][j] ** (1.0 / gamma))
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]
    ######################
    OnDraw()

def andImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)
    # 진짜 영상처리
    global sx, sy, ex, ey
    for i in range(m_oriH):
        for j in range(m_oriW):
            for rgb in range(RGB):
                if sx == -1:
                    if m_tarH / 4 < i < m_tarH / 4 * 3 and m_tarW / 4 < j < m_tarW / 4 * 3:
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j] & 255
                    else:
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j] & 0
                else:
                    if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j] & 255
                    else:
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j] & 0

    ######################
    OnDraw()

def orImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)
    # 진짜 영상처리
    for i in range(m_oriH):
        for j in range(m_oriW):
            for rgb in range(RGB):
                if sx == -1:
                    if m_tarH / 4 < i < m_tarH / 4 * 3 and m_tarW / 4 < j < m_tarW / 4 * 3:
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j] | 255
                    else:
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j] | 0
                else:
                    if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j] | 255
                    else:
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j] | 0
    ######################
    OnDraw()

def posterImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)
    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    sector = askinteger('포스터라이징', '나눌 구간의 수')
    value = int(255 / (sector - 1))  # 값
    sector_size = int(255 / sector)  # 구간별 범위
    for i in range(m_tarH):
        for j in range(m_tarW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    val = int(value * int(m_oriImage[rgb][i][j] / sector_size))
                    if val > 255:
                        val = 255
                    elif val < 0:
                        val = 0
                    m_tarImage[rgb][i][j] = val
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()

def rangeImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)

    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    range1 = askinteger('범위강조', '시작 범위')
    range2 = askinteger('범위강조', '끝 범위')
    for i in range(m_tarH):
        for j in range(m_tarW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    if range1 <= m_oriImage[rgb][i][j] <= range2:
                        m_tarImage[rgb][i][j] = 255
                    else:
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()

def parabolaImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)

    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    for i in range(m_tarH):
        for j in range(m_tarW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    v = int(255 - 255 * (m_oriImage[rgb][i][j] / 127-1) ** 2)
                    if v > 255:
                        m_tarImage[rgb][i][j] = 255
                    elif v < 0:
                        m_tarImage[rgb][i][j] = 0
                    else:
                        m_tarImage[rgb][i][j] = v
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()


###############################################################
## 기하학 처리 함수
def zoomInImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    scale = askinteger('확대', '값')
    m_tarH = m_oriH * scale;
    m_tarW = m_oriW * scale;
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)

    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    for i in range(m_tarH):
        for j in range(m_tarW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i // scale][j // scale]
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()

def zoomOutImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    scale = askinteger('축소', '값')
    m_tarH = m_oriH // scale
    m_tarW = m_oriW // scale
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)

    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    for i in range(m_tarH):
        for j in range(m_tarW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i * scale][j * scale]
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]
    # for i in range(m_oriH, scale):
    #     for j in range(m_oriW, scale):
    #         hap = 0
    #         for m in range(scale):
    #             for n in range(scale):
    #                 hap += m_oriImage[i + m][j + n]
    #         m_tarImage[int(i / scale)][int(j / scale)] = int(hap / (scale * scale))
    ######################
    OnDraw()

def moveImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    x = askinteger('이동', '이동할 값(x축)')
    y = askinteger('이동', '이동할 값(y축)')
    m_tarH = m_oriH;
    m_tarW = m_oriW;
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)

    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    for i in range(m_tarH):
        for j in range(m_tarW):
            h = i + y
            w = j + x
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    if 0 <= i - y < m_oriH and 0 <= j - x < m_oriW:
                        m_tarImage[rgb][i][j] = m_oriImage[rgb][i - y][j - x]
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()

def rotateImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    angle = askinteger('회전', '회전할 값')

    radian = angle * 3.141592 / 180.0
    temp = (90 - angle) * 3.141592 / 180.0
    m_tarH = abs(int(m_oriH * math.cos(radian))) + abs(int(m_oriW * math.cos(temp)))
    m_tarW = abs(int(m_oriH * math.cos(temp))) + abs(int(m_oriW * math.cos(radian)))
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)
    tarCx = m_tarH / 2
    tarCy = m_tarW / 2
    oriCx = m_oriH / 2
    oriCy = m_oriW / 2
    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    for i in range(m_tarH):
        for j in range(m_tarW):
            tarX = i
            tarY = j
            oriX = int(math.cos(radian) * (tarX - tarCx) + math.sin(radian) * (tarY - tarCy) + oriCx)
            oriY = int(-math.sin(radian) * (tarX - tarCx) + math.cos(radian) * (tarY - tarCy) + oriCy)
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    if 0 <= oriX < m_oriH and 0 <= oriY < m_oriW:
                        m_tarImage[rgb][tarX][tarY] = m_oriImage[rgb][oriX][oriY]
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()

def mirroringImage1():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH;
    m_tarW = m_oriW;
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)

    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    for i in range(m_tarH):
        for j in range(m_tarW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][m_oriH - 1 - i][j]
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]
    ######################
    OnDraw()

def mirroringImage2():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH;
    m_tarW = m_oriW;
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)

    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    for i in range(m_tarH):
        for j in range(m_tarW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][m_oriW - 1 - j]
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()


########################################################
# 히스토그램 처리 함수
def stretchImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)

    low = [m_oriImage[0][0][0], m_oriImage[1][0][0], m_oriImage[2][0][0]]
    high = [m_oriImage[0][0][0], m_oriImage[1][0][0], m_oriImage[2][0][0]]
    for i in range(1, m_tarH):
        for j in range(1, m_tarW):
            for rgb in range(RGB):
                if low[rgb] > m_oriImage[rgb][i][j]:
                    low[rgb] = m_oriImage[rgb][i][j]
                elif high[rgb] < m_oriImage[rgb][i][j]:
                    high[rgb] = m_oriImage[rgb][i][j]
    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    for i in range(m_tarH):
        for j in range(m_tarW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    newVal = float(m_oriImage[rgb][i][j] - low[rgb]) / (high[rgb] - low[rgb]) * 255.0
                    if (newVal < 0.0):
                        newVal = 0
                    if (newVal > 255.0):
                        newVal = 255
                    m_tarImage[rgb][i][j] = int(newVal)
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()

def endInImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB,m_tarH, m_tarW)

    low = [m_oriImage[0][0][0], m_oriImage[1][0][0], m_oriImage[2][0][0]]
    high = [m_oriImage[0][0][0], m_oriImage[1][0][0], m_oriImage[2][0][0]]
    for i in range(1, m_tarH):
        for j in range(1, m_tarW):
            for rgb in range(RGB):
                if low[rgb] > m_oriImage[rgb][i][j]:
                    low[rgb] = m_oriImage[rgb][i][j]
                elif high[rgb] < m_oriImage[rgb][i][j]:
                    high[rgb] = m_oriImage[rgb][i][j]
    for rgb in range(RGB):
        low[rgb] += 50
        high[rgb] -= 50

    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    for i in range(m_tarH):
        for j in range(m_tarW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    newVal = float(m_oriImage[rgb][i][j] - low[rgb]) / (high[rgb] - low[rgb]) * 255.0
                    if (newVal < 0.0):
                        newVal = 0
                    if (newVal > 255.0):
                        newVal = 255
                    m_tarImage[rgb][i][j] = int(newVal)
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]

    ######################
    OnDraw()

def histoEqual():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)

    hist = [[0 for _ in range(256)] for _ in range(RGB)]
    hap = [[0 for _ in range(256)] for _ in range(RGB)]
    n = [[0 for _ in range(256)] for _ in range(RGB)]
    # 진짜 영상처리
    global sx, sy, ex, ey
    if sx == -1:  # 마우스 클릭을 안했을 때
        sx = sy = 0
        ex = m_tarW
        ey = m_tarH
    # 1단계
    for i in range(m_oriH):
        for j in range(m_oriW):
            for rgb in range(RGB):
                hist[rgb][m_oriImage[rgb][i][j]] += 1

    # 2단계
    for i in range(256):
        for rgb in range(RGB):
            hap[rgb][i] = hist[rgb][i]
            if i != 0:
                hap[rgb][i] += hap[rgb][i-1]

            # 3단계
            n[rgb][i] = int(hap[rgb][i]*(1/(m_oriH * m_oriW))*255)

    for i in range(m_tarH):
        for j in range(m_tarW):
            for rgb in range(RGB):
                if sx <= j <= ex and sy <= i <= ey:  # 영상 처리할 좌표
                    m_tarImage[rgb][i][j] = n[rgb][m_oriImage[rgb][i][j]]
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]
    ######################
    OnDraw()


########################################################
# 화소영역 처리 함수
def embossRGBImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    global sx, sy, ex, ey, boxLine
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)

    # 진짜 영상처리
    MSIZE = 3
    mask = [[-1, 0, 0],
            [ 0, 0, 0],
            [ 0, 0, 1]]
    ## 임시 메모리 확보
    tempOriImage = OnMalloc3D(RGB,m_oriH+2,m_oriW+2,127.0)
    tempTarImage = OnMalloc3D(RGB, m_oriH + 2, m_oriW + 2, 0.0)
    for rgb in range(RGB):
        for i in range(m_oriH):
            for j in range(m_oriW):
                tempOriImage[rgb][i+1][j+1] = m_oriImage[rgb][i][j]
    ## 회선 연산
    for rgb in range(RGB):
        for i in range(m_oriH):
            for j in range(m_oriW):
                S = 0.0
                for m in range(MSIZE):
                    for n in range(MSIZE):
                        S += tempOriImage[rgb][i+m][j+n] * mask[m][n]
                tempTarImage[rgb][i][j] = S
    ## 후처리 및 임시 결과 --> 결과
    if sx == -1:
        sx = sy = 0
        ex = m_tarW-1
        ey = m_tarH-1

    for rgb in range(RGB):
        for i in range(m_tarH):
            for j in range(m_tarW):
                if sx <= j <= ex and sy <= i <= ey:
                    tempTarImage[rgb][i][j] += 127
                    v = int(tempTarImage[rgb][i][j])
                    if v > 255:
                        m_tarImage[rgb][i][j] = 255
                    elif v < 0:
                        m_tarImage[rgb][i][j] = 0
                    else:
                        m_tarImage[rgb][i][j] = v
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]
    ######################
    OnDraw()

import colorsys
def embossHSVImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    global sx, sy, ex, ey, boxLine
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)

    ## RGB --> HSI
    oriImageHSV = OnMalloc3D(RGB,m_oriH,m_oriW,0.0)
    ## RGB --> HSV 변환 입력
    for i in range(m_oriH):
        for j in range(m_oriW):
            r, g, b = m_oriImage[RR][i][j], m_oriImage[GG][i][j], m_oriImage[BB][i][j]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            oriImageHSV[0][i][j], oriImageHSV[1][i][j], oriImageHSV[2][i][j] = h, s, v

    # 진짜 영상처리
    MSIZE = 3
    mask = [[-1, 0, 0],
            [0, 0, 0],
            [0, 0, 1]]
    ## 임시 메모리 확보
    tempOriImageHSV = OnMalloc3D(RGB, m_oriH + 2, m_oriW + 2)
    tempTarImageHSV = OnMalloc3D(RGB, m_oriH + 2, m_oriW + 2, 0)
    for rgb in range(RGB):
        for i in range(m_oriH):
            for j in range(m_oriW):
                tempOriImageHSV[rgb][i + 1][j + 1] = oriImageHSV[rgb][i][j]
    ## 회선 연산
    for i in range(m_oriH):
        for j in range(m_oriW):
            S = 0.0
            for m in range(MSIZE):
                for n in range(MSIZE):
                    S += tempOriImageHSV[2][i + m][j + n] * mask[m][n]
            tempTarImageHSV[2][i][j] = S
            tempTarImageHSV[1][i][j] = tempOriImageHSV[1][i][j]
            tempTarImageHSV[0][i][j] = tempOriImageHSV[0][i][j]

    ## 후처리 및 임시 결과 --> 결과
    if sx == -1:
        sx = sy = 0
        ex = m_tarW - 1
        ey = m_tarH - 1

    for i in range(m_tarH):
        for j in range(m_tarW):
            if sx <= j <= ex and sy <= i <= ey:
                # 후처리
                tempTarImageHSV[2][i][j] += 127.0
                # h,s,v값 찾기
                h = tempTarImageHSV[0][i][j]
                s = tempTarImageHSV[1][i][j]
                v = tempTarImageHSV[2][i][j]
                # 오버플로우 체크
                if v > 255:
                    v = 255
                elif v < 0:
                    v = 0
                # rgb 변환
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                # 알맞은값 넣기
                m_tarImage[RR][i][j], m_tarImage[GG][i][j], m_tarImage[BB][i][j] = int(r), int(g), int(b)
            else:
                for rgb in range(RGB):
                    m_tarImage[rgb][i][j] = int(m_oriImage[rgb][i][j])
    ######################
    OnDraw()

def blurrImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    global sx, sy, ex, ey, boxLine
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)
    # 진짜 영상처리
    MSIZE = 5

    mask = [[1/(MSIZE**2) for _ in range(MSIZE)] for _ in range(MSIZE)]
    ## 임시 메모리 확보
    tempOriImage = OnMalloc3D(RGB, m_oriH + MSIZE-1, m_oriW + MSIZE-1, 127.0)
    tempTarImage = OnMalloc3D(RGB, m_oriH + MSIZE-1, m_oriW + MSIZE-1, 0.0)
    for rgb in range(RGB):
        for i in range(m_oriH):
            for j in range(m_oriW):
                tempOriImage[rgb][i + 1][j + 1] = m_oriImage[rgb][i][j]
    ## 회선 연산
    for rgb in range(RGB):
        for i in range(m_oriH):
            for j in range(m_oriW):
                S = 0.0
                for m in range(MSIZE):
                    for n in range(MSIZE):
                        S += tempOriImage[rgb][i + m][j + n] * mask[m][n]
                tempTarImage[rgb][i][j] = S
    ## 후처리 및 임시 결과 --> 결과
    if sx == -1:
        sx = sy = 0
        ex = m_tarW - 1
        ey = m_tarH - 1

    for rgb in range(RGB):
        for i in range(m_tarH):
            for j in range(m_tarW):
                if sx <= j <= ex and sy <= i <= ey:
                    v = int(tempTarImage[rgb][i][j])
                    if v > 255:
                        m_tarImage[rgb][i][j] = 255
                    elif v < 0:
                        m_tarImage[rgb][i][j] = 0
                    else:
                        m_tarImage[rgb][i][j] = v
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]
    ######################
    OnDraw()

def sharpImage():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    global sx, sy, ex, ey, boxLine
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)
    # 진짜 영상처리
    MSIZE = 3
    mask = [[ 0.0, -1.0,  0.0],
            [-1.0,  5.0, -1.0],
            [ 0.0, -1.0,  0.0 ]]
    ## 임시 메모리 확보
    tempOriImage = OnMalloc3D(RGB, m_oriH + 2, m_oriW + 2, 127.0)
    tempTarImage = OnMalloc3D(RGB, m_oriH + 2, m_oriW + 2, 0.0)
    for rgb in range(RGB):
        for i in range(m_oriH):
            for j in range(m_oriW):
                tempOriImage[rgb][i + 1][j + 1] = m_oriImage[rgb][i][j]
    ## 회선 연산
    for rgb in range(RGB):
        for i in range(m_oriH):
            for j in range(m_oriW):
                S = 0.0
                for m in range(MSIZE):
                    for n in range(MSIZE):
                        S += tempOriImage[rgb][i + m][j + n] * mask[m][n]
                tempTarImage[rgb][i][j] = S
    ## 후처리 및 임시 결과 --> 결과
    if sx == -1:
        sx = sy = 0
        ex = m_tarW - 1
        ey = m_tarH - 1

    for rgb in range(RGB):
        for i in range(m_tarH):
            for j in range(m_tarW):
                if sx <= j <= ex and sy <= i <= ey:
                    v = int(tempTarImage[rgb][i][j])
                    if v > 255:
                        m_tarImage[rgb][i][j] = 255
                    elif v < 0:
                        m_tarImage[rgb][i][j] = 0
                    else:
                        m_tarImage[rgb][i][j] = v
                else:
                    m_tarImage[rgb][i][j] = m_oriImage[rgb][i][j]
    ######################
    OnDraw()

def edgeImage1():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    global sx, sy, ex, ey, boxLine
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)

    ## RGB --> HSI
    oriImageHSV = OnMalloc3D(RGB, m_oriH, m_oriW, 0.0)
    ## RGB --> HSV 변환 입력
    for i in range(m_oriH):
        for j in range(m_oriW):
            r, g, b = m_oriImage[RR][i][j], m_oriImage[GG][i][j], m_oriImage[BB][i][j]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            oriImageHSV[0][i][j], oriImageHSV[1][i][j], oriImageHSV[2][i][j] = h, s, v

    # 진짜 영상처리
    MSIZE = 3
    mask = [[0, 0, 0],
            [-1, 1, 0],
            [0, 0, 0]]
    ## 임시 메모리 확보
    tempOriImageHSV = OnMalloc3D(RGB, m_oriH + 2, m_oriW + 2)
    tempTarImageHSV = OnMalloc3D(RGB, m_oriH + 2, m_oriW + 2, 0)
    for rgb in range(RGB):
        for i in range(m_oriH):
            for j in range(m_oriW):
                tempOriImageHSV[rgb][i + 1][j + 1] = oriImageHSV[rgb][i][j]
    ## 회선 연산
    for i in range(m_oriH):
        for j in range(m_oriW):
            S = 0.0
            for m in range(MSIZE):
                for n in range(MSIZE):
                    S += tempOriImageHSV[2][i + m][j + n] * mask[m][n]
            tempTarImageHSV[2][i][j] = S
            tempTarImageHSV[1][i][j] = tempOriImageHSV[1][i][j]
            tempTarImageHSV[0][i][j] = tempOriImageHSV[0][i][j]

    ## 후처리 및 임시 결과 --> 결과
    if sx == -1:
        sx = sy = 0
        ex = m_tarW - 1
        ey = m_tarH - 1

    for i in range(m_tarH):
        for j in range(m_tarW):
            if sx <= j <= ex and sy <= i <= ey:
                # 후처리
                tempTarImageHSV[2][i][j] += 127.0
                # h,s,v값 찾기
                h = tempTarImageHSV[0][i][j]
                s = tempTarImageHSV[1][i][j]
                v = tempTarImageHSV[2][i][j]
                # 오버플로우 체크
                if v > 255:
                    v = 255
                elif v < 0:
                    v = 0
                # rgb 변환
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                # 알맞은값 넣기
                m_tarImage[RR][i][j], m_tarImage[GG][i][j], m_tarImage[BB][i][j] = int(r), int(g), int(b)
            else:
                for rgb in range(RGB):
                    m_tarImage[rgb][i][j] = int(m_oriImage[rgb][i][j])
    ######################
    OnDraw()

def edgeImage2():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    global sx, sy, ex, ey, boxLine
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)

    ## RGB --> HSI
    oriImageHSV = OnMalloc3D(RGB, m_oriH, m_oriW, 0.0)
    ## RGB --> HSV 변환 입력
    for i in range(m_oriH):
        for j in range(m_oriW):
            r, g, b = m_oriImage[RR][i][j], m_oriImage[GG][i][j], m_oriImage[BB][i][j]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            oriImageHSV[0][i][j], oriImageHSV[1][i][j], oriImageHSV[2][i][j] = h, s, v

    # 진짜 영상처리
    MSIZE = 3
    mask = [[0, -1, 0],
            [0, 1, 0],
            [0, 0, 0]]
    ## 임시 메모리 확보
    tempOriImageHSV = OnMalloc3D(RGB, m_oriH + 2, m_oriW + 2)
    tempTarImageHSV = OnMalloc3D(RGB, m_oriH + 2, m_oriW + 2, 0)
    for rgb in range(RGB):
        for i in range(m_oriH):
            for j in range(m_oriW):
                tempOriImageHSV[rgb][i + 1][j + 1] = oriImageHSV[rgb][i][j]
    ## 회선 연산
    for i in range(m_oriH):
        for j in range(m_oriW):
            S = 0.0
            for m in range(MSIZE):
                for n in range(MSIZE):
                    S += tempOriImageHSV[2][i + m][j + n] * mask[m][n]
            tempTarImageHSV[2][i][j] = S
            tempTarImageHSV[1][i][j] = tempOriImageHSV[1][i][j]
            tempTarImageHSV[0][i][j] = tempOriImageHSV[0][i][j]

    ## 후처리 및 임시 결과 --> 결과
    if sx == -1:
        sx = sy = 0
        ex = m_tarW - 1
        ey = m_tarH - 1

    for i in range(m_tarH):
        for j in range(m_tarW):
            if sx <= j <= ex and sy <= i <= ey:
                # 후처리
                tempTarImageHSV[2][i][j] += 127.0
                # h,s,v값 찾기
                h = tempTarImageHSV[0][i][j]
                s = tempTarImageHSV[1][i][j]
                v = tempTarImageHSV[2][i][j]
                # 오버플로우 체크
                if v > 255:
                    v = 255
                elif v < 0:
                    v = 0
                # rgb 변환
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                # 알맞은값 넣기
                m_tarImage[RR][i][j], m_tarImage[GG][i][j], m_tarImage[BB][i][j] = int(r), int(g), int(b)
            else:
                for rgb in range(RGB):
                    m_tarImage[rgb][i][j] = int(m_oriImage[rgb][i][j])
    ######################
    OnDraw()

def changeSatur():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)
    value = askfloat('확대', '값(-1.0~1.0)')

    global sx, sy, ex, ey, boxLine
    if sx == -1:
        sx = sy = 0
        ex = m_tarW - 1
        ey = m_tarH - 1
    # 진짜 영상처리
    for i in range(m_oriH):
        for j in range(m_oriW):
            if sx <= j <= ex and sy <= i <= ey:
                r, g, b = m_oriImage[RR][i][j], m_oriImage[GG][i][j], m_oriImage[BB][i][j]
                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                s += value
                if s > 1:
                    s = 1.0
                elif s < 0.0:
                    s = 0
                # rgb 변환
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                # 알맞은값 넣기
                m_tarImage[RR][i][j], m_tarImage[GG][i][j], m_tarImage[BB][i][j] = int(r), int(g), int(b)
            else:
                for rgb in range(RGB):
                    m_tarImage[rgb][i][j] = int(m_oriImage[rgb][i][j])
    ######################

    OnDraw()

import colorsys
def selectRangeHSV():
    global window, canvas, paper, fileName
    global m_oriImage, m_tarImage
    global m_oriH, m_oriW, m_tarH, m_tarW
    ## 메모리 해제 필요없음
    ## 결과영상크기결정 --> 알고리즘에 따라 바뀜
    m_tarH = m_oriH
    m_tarW = m_oriW
    # 메모리 할당
    m_tarImage = OnMalloc3D(RGB, m_tarH, m_tarW)
    range1 = askinteger('범위추출', '시작 범위 (0-360)')
    range2 = askinteger('범위추출', '끝 범위 (0-360)')

    global sx, sy, ex, ey, boxLine
    if sx == -1:
        sx = sy = 0
        ex = m_tarW - 1
        ey = m_tarH - 1
    # 진짜 영상처리
    for i in range(m_oriH):
        for j in range(m_oriW):
            if sx <= j <= ex and sy <= i <= ey:
                r, g, b = m_oriImage[RR][i][j], m_oriImage[GG][i][j], m_oriImage[BB][i][j]
                h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                h = h * 360  # Convert to degrees
                if range1 <= h <= range2:
                    m_tarImage[RR][i][j], m_tarImage[GG][i][j], m_tarImage[BB][i][j] = int(r), int(g), int(b)
                else:
                    gray = int((r+g+b)/3)
                    m_tarImage[RR][i][j] = m_tarImage[GG][i][j] = m_tarImage[BB][i][j] = gray
            else:
                for rgb in range(RGB):
                    m_tarImage[rgb][i][j] = int(m_oriImage[rgb][i][j])
    ######################

    OnDraw()


###############################################################################################################################################
## 전역변수
window, canvas, paper = None, None, None
m_oriImage, m_tarImage = None, None     # 3차원 배열
m_oriH, m_oriW, m_tarH, m_tarW = [0] * 4
fileName = ''
RR, GG, BB, RGB = 0, 1, 2, 3    # 상수 정의
sbar = None # 상태바
window, canvas, paper = None, None, None
sx, sy, ex, ey = [-1] * 4
boxLine = None
mouseYN = None
hop = 1
## 메인코드
window = Tk()
window.geometry('512x512')
window.title('Color Image Processing (RC 3)')

sbar = Label(window, text="상태바", bd=1, relief=SUNKEN, anchor=W)
sbar.pack(side=BOTTOM, fill=X)

# 메뉴 만들기
mouseYN = BooleanVar()  # 마우스 사용 여부 변수
mouseYN.set(False)  # 초기값 No
mainMenu = Menu(window)  # 메뉴의 틀
window.config(menu=mainMenu)

fileMenu = Menu(mainMenu, tearoff=0)  # 상위 메뉴
mainMenu.add_cascade(label='파일', menu=fileMenu)
fileMenu.add_command(label='열기', command=OnOpenDocument)
fileMenu.add_command(label='저장', command=OnSaveDocument)
fileMenu.add_separator()
fileMenu.add_command(label='종료', command=exit)

pixelMenu = Menu(mainMenu, tearoff=0)  # 상위 메뉴
mainMenu.add_cascade(label='화소점 처리', menu=pixelMenu)
pixelMenu.add_command(label='동일이미지', command=equalImage)
pixelMenu.add_command(label='그레이스케일', command=grayScaleImage)
pixelMenu.add_command(label='밝게/어둡게', command=addImage)
pixelMenu.add_command(label='반전', command=reverseImage)
pixelMenu.add_command(label='이진화', command=bwImage)
pixelMenu.add_command(label='감마보정', command=gammaImage)
pixelMenu.add_command(label='and', command=andImage)
pixelMenu.add_command(label='or', command=orImage)
pixelMenu.add_command(label='포스터라이징', command=posterImage)
pixelMenu.add_command(label='범위강조', command=rangeImage)
pixelMenu.add_command(label='파라볼라', command=parabolaImage)

geometryMenu = Menu(mainMenu, tearoff=0)  # 상위 메뉴
mainMenu.add_cascade(label='기하학 처리', menu=geometryMenu)
geometryMenu.add_command(label='확대', command=zoomInImage)
geometryMenu.add_command(label='축소', command=zoomOutImage)
geometryMenu.add_command(label='이동', command=moveImage)
geometryMenu.add_command(label='회전', command=rotateImage)
geometryMenu.add_command(label='상하대칭', command=mirroringImage1)
geometryMenu.add_command(label='좌우대칭', command=mirroringImage2)

histogramMenu = Menu(mainMenu, tearoff=0)  # 상위 메뉴
mainMenu.add_cascade(label='히스토그램 처리', menu=histogramMenu)
histogramMenu.add_command(label='스트레치', command=stretchImage)
histogramMenu.add_command(label='엔드-인', command=endInImage)
histogramMenu.add_command(label='평활화', command=histoEqual)

areaMenu = Menu(mainMenu, tearoff=0)  # 상위 메뉴
mainMenu.add_cascade(label='화소영역 처리', menu=areaMenu)
areaMenu.add_command(label='엠보싱(RGB)', command=embossRGBImage)
areaMenu.add_command(label='엠보싱(HSV)', command=embossHSVImage)
areaMenu.add_command(label='블러링', command=blurrImage)
areaMenu.add_command(label='샤프닝', command=sharpImage)
areaMenu.add_command(label='수직경계선', command=edgeImage1)
areaMenu.add_command(label='수평경계선', command=edgeImage2)

hsvMenu = Menu(mainMenu, tearoff=0)  # 상위 메뉴
mainMenu.add_cascade(label='HSV 처리', menu=hsvMenu)
hsvMenu.add_command(label='채도변경', command=changeSatur)
hsvMenu.add_command(label='범위추출', command=selectRangeHSV)

mainMenu.add_checkbutton(label="마우스 사용", onvalue=1, offvalue=0, variable=mouseYN, command=OnBindMouse)

window.mainloop()
