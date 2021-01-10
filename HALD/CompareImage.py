from PIL import Image, ImageChops 
import numpy as np

a = Image.open('1.png')
b = Image.open('2.png')
 
diff = ImageChops.difference(a,b)
diff = np.asarray(diff)
# print(diff)
print(np.sum(diff))

 


