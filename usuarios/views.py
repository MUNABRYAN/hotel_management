"""
Vistas de autenticación personalizadas con Bootstrap.
Usamos las vistas genéricas de Django y solo personalizamos el template.
"""
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy


class LoginViewPersonalizado(LoginView):
    """
    Login personalizado con template Bootstrap.
    Hereda TODO el comportamiento seguro de Django (CSRF, sesiones, etc.)
    Solo cambiamos el template y la URL de redirección.
    """
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True  # Si ya inició sesión, redirige al dashboard

    def get_success_url(self):
        """Después de login exitoso, ir al dashboard."""
        return reverse_lazy('hotel:dashboard')


class LogoutViewPersonalizado(LogoutView):
    """
    Logout que redirige al login.
    """
    next_page = reverse_lazy('usuarios:login')