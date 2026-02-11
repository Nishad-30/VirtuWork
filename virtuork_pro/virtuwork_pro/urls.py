"""
URL configuration for virtuwork_pro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
# virtuwork_pro/urls.py
from django.urls import path
from core import views as core_views
from simulation import views as sim_views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', core_views.landing_page, name='landing'),
    path('signup/', core_views.signup_view, name='signup'),
    path('login/', core_views.login_view, name='login'),
    
    # This is the missing piece:
    path('dashboard/', core_views.dashboard_view, name='dashboard'),
    path('how-it-works/', core_views.how_it_works, name='how_it_works'),
    # Simulation routes
    path('simulation/create/', sim_views.create_simulation, name='create_simulation'),
    path('simulation/delete/<int:sim_id>/', sim_views.delete_simulation, name='delete_simulation'),
    path('simulation/resume/<int:sim_id>/', sim_views.resume_simulation, name='resume_simulation'),
    
    # Auth
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    
    # API
    path('api/check-email/', core_views.check_email_exists, name='check_email'),
    path('simulation/chat/<int:simulation_id>/', sim_views.simulation_chat, name='simulation_chat'),
    path('simulation/send-message/', sim_views.send_message, name='send_message'),
    path('simulation/initiate-ai/<int:simulation_id>/', sim_views.initiate_ai_logic, name='initiate_ai'),
    path('simulation/submit-task/', sim_views.submit_task, name='submit_task'),
    path('send-message-ajax/', sim_views.send_message_ajax, name='send_message_ajax'),
    path('simulation/end-simulation-report/<int:simulation_id>/', sim_views.end_simulation_report, name='end_simulation_report'),
    
    path('profile/', sim_views.profile_view, name='profile'),
    path('certificate/<int:simulation_id>/', sim_views.certificate_view, name='certificate'),
    path('certificate/download/<int:sim_id>/', sim_views.download_certificate_pdf, name='download_certificate'),
]
