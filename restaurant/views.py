from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from .models import MenuDelDia


class MenuDiaListView(LoginRequiredMixin, ListView):
    model = MenuDelDia
    template_name = 'restaurant/menu_dia.html'
    context_object_name = 'menus'
    ordering = ['-fecha']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hoy'] = timezone.now().date()
        return context


class CrearMenuView(LoginRequiredMixin, CreateView):
    model = MenuDelDia
    template_name = 'restaurant/form_menu.html'
    fields = ['nombre', 'fecha', 'precio', 'disponible']
    success_url = reverse_lazy('restaurant:menu_dia')