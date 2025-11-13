import cv2 as cv
import numpy as np
import sys

# 4개 이미지 읽기
img_1 = cv.imread("/home/dudqls/log-git/week8/imgs/1.jpg")
img_2 = cv.imread("/home/dudqls/log-git/week8/imgs/2.jpg")
img_3 = cv.imread("/home/dudqls/log-git/week8/imgs/3.jpg")
img_4 = cv.imread("/home/dudqls/log-git/week8/imgs/4.jpg")

images = [img_1, img_2, img_3, img_4]

# 각 이미지가 제대로 읽혔는지 확인
for idx, img in enumerate(images, 1):
    if img is None:
        sys.exit(f"Could not read image {idx}")

def detect_yellow_border(img):
    # BGR을 HSV로 변환
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    
    # 노란색 범위 정의 (더 넓은 범위)
    lower_yellow = np.array([23, 100, 80])
    upper_yellow = np.array([40, 255, 255])
    
    # 노란색 마스크 생성
    mask = cv.inRange(hsv, lower_yellow, upper_yellow)
    
    # 모폴로지 연산으로 노이즈 제거
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    
    # 엣지 검출 (Canny)
    edges = cv.Canny(mask, 50, 150)
    
    # 엣지를 기반으로 컨투어 찾기
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    # BGR 컬러 이미지로 생성 (검은색 배경)
    result = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    
    # 감지된 선 처리
    if contours:
        # 컨투어를 면적 기준으로 정렬
        contours = sorted(contours, key=cv.contourArea, reverse=True)
        for contour in contours[:2]:  # 상단과 하단 경계
            # 정확한 경계선만 흰색으로 그리기
            cv.drawContours(result, [contour], 0, (255, 255, 255), 2)
    
    # 원래 노란색 마스크 영역을 노란색으로 채우기
    yellow_area = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    yellow_area[mask > 0] = (0, 255, 255)
    
    # 결과 합치기 (노란색 영역 + 흰색 선)
    result = cv.add(yellow_area, result)
    
    return result

# 각 이미지 처리 및 표시
for idx, img in enumerate(images, 1):
    processed = detect_yellow_border(img)
    
    cv.imshow(f"Image {idx} - Yellow Border Detection", processed)
    
    k = cv.waitKey(0)
    
    if k == ord("s"):
        filename = f"result_{idx}.png"
        cv.imwrite(filename, processed)
        print(f"Saved: {filename}")
    elif k == ord("q"):
        break

cv.destroyAllWindows()