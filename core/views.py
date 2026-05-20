"""
Vistas genéricas para CRUDs de administración.
Principio DRY: Una sola implementación para todos los modelos.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from .models import CrudConfig


# =============================================================================
# FACTORY DE CRUDs
# =============================================================================

class GenericListView(LoginRequiredMixin, ListView):
    template_name = 'core/generic_list.html'
    paginate_by = 20
    config = None
    
    def get_queryset(self):
        return self.config.model.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = self.config
        context['campos'] = self.config.list_display
        return context


class GenericCreateView(LoginRequiredMixin, CreateView):
    template_name = 'core/generic_form.html'
    config = None
    
    def get_form_class(self):
        from core.forms import LocalizedModelForm
        class GenericForm(LocalizedModelForm):
            class Meta:
                model = self.config.model
                fields = self.config.fields if self.config.fields != '__all__' else '__all__'
        return GenericForm
    
    def get_success_url(self):
        return self.config.success_url
    
    def form_valid(self, form):
        messages.success(self.request, f'{self.config.titulo_singular} creado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = self.config
        context['modo'] = 'Crear'
        return context


class GenericUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'core/generic_form.html'
    config = None
    
    def get_queryset(self):
        return self.config.model.objects.all()
    
    def get_form_class(self):
        from core.forms import LocalizedModelForm
        class GenericForm(LocalizedModelForm):
            class Meta:
                model = self.config.model
                fields = self.config.fields if self.config.fields != '__all__' else '__all__'
        return GenericForm
    
    def get_success_url(self):
        return self.config.success_url
    
    def form_valid(self, form):
        messages.success(self.request, f'{self.config.titulo_singular} actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = self.config
        context['modo'] = 'Editar'
        return context


class GenericDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'core/generic_confirm_delete.html'
    config = None
    
    def get_queryset(self):
        return self.config.model.objects.all()
    
    def get_success_url(self):
        return self.config.success_url
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.warning(self.request, f'{self.config.titulo_singular} "{obj}" eliminado.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = self.config
        return context