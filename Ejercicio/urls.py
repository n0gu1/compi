from django.urls import path
from Ejercicio.vista import (
    index,
    registro_pdf,
    editor,
    api_compile,
    api_execute,
    db_ping,
    login_view,
    dashboard,   
    logout_view    # ① importar aquí
)

urlpatterns = [
    path("admin/", editor, name="admin"),
    path("", index, name="index"),
    path("pdf/registro/", registro_pdf, name="registro_pdf"),
    path("editor/", editor, name="editor"),
    path("dashboard/", dashboard, name="dashboard"),  
    path("api/compile/", api_compile, name="api_compile"),
    path("api/execute/", api_execute, name="api_execute"),
    path("api/db_ping/", db_ping, name="api_db_ping"),
    path("login/", login_view, name="login_view"),
    path("logout/", logout_view, name="logout"),
]
