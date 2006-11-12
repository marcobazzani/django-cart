from django.conf.urls.defaults import *
	
urlpatterns = patterns('',
    (r'^$', 'dharmaseed.shop.views.index'),
    (r'^cart/$', 'dharmaseed.shop.views.cart'),
    (r'^cart/add/.*/testcookie/$', 'dharmaseed.shop.views.testcookie'),
    (r'^cart/add/(.*)/$', 'dharmaseed.shop.views.addtocart'),
    (r'^cart/empty/$', 'dharmaseed.shop.views.emptycart'),
    (r'^cart/updatecart/$', 'dharmaseed.shop.views.updatecart'),
)
