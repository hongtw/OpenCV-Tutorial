import cv2
import matplotlib.pyplot as plt

def show(img, title=None, figsize=(15, 12)):
    #show img from opencv to jupyter notebook
    plt.figure(figsize=figsize)
    plt.axis('off')
    if title:
        plt.title(title)
    if img.ndim == 2:
        plt.imshow(img, cmap='gray')
    else:
        plt.imshow(img[:,:,[2,1,0]])
        
def show_images(images, title, ver=True, figsize=(15, 7)):

    import matplotlib.pyplot as plt
    from matplotlib.pyplot import figure, imshow, axis
     
    fig = figure(figsize=figsize)
    total = len(images)
    for i in range(total):
        if images[i].ndim == 3:
            images[i] = images[i][:,:,[2,1,0]]
        if ver:
            fig.add_subplot(total, 1, i + 1)
        else:
            fig.add_subplot(1, total, i + 1)
        plt.title(title[i])
        imshow(images[i], cmap='Greys_r')
        axis('off')
        
    plt.show()