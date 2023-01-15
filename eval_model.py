from keras.models import load_model, Model
from os import path, getcwd, listdir
from keras.preprocessing.image import image_utils
from sys import argv

if argv.__len__() != 2:
    exit(1)
if not path.isfile(argv[1]):
    exit(1)

model: Model = load_model(path.join(getcwd(), "models", "2023-01-14 14:23:17.353263hello.h5"))
model.summary()
image = image_utils.img_to_array(image_utils.load_img(argv[1], target_size=(224, 224, 3)))

image_nad = image_utils.img_to_array(image) / 255

image_nad = image_nad[None, ...]

labels: dict = {'一岡伶奈': 0, '上國料萌衣': 1, '中山夏月姫': 2, '中西香菜': 3, '井上玲音': 4, '伊勢鈴蘭': 5,
                '佐々木莉佳子': 6, '佐藤優樹': 7, '入江里咲': 8, '八木栞': 9, '前田こころ': 10, '加賀楓': 11,
                '勝田里奈': 12, '北原もも': 13, '北川莉央': 14, '和田桜子': 15, '嗣永桃子': 16, '太田遥香': 17,
                '室田瑞希': 18, '宮崎由加': 19, '宮本佳林': 20, '小川麗奈': 21, '小林萌花': 22, '小片リサ': 23,
                '小田さくら': 24, '小野瑞歩': 25, '小野田紗栞': 26, '小関舞': 27, '山岸理子': 28, '山木梨沙': 29,
                '山﨑夢羽': 30, '山﨑愛生': 31, '岡村ほまれ': 32, '岡村美波': 33, '岸本ゆめの': 34, '島倉りか': 35,
                '川名凜': 36, '川村文乃': 37, '工藤由愛': 38, '工藤遥': 39, '平井美葉': 40, '平山遊季': 41,
                '広本瑠璃': 42, '広瀬彩海': 43, '斉藤円香': 44, '新沼希空': 45, '有澤一華': 46, '松本わかな': 47,
                '松永里愛': 48, '梁川奈々美': 49, '森戸知沙希': 50, '植村あかり': 51, '横山玲奈': 52, '橋迫鈴': 53,
                '段原瑠々': 54, '江口紗耶': 55, '江端妃咲': 56, '河西結心': 57, '浅倉樹々': 58, '浜浦彩乃': 59,
                '清水佐紀': 60, '清野桃々姫': 61, '為永幸音': 62, '熊井友理奈': 63, '生田衣梨奈': 64, '田代すみれ': 65,
                '田口夏実': 66, '田村芽実': 67, '相川茉穂': 68, '石山咲良': 69, '石栗奏美': 70, '石田亜佑美': 71,
                '福田真琳': 72, '秋山眞緒': 73, '稲場愛香': 74, '窪田七海': 75, '竹内朱莉': 76, '笠原桃奈': 77,
                '筒井澪心': 78, '米村姫良々': 79, '船木結': 80, '菅谷梨沙子': 81, '藤井梨央': 82, '西田汐里': 83,
                '西﨑美空': 84, '譜久村聖': 85, '谷本安美': 86, '豫風瑠乃': 87, '道重さゆみ': 88, '遠藤彩加里': 89,
                '里吉うたの': 90, '野村みな美': 91, '金澤朋子': 92, '鈴木香音': 93, '鞘師里保': 94, '須藤茉麻': 95,
                '飯窪春菜': 96, '高木紗友希': 97, '高瀬くるみ': 98}

print(labels.keys())

ans = model.predict(image_nad)
print(ans)
eve = {key: val for key, val in zip(labels, ans[0])}
print(eve)
print(sorted(eve.items(), key=lambda acc: acc[1])[80:])
