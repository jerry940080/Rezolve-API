import ctypes
ctypes.CDLL("libcudnn.so")
print("cuDNN 已正確載入")