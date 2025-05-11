import matplotlib.pyplot as plt

def display_images(images):
    plt.figure()

    plt.subplot(2, 3, 1)
    plt.title(r"$\alpha=0 °$")
    plt.imshow(images[0], cmap='gray')
    plt.axis('off')

    plt.subplot(2, 3, 2)
    plt.title(r"$\alpha=90 °$")
    plt.imshow(images[1], cmap='gray')
    plt.axis('off')

    plt.subplot(2, 3, 3)
    plt.title(r"$\alpha=180 °$")
    plt.imshow(images[2], cmap='gray')
    plt.axis('off')

    plt.subplot(2, 3, 4)
    plt.title(r"$\alpha=270 °$")
    plt.imshow(images[3], cmap='gray')
    plt.axis('off')

    plt.subplot(2, 3, 5)
    plt.title(r"$\alpha=360 °$")
    plt.imshow(images[4], cmap='gray')
    plt.axis('off')

    plt.subplot(2, 3, 6)
    plt.title(r"Somme des 4 premières")
    plt.imshow(images[0]+images[1]+images[2]+images[3], cmap='gray')
    plt.axis('off')

    plt.tight_layout()
    plt.suptitle('Images enregistrées avec succès.')
    plt.show()

def save_images(images, path):
    for i in range(5):
        plt.figure()
        plt.imshow(images[i], 'gray')
        plt.axis('off')
        plt.savefig(f'{path}/zygo_interf_{i+1}.png')
        plt.close()
    return 0

if __name__ == '__main__':
    import numpy as np
    images = [np.random.randint(0, 255, (100, 100)) for _ in range(5)]
    display_images(images)