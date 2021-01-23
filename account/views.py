from django.shortcuts import render
from utils.baseclasses import BaseAPIView
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS_1_V1_5
from Crypto.PublicKey import RSA
from .decorators import login_required
from utils.hashtool import hash2mark
import json
import hashlib
import base64
import os
from utils import functions, contants, google_auth
from .models import Cache, AdminUser, WebsiteInfo, ImgSource, Carousel
from django.contrib import auth
from .serializer import AdminUserSerializer, WebsiteInfoSerializer
# Create your views here.


class LoginRequest(BaseAPIView):
    def get(self, request):
        mark_info = request.GET.get('mark_info')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        verify_mark = hash2mark(timestamp, nonce)
        _timestamp = functions.timestamp()

        if mark_info != verify_mark:
            return self.error({'msg': '标记信息校验错误'})
        ip = functions.user_ip()

        if Cache.objects.filter(ip_address=ip).exists():
            obj = Cache.objects.get(ip_address=ip)
            if _timestamp - obj.timestamp <= 1800:
                return self.info(
                    {
                        'mark_info': obj.mark_info,
                        'pub_key': obj.public
                    }
                )
            else:
                obj.delete()

        # todo: 完善hash函数以及mark_info2int函数
        if _timestamp - timestamp <= 1800:
            rsa = RSA.generate(2048, mark_info)
            rsa_hex_pub = rsa.publickey().export_key('DER').hex()
            rsa_hex_sec = rsa.export_key('DER').hex
            obj = Cache.objects.create(mark_info=mark_info, public=rsa_hex_pub, secret=rsa_hex_sec,
                                       timestamp=timestamp, ip_address=ip)
            obj.save()
            return self.success(
                {
                    'pub_key': obj.public
                }
            )

        return self.error({
            'errMsg': 'timeout'
        })


class Login(BaseAPIView):
    def post(self, request):
        data = request.data
        mark_info = data['mark_info']

        if not Cache.objects.filter(mark_info=mark_info).exists():
            return self.error({
                'errMsg': 'mark_info is not exist.'
            })

        # 数据解密处理，最后转json
        crypto_data = data['crypto']
        obj = Cache.objects.get(mark_info=mark_info)
        sec = bytes.fromhex(obj.secret)
        rsa = RSA.import_key(sec, 'DER')
        cipher = Cipher_PKCS_1_V1_5.new(rsa)
        text = cipher.decrypt(crypto_data)

        try:
            json_data = json.loads(text)
        except json.decoder.JSONDecodeError:
            return self.error({
                'errMsg': 'cipher message error.'
            })

        username = json_data['username']
        password = json_data['password']
        user = auth.authenticate(username=username, password=password)
        if user:
            if AdminUser.check_password(user,password):
                auth.login(request, user)
                Cache.objects.get(mark_info=mark_info).delete()
                return self.success(None)
            else:
                return self.error({
                    'errMsg': "Username or Password is incorrect"
                })
        else:
            return self.error({
                'errMsg': "User is not existed"
            })


class UserInfoAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        return self.success(AdminUserSerializer(user).data)


class WebsiteInfoAPI(BaseAPIView):
    def get(self, request):
        obj = WebsiteInfo.objects.get(_id=0)
        return self.success(WebsiteInfoSerializer(obj).data)

    @login_required
    def post(self, request):
        data = request.data
        obj = WebsiteInfo.objects.get(_id=0)
        obj.title = data['title']
        obj.record = data['record']
        obj.record_switch = data['record_switch']
        obj.save()
        return self.success(None)


# 用于响应需要二次验证进行修改用户名、密码、邮箱的操作
class VerifyChange(BaseAPIView):
    @login_required
    def post(self, request):
        data = request.data
        user = request.user

        username = data['username']
        password = data['password']
        email = data['email']
        code = data['code']

        # 这里先默认用户已经进行了二次验证绑定
        db_google_sec = user.google_secret
        google_code_array = google_auth.generate_pin(db_google_sec)
        if code not in google_code_array:
            return self.error({
                'errMsg': 'Google verify code is wrong.'
            })

        user.username = username
        user.email = email
        if len(password) != 0:
            if len(password) <= 12:
                return self.error({
                    'errMsg': 'Password is too short.'
                })
            user.set_password(password)
        user.save()
        return self.success(None)


# 用于响应修改二次验证的修改
class ChangeVerifySec(BaseAPIView):
    @login_required
    def get(self, request):
        random_sec = google_auth.generate_secret()
        return self.success({
            'sec': random_sec
        })

    @login_required
    def post(self, request):
        user = request.user
        data = request.data
        upload_sec =  data['new_sec']
        origin = data['origin']
        new_code = data['new_code']

        db_google_sec = user.google_secret
        new_code_array = google_auth.generate_pin(upload_sec)

        # todo：判断upload_sec是base32编码
        if db_google_sec is None:
            if new_code in new_code_array:
                user.google_secret = upload_sec
                user.save()
                return self.success(None)
            else:
                return self.error(
                    {
                        'errMsg': 'New google auth code error.'
                    }
                )
        origin_code_array = google_auth.generate_pin(db_google_sec)
        # todo:代码重复，后续考虑优化
        if origin in origin_code_array:
            if new_code in new_code_array:
                user.google_secret = upload_sec
                user.save()
                return self.success(None)
            else:
                return self.error(
                    {
                        'errMsg': 'New google auth code error.'
                    }
                )
        else:
            return self.error(
                    {
                        'errMsg': 'Old google auth code error.'
                    }
                )


class UploadAPI(BaseAPIView):
    @login_required
    def get(self, request):
        # 这里的MD5信息是图片内容经过Base64处理后进行哈希得到
        md5 = request.GET.get('file_md5')
        if ImgSource.objects.filter(md5=md5).exists():
            return self.info(
                {
                    'errMsg': 'File already exists.'
                }
            )

        return self.success(None)

    def post(self, request):
        data = request.data
        file_data = data['encode_data']
        file_type = data['type']
        file_md5 = data['md5']
        if file_type not in file_type:
            return self.error(
                {
                    'errMsg': 'File type is not allow.'
                }
            )

        if ImgSource.objects.filter(md5=file_md5).exists():
            return self.error(
                {
                    'errMsg': 'File already exists.'
                }
            )

        md5_digest = hashlib.md5(file_data.encode('utf-8')).hexdigest()
        file_path = './static/images/{0}.{1}'.format(md5_digest, file_type)
        file_bin = base64.b64decode(file_data)

        f = open(file_path, 'wb')
        f.write(file_bin)
        f.close()

        obj = ImgSource.objects.create(md5=md5_digest, path=file_path)
        obj.save()

        return self.success(None)


class CarouselManage(BaseAPIView):
    @login_required
    def post(self, request):
        data = request.data
        url = data['url']
        description = data['desc']

        obj = Carousel.objects.create(url=url, description = description)
        obj.save()

        return self.success(None)

    def get(self, request):
        pass

    @login_required
    def put(self, request):
        data = request.data
        desc = data['desc']
        _id = data['id']

        if not Carousel.objects.filter(_id=_id).exists():
            return self.error(
                {
                    'errMsg': 'Carousel with post id is not exist.'
                }
            )

        obj = Carousel.objects.get(_id=_id)
        obj.description = desc
        obj.save()

        return self.success(None)

    @login_required
    def delete(self, request):
        _id = request.data['id']

        # todo : 重复代码
        if not Carousel.objects.filter(_id=_id).exists():
            return self.error(
                {
                    'errMsg': 'Carousel with post id is not exist.'
                }
            )

        Carousel.objects.get(_id=_id).delete()
        return self.success(None)