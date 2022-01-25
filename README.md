# Automatic-License-Plate-Recognition-based-on-NVDIA-Jetson-board-with-pytesseract-module

比較適用的情境為**靜態**的情境，
若是**車牌會晃動**，則誤判機率高。
同時。相片的**寬高要夠大**，至少(w,h) = **(640,480)**，
這樣的相片大小才可以被tesseract的OCR辨識
(但辨識結果不是完全正確，大概tesseract的精準度不夠吧)。
