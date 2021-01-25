from account.decorators import login_required
from utils.baseclasses import BaseAPIView
from .models import VXPage
from .serializer import VXPageSerializer, VXPageHomeSerializer
from utils import article_spider


class ArticlesHomeAPI(BaseAPIView):
    def get(self, request):
        articles = VXPage.objects.all()
        length = VXPage.objects.count()
        articles = articles[length - (min(length, 5)): length]
        return self.success(VXPageHomeSerializer(articles, many=True).data)


class ArticleAPI(BaseAPIView):
    def get(self, request):
        _id = request.GET.get('id')
        obj = VXPage.objects.get(_id=_id)
        return self.success(VXPageSerializer(obj).data)


class ArticlesManage(BaseAPIView):
    def get(self, request):
        articles = VXPage.objects.all()
        return self.success(VXPageHomeSerializer(articles, many=True).data)

    # 爬虫需要检查地址的有效性
    @login_required
    def post(self, request):
        url = request.data['vx_url']
        page_json = article_spider.get_article_page(url)
        obj = VXPage.objects.create(
            title=page_json['title'],
            author=page_json['nickname'],
            context=page_json['page']
        )
        obj.save()

        return self.success(None)

    @login_required
    def put(self, request):
        _id = request.data['id']
        desc = request.data['desc']

        if VXPage.objects.filter(_id=_id).exists():
            obj = VXPage.objects.get(_id=id)
            obj.description = desc
            obj.save()

            return self.success(None)

        return self.error(None)

    @login_required
    def delete(self, request):
        _id = request.data['id']

        if VXPage.objects.filter(_id=_id).exists():
            VXPage.objects.get(_id=_id).delete()
            return self.success(None)

        return self.error(None)
