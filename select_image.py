from tkinter import font
import tkinter
from PIL import Image, ImageTk
import os
import shutil
import webbrowser

known_face_file = []

for dir_dataset in os.listdir(os.path.join(os.getcwd(), 'face_dataset')):
    if dir_dataset == 'no_face' or dir_dataset == 'お知らせ' or dir_dataset == 'ブログ':
        continue
    if not os.path.isdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset)):
        continue
    for file in os.listdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset)):
        if '.jpg' not in file:
            continue
        known_face_file.append(os.path.join(os.getcwd(), 'face_dataset', dir_dataset, file))

# random.shuffle(known_face_file)
print("file count: " + str(len(known_face_file)))

window_size = [1920, 1080]

image_order = 0
init = True
pixel_size = -120

if not os.path.isfile(os.path.join(os.getcwd(), 'selected_count.txt')):
    with open('selected_count.txt', 'w') as f:
        f.write('0')

with open('selected_count.txt', 'r') as f:
    image_order = int(f.read())
    if type(image_order) is not int:
        image_order = 0
    print(image_order)


def show_image(order, root):
    global known_face_file, canvas, image, tk_image, next_button, before_button, init, font, label1, label2
    root.title(known_face_file[order])
    person_name = os.path.basename(known_face_file[image_order]).split('=')[0]

    print("Pressed next\nimage order: " + str(order))
    image = Image.open(known_face_file[image_order])
    width, height = image.size
    if init is False:
        canvas.destroy()
        label1.destroy()
        label2.destroy()
    init = False
    label1 = tkinter.Label(root, text=person_name, font=font)
    label2 = tkinter.Label(root, text=image_order, font=font)
    canvas = tkinter.Canvas(
        root,
        width=width,
        height=height
    )
    tk_image = ImageTk.PhotoImage(image)
    canvas.create_image(
        width / 2,
        height / 2,
        anchor=tkinter.CENTER,
        image=tk_image,
        tag='image'
    )
    canvas.pack(side='bottom')
    canvas.place(x=(window_size[0] - width) / 2, y=(window_size[1] - height) / 2)
    before_button.pack()
    next_button.pack()
    label1.pack(side=tkinter.LEFT)
    label2.pack(side=tkinter.BOTTOM)
    return order


window_root = tkinter.Tk()
font = font.Font(size=pixel_size, weight='bold')
window_root.title(known_face_file[image_order])
window_root.geometry(str(window_size[0]) + 'x' + str(window_size[1]))

next_button = tkinter.Button(text='次へ', width=50)
before_button = tkinter.Button(text='一つ戻る', width=50)
show_image(image_order, window_root)


def go_next(event):
    global image_order
    print("Pressed next\nimage order: " + str(image_order))
    image_order += 1
    show_image(image_order, window_root)


def back_before(event):
    global image_order
    print("Pressed before\nimage order: " + str(image_order))
    image_order -= 1
    show_image(image_order, window_root)


def yes(event):
    print("Copying..." + os.path.basename(known_face_file[image_order]))
    if not os.path.isdir(os.path.join(os.getcwd(),
                                      'selected_dataset',
                                      os.path.basename(known_face_file[image_order]).split('=')[0])):
        os.mkdir(os.path.join(os.getcwd(),
                              'selected_dataset',
                              os.path.basename(known_face_file[image_order]).split('=')[0]))

    shutil.copy2(known_face_file[image_order],
                 os.path.join(
                     os.getcwd(),
                     'selected_dataset',
                     os.path.basename(known_face_file[image_order]).split('=')[0],
                     os.path.basename(known_face_file[image_order])
                 ))
    go_next('')


def do_nothing(event):
    pass


def finish(event):
    with open('selected_count.txt', 'w') as f:
        f.write(str(image_order))
    exit()


next_button.bind("<Button-1>", go_next)
before_button.bind("<Button-1>", back_before)
window_root.bind('<y>', yes)
window_root.bind('<n>', go_next)
window_root.bind('<b>', back_before)
window_root.bind('<o>', lambda e: webbrowser.open(
    'https://ameblo.jp/' + known_face_file[image_order].split('=')[1] + '/entry-' +
    known_face_file[image_order].split('=')[-1].split('-')[0] + '.html'))
window_root.bind('<q>', finish)

window_root.mainloop()
