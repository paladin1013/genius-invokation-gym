**警告：本代码由于**recognize_card**和**similarity**部分鲁棒性很差，实际上运行结果并不正确。**



保证你先运行过一遍get_images_file.py



ocr.py：记牌器

首先，在使用之前，请把ZOOM=1.5这一行改为你的屏幕缩放率。

运行ocr.py。然后鼠标移动至右上角齿轮圆心，按c。鼠标移动至左下你的牌堆的右下角，按c。（见keypoints1中的两个点）

之后确保你已经换完牌，并且双方还没有打出过牌的情况下，按c开始记录。

运行过程中，请不要挪动缩放或切换窗口。