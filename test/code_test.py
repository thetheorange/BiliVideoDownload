import jsonpath
import qrcode
import requests

url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
    "Referer": "https://www.bilibili.com/"
}
data = requests.get(url=url,
                    headers=headers)
data = data.json()
print(data)
# 生成二维码
qr = qrcode.QRCode(
    version=5,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4
)
qr.add_data(jsonpath.jsonpath(data, "$.data.url")[0])
qr.make(fit=True)
# 保存二维码图片
code_img = qr.make_image(fill_color="black")
code_img.save("../template/images/code.jpg")