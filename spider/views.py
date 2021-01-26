from account.decorators import login_required
from utils.baseclasses import BaseAPIView
from .models import VXPage
from .serializer import VXPageSerializer, VXPageHomeSerializer
from utils import article_spider
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response


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
        pageinator = Paginator(articles, 5, 2)
        page = request.GET.get('page')

        try:
            result = pageinator.page(page)
        except PageNotAnInteger:
            result = pageinator.page(1)
        except EmptyPage:
            result = pageinator.page(pageinator.num_pages)

        result = VXPageHomeSerializer(result, many=True)

        return Response({
            'code': 0,
            'total': articles.count() // 10 + 1,
            'data': result.data
        })

    # 爬虫需要检查地址的有效性
    @login_required
    def post(self, request):
        url = request.data['vx_url']
        desc = request.data['desc']
        page_json = article_spider.get_article_page(url)
        obj = VXPage.objects.create(
            title=page_json['title'],
            author=page_json['nickname'],
            context=page_json['page'],
            description=desc
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
