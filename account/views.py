from django.shortcuts import render
from utils.baseclasses import BaseAPIView
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS_1_V1_5
from Crypto.PublicKey import RSA
from Crypto import Random
from .decorators import login_required, check_maintain
from utils.hashtool import hash2mark
import json
import hashlib
import base64
import time
from utils import functions, contants, google_auth, article_spider
from .models import Cache, AdminUser, WebsiteInfo, ImgSource, Carousel, Personnel
from django.contrib import auth
from .serializer import AdminUserSerializer, WebsiteInfoSerializer, CarouselSerializer, PersonnelSerializer


class LoginRequest(BaseAPIView):
    @check_maintain
    def get(self, request):
        mark_info = request.GET.get('mark_info')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')

        timestamp = int(timestamp)
        verify_mark = hash2mark(timestamp, nonce)
        _timestamp = functions.timestamp()

        if mark_info != verify_mark:
            return self.error({'msg': '标记信息校验错误'})
        ip = functions.user_ip(request)

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

        if _timestamp - timestamp <= 1800:
            rsa = RSA.generate(2048, Random.new().read)
            rsa_hex_pub = rsa.publickey().export_key('PEM').decode()
            rsa_hex_sec = rsa.export_key('PEM').decode()
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
        ip_address = functions.user_ip(request)

        if not Cache.objects.filter(mark_info=mark_info, ip_address=ip_address).exists():
            return self.error({
                'errMsg': 'mark_info is not exist.'
            })

        # 数据解密处理，最后转json
        obj = Cache.objects.get(mark_info=mark_info, ip_address=ip_address)
        if obj.errCount >= 5:
            return self.frequent()

        crypto_data = data['crypto']
        sec = obj.secret
        rsa = RSA.import_key(sec, 'PEM')
        cipher = Cipher_PKCS_1_V1_5.new(rsa)
        text = cipher.decrypt(base64.b64decode(crypto_data), None).decode()
        try:
            json_data = json.loads(text)
        except json.decoder.JSONDecodeError:
            return self.error({
                'errMsg': 'cipher message error.'
            })

        username = json_data['username']
        password = json_data['password']
        user = auth.authenticate(username=username, password=password)
        if user and AdminUser.check_password(user, password):
            auth.login(request, user)
            Cache.objects.get(mark_info=mark_info).delete()
            return self.success(None)
        else:
            obj.errCount += 1
            obj.save()
            return self.error({
                'errMsg': "User is not existed or password is wrong"
            })


class LogoutAPI(BaseAPIView):
    @login_required
    def get(self, request):
        auth.logout(request)
        return self.success(None)



class UserInfoAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        return self.success(AdminUserSerializer(user).data)


class WebsiteInfoAPI(BaseAPIView):
    def get(self, request):
        obj = WebsiteInfo.objects.last()
        return self.success(WebsiteInfoSerializer(obj).data)

    @login_required
    def post(self, request):
        data = request.data
        obj = WebsiteInfo.objects.last()
        obj.title = data['title']
        obj.record = data['record']
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

        # todo:对谷歌验证码短时间验证次数的校验可以改为一个模块

        lastTimestamp = user.errTimestamp
        timestamp = functions.timestamp()

        if (user.errCount > contants.verifyMax) and (lastTimestamp is not None) and \
                (timestamp - lastTimestamp < contants.intervals):
            return self.frequent({
                'errMsg': 'Verify error is too frequently.'
            })

        # 这里先默认用户已经进行了二次验证绑定
        db_google_sec = user.google_secret
        google_code_array = google_auth.generate_pin(db_google_sec)
        if code not in google_code_array:
            user.errCount += 1
            user.errTimestamp = timestamp
            user.save()
            return self.error({
                'errMsg': 'Google verify code is wrong.',
                'errCount': user.errCount
            })

        user.username = username
        user.email = email
        if len(password) != 0:
            if len(password) <= 12:
                return self.error({
                    'errMsg': 'Password is too short.'
                })
            user.set_password(password)
        user.errCount = 0
        user.errTimestamp = None
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

        lastTimestamp = user.errTimestamp
        timestamp = functions.timestamp()

        if (user.errCount > contants.verifyMax) and (lastTimestamp is not None) and \
                (timestamp - lastTimestamp < contants.intervals):
            return self.frequent({
                'errMsg': 'Verify error is too frequently.'
            })

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

        if origin in origin_code_array and new_code in new_code_array:
            user.google_secret = upload_sec
            user.errCount = 0
            user.errTimestamp = None
            user.save()
            return self.success(None)

        user.errCount += 1
        user.errTimestamp = timestamp
        user.save()
        return self.error(
                {
                    'errMsg': 'Old code or new code error.'
                }
            )


class UploadAPI(BaseAPIView):

    @login_required
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
            obj = ImgSource.objects.get(md5=file_md5)
            return self.success(
                {
                    'file_path': obj.path[1:]
                }
            )

        md5_digest = hashlib.md5(file_data.encode('utf-8')).hexdigest()
        file_path = './sources/images/{0}.{1}'.format(md5_digest, file_type)
        file_bin = base64.b64decode(file_data)

        f = open(file_path, 'wb')
        f.write(file_bin)
        f.close()

        obj = ImgSource.objects.create(md5=md5_digest, path=file_path)
        obj.save()

        return self.success({
            'file_path': file_path[1:]
        })


class CarouselManage(BaseAPIView):
    @login_required
    def post(self, request):
        data = request.data
        url = data['url']
        description = data['desc']

        obj = Carousel.objects.create(url=url, description = description)
        obj.save()

        return self.success(None)

    @check_maintain
    def get(self, request):
        objs = Carousel.objects.all()
        return self.success(CarouselSerializer(objs, many=True).data)

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


class PersonnelManage(BaseAPIView):
    @check_maintain
    def get(self, request):
        objs = Personnel.objects.all()
        return self.success(PersonnelSerializer(objs, many=True).data)

    @login_required
    def post(self, request):
        data = request.data
        name = data['name']
        avatar = data['avatar']
        duties = data['duties']

        obj = Personnel.objects.create(
            name=name,
            avatar=avatar,
            duties=duties
        )
        obj.save()
        return self.success(None)

    @login_required
    def put(self, request):
        data = request.data

        _id = data['id']
        name = data['name']
        duties = data['duties']

        if not Personnel.objects.filter(_id=_id).exists():
            return self.error(
                {
                    'errMsg': 'Personnel is not exists.'
                }
            )

        obj = Personnel.objects.get(_id=_id)
        obj.name = name
        obj.duties = obj.duties
        obj.save()
        return self.success(None)

    # todo:重复代码
    @login_required
    def delete(self, request):
        _id = request.data['id']

        if not Personnel.objects.filter(_id=_id).exists():
            return self.error(
                {
                    'errMsg': 'Personnel is not exists.'
                }
            )

        Personnel.objects.get(_id=_id).delete()
        return self.success(None)


class SwitchAPI(BaseAPIView):
    @login_required
    def get(self, request):
        switch = request.GET.get('switch')
        obj = WebsiteInfo.objects.last()
        if switch == 'maintain':
            obj.maintain = not obj.maintain
        elif switch == 'record':
            obj.record_switch = not obj.record_switch
        else:
            return self.error(None)

        obj.save()
        return self.success(None)