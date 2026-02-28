"""
URL configuration for aicteapproval project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('vvit/download-excel/',  DownloadInstitutionExcelView.as_view()), 
    # Authority
    path('vvit/register/',           RegisterView.as_view()),
    path('vvit/login/',              LoginView.as_view()),
    path('vvit/authority/login/',    AuthorityLoginView.as_view()),

    # ── Institution ───────────────────────────────────────────────────────────
    path('vvit/upload/',             UploadDisclosureView.as_view()),
    path('vvit/submit-approval/',    SubmitApprovalView.as_view()),
    path('vvit/approval-status/',    ApprovalStatusView.as_view()),
    path('vvit/dashboard/',          DashboardView.as_view()),
    path('vvit/disclosures/',        DisclosuresListView.as_view()),
    path('vvit/notifications/',      NotificationsView.as_view()),
    path('vvit/ai-risk/',            AIRiskView.as_view()),

    # ── Authority ─────────────────────────────────────────────────────────────
    path('vvit/authority/pending/',  AuthorityPendingApprovalsView.as_view()),
    path('vvit/authority/review/',   AuthorityReviewView.as_view()),
    path('vvit/authority/all/',      AuthorityAllInstitutionsView.as_view()),
    path('vvit/authority/stats/',    AuthorityStatsView.as_view()),
]
