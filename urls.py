from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.new_offer, name='new_offer'),
    url(r'^sign/(?P<pk>\d+)$', views.sign, name='sign'),
    url(r'^save-worker/(?P<pk>\d+)/(?P<worker_pk>\d+)$', views.save_worker, name='save_worker'),
    url(r'^search/$', views.search_offer, name='search_offer'),
    url(r'^offers/$', views.my_offer, name='my_offer'),
    url(r'^choose/(?P<pk>\d+)$', views.choose_worker, name='choose_worker'),
    url(r'^rate/(?P<pk>\d+)$', views.rate_user, name='rate_user'),
    url(r'^ranking/$', views.ranking, name='ranking'),
    url(r'^(?P<pk>\d+)/rank/$', views.personal_rank, name='personal_rank'),
    url(r'^(?P<pk>\d+)/(?P<yes_no>\d+)$', views.worker_accept, name='worker_accept'),
    url(r'^accounts/password/reset/$', auth_views.password_reset,
        {'post_reset_redirect': '/accounts/password/reset/done/',
         'template_name': 'registration/password_reset.html'},
        name="password_reset"),

    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done,
        {'template_name': 'registration/password_reset_done_custom.html'}),

    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect': '/accounts/password/done/',
         'template_name': 'registration/password_reset_confirm_custom.html'}, name='password_reset_confirm'),

    url(r'^accounts/password/done/$', auth_views.password_reset_complete,
        {'template_name': 'registration/password_reset_complete_custom.html'}),
    url(r'^accounts/password/change/$', auth_views.password_change,
        {'template_name': 'registration/password_change_form_custom.html'}, name='password_change'),
    url(r'^accounts/password/change/done/$', auth_views.password_change_done, name='password_change_done')
]
