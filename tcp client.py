#-*- encoding:utf-8 -*-

#server傳影像給client

import socket
import cv2
import numpy
import numpy as np
import math
import time
import imutils
from PIL import Image
#import easyocr
import pytesseract


#client傳給server的文字訊息
clientMessage_01 = 'len ok!'
clientMessage_02 = 'img ok and show ok!!'

TCP_IP = "192.168.43.241"
TCP_PORT = 8000

sock = socket.socket()
sock.connect((TCP_IP, TCP_PORT))
print("connect!")


#socket
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#根據資料長度，將檔案全部接收進來。
#以免因為sock.recv(count)每次這行只能接收count長度的bytes，
#讓data傳的不完整
def recvall(sock, count):
    buf = b'' #bytes type
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def tcp_ip_receive_img():
#    print("client start receive.............")
    
    #--------------------------------------------
    #當呼叫send的時候，資料並不是即時發給客戶端的。
    # 而是放到了系統的socket傳送緩衝區裡，
    # 等緩衝區滿了、或者資料等待超時了，資料才會傳送，
    # 所以有時候傳送太快的話，前一份資料還沒有傳給客戶端，
    # 那麼這份資料和上一份資料一起發給客戶端的時候就會造成“粘包” 。
    #(這也是為什麼接收端接收到的資料是幾份資料混雜起來的)
    #--------------------------------------------

    #接收圖片長度
    length_btyes = sock.recv(1024)  
    #一次REQUEST只會接收 1024 bytes長度的資料，當達1024時，就會輸出中止訊號，並且要等待下次的recv()。 
    # 若不希望中止，則可以使用recvall()。

    #用於處理utf8 decode無法成功執行的問題
    #為了迴避UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 5: invalid start byte
    #選擇犧牲少數幾個無法decode的值
    try:
        length_int = int(length_btyes.decode("utf-8"))  #decode UTF-8 encoded bytes to a Unicode string.
        
#        print(length_int) #FIXME:DEBUG用
    except: #utf8_decode_error
        print("error at: decode UTF-8 encoded bytes to a Unicode string.")


    #確認接收到len後，client傳"len ok!"給server
    #這樣server才會繼續send()
    #如此是避免Server太早開始send()，這樣會造成buffer可能出現兩種data，造成黏包。
    #---------------------------------------------------------
    sock.sendall(clientMessage_01.encode("utf-8"))
    #---------------------------------------------------------   

    #接收圖片本身
    stringData = recvall(sock, length_int)

    #檢驗收到的圖片是否正確  是否出現黏包
#    print((list(stringData))[:3])#FIXME:DEBUG用
#    print((list(stringData))[-3:])#FIXME:DEBUG用

    #img decode
    #先進行btyes to str 的decode，再進行jpg的decode
    data = numpy.fromstring(stringData, dtype='uint8')  #stringData 是一大串類似  '\x01\x02'  這樣的東西的字串
    decimg=cv2.imdecode(data,1)  #解碼圖片

    decimg = cv2.flip(decimg, 1) ##垂直翻轉 #FIXME:根據不同攝像頭，這個可以更改
#    cv2.putText(decimg, "at client", (10, 60), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)  #FIXME:DEBUG用
#    cv2.imshow('CLIENT2',decimg)#FIXME:DEBUG用
    cv2.waitKey(20)

    #展示完圖片後，接著client會告訴server可以傳下一張圖片過來了
    #---------------------------------------------------------  
    sock.sendall(clientMessage_02.encode("utf-8"))
    #---------------------------------------------------------  
    
    #print("Get one")
    #print(decimg.shape)

    return decimg
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



def find_car_plate_find_number(img):
    str_result = ""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #轉灰階(為了加速運算)
    gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise(使影像平滑化,模糊化)去除我們不想要的資訊
    edged = cv2.Canny(gray, 30, 200) #Perform Edge detection(影像邊緣檢測)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #獲取輪廓--findContours
    #cv2.RETR_TREE：建立一個等級樹結構的輪廓。
    #cv2.CHAIN_APPROX_SIMPLE壓縮水平方向，垂直方向，對角線方向的元素，只保留該方向的終點座標，例如一個矩形輪廓只需4個點來儲存輪廓資訊
    cnts = imutils.grab_contours(cnts)#grab contour
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]#只取前十個top10 contour
    screenCnt = None

    # loop over our contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        #對 contour 做多邊形逼近
        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        detected = 0
        #print ("No contour detected")
        return None
    else:
        detected = 1
    #如果有四邊形 就把那四邊形框出來

    if detected == 1:
        cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

    #print(screenCnt[0][0][0])
    #print(screenCnt[0][0][1])
    # Masking the part other than the number plate
    #截的圖片為搜到的四邊形
    #理想的話:只有車牌呈現
    #blank mask(shape to our image)
    mask = np.zeros(gray.shape,np.uint8)
    #挖出四邊形(等等要覆蓋在原圖img)
    new_image = cv2.drawContours(mask,[screenCnt],0,255,-1)
    #masking the entire picture except for the place where the number plate is
    #將遮罩印在原來的圖片上
    new_image = cv2.bitwise_and(img,img,mask=mask)

    # Now crop(截圖)
    #cropping it and saving it as a new image
    (x, y) = np.where(mask == 255)
    #四邊形之座標
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    Cropped = gray[topx:bottomx+1, topy:bottomy+1]

#    cv2.imwrite('./output/output.jpg', Cropped)
#
#    reader = easyocr.Reader(['ch_sim', 'en'])
#    result = reader.readtext('./output/output.jpg', detail=0)
#    print(result)
#
#    str_result = ""
#    for ele in result:
#        str_result = str_result + ele

    #Read the number plate
    #用pytesseract去辨識車牌文字數字
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\user\AppData\Local\tesseract.exe' # FIXME:
    text = pytesseract.image_to_string(Cropped, config='--psm 11')

    #因為會讀到很多東西 然後不知道為甚麼我讀完會的到'??這個'，故去掉問號split掉
    text_s= text.split('\n')

#    img = cv2.putText(img, max(text_s),(screenCnt[0][0][0],screenCnt[0][0][1]-30), cv2.FONT_HERSHEY_SIMPLEX,  
#                       1, (255, 255, 0), 2, cv2.LINE_AA)
#    cv2.imwrite('./output/output2.jpg', img)

    return max(text_s)

def detect():
    car_plate_number = ""

    #會一直執行 "拍一張拍照，然後對照片做處理" 的動作。
    while True:

        #rpi傳圖片給筆電by socket
        frame = tcp_ip_receive_img()

        #圖像處理找出車牌及將車牌外的影像去除
        car_plate_number = find_car_plate_find_number(frame)

        if car_plate_number is not None:
            cv2.putText(frame, car_plate_number, (10, 60), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        cv2.imshow('car plate', frame) #frame此時是bgr形式，因為imshow()輸入的圖片必須是bgr形式
        if cv2.waitKey(1) & 0xFF == 27:
            break


if __name__ == '__main__':
    detect()
    sock.close()
    cv2.destroyAllWindows()