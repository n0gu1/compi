import io
import base64
import bcrypt
import cloudinary.uploader
import uuid
from pathlib import Path

from django.conf import settings
from django.db import connections, OperationalError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import code128

from compiler import compile_text, compile_to_ast
from compiler.utils import flatten_ast
from .rover import execute
from .twilio_messenger import TwilioMessenger

twilio = TwilioMessenger()   # singleton sencillo

print(cloudinary.config().cloud_name)
# ─────────────────────  HELPER: crear_usuario  ──────────────────────
# vista.py
# ---------------------------------------------------------------------------
#  Crear usuario llamando al SP y CONFIRMANDO la transacción
# ---------------------------------------------------------------------------
def crear_usuario(nombre: str,
                  nickname: str,
                  password: str,
                  image_file,
                  correo: str,
                  telefono: str) -> str:
    """Invoca el SP insertar_usuario y devuelve el mensaje que este genere."""

    # ─── 1) hashear password ────────────────────────────────────────────────
    pwd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # ─── 2) imagen → base-64 (opcional) ─────────────────────────────────────
    img_b64 = ""
    if image_file:
        img_b64 = base64.b64encode(image_file.read()).decode()
        image_file.seek(0)         # por si la vuelves a leer más adelante

    try:
        # ─── 3) llamar al SP ────────────────────────────────────────────────
        with connections["mysql_remoto"].cursor() as cur:
            cur.execute("SET @resultado := ''")
            cur.execute(
                """
                CALL insertar_usuario(
                    %s,   -- nombre
                    %s,   -- nickname
                    %s,   -- password hash
                    %s,   -- avatar base64
                    %s,   -- correo
                    %s,   -- teléfono
                    @resultado
                )
                """,
                [nombre, nickname, pwd_hash, img_b64, correo, telefono],
            )

            # ⚠️  DIFERENCIA CLAVE: confirmar la transacción
            cur.connection.commit()              # <── nuevo

            cur.execute("SELECT @resultado")
            sp_msg = cur.fetchone()[0] or ""

        # si el SP devolvió algo, úsalo como respuesta
        if sp_msg:
            return sp_msg

        # ─── 4) verificación extra (opcional) ──────────────────────────────
        with connections["mysql_remoto"].cursor() as cur2:
            cur2.execute(
                "SELECT 1 FROM tb_usuarios WHERE nickname = %s LIMIT 1",
                [nickname],
            )
            if cur2.fetchone():
                return "Ha sido registrado exitosamente"

        # si no se insertó nada y el SP no dijo nada
        return "(SP no retornó mensaje y no se encontró registro)"

    except Exception as exc:
        return f"Error al invocar SP: {exc}"


# ─────────────── Función auxiliar para código de barras ────────────────
def generar_codigo_barra(valor: str) -> str:
    return base64.urlsafe_b64encode(valor.encode()).decode()

# ────────────────────────────────────────────────────────────────────

def index(request):
    return render(request, "index.html")

@require_GET
def dashboard(request):
    if request.session.get("id_rol") != 2:
        return HttpResponse("Acceso denegado", status=403)

    try:
        with connections["mysql_remoto"].cursor() as cur:
            cur.execute("""
                SELECT i.id_ingreso, u.nombre, u.avatar, i.fecha_ingreso, i.fecha_salida
                FROM tb_ingresos i
                JOIN tb_usuarios u ON i.id_usuario = u.id_usuario
                WHERE i.id_grupo = 6
                ORDER BY i.fecha_ingreso DESC
            """)
            rows = cur.fetchall()

        datos = [
            {
                "id": row[0],
                "nombre": row[1],
                "avatar": row[2],
                "ingreso": row[3],
                "salida": row[4],
            }
            for row in rows
        ]
        return render(request, "dashboard.html", {"datos": datos})

    except Exception as e:
        return HttpResponse(f"Error al cargar datos: {e}", status=500)

    try:
        with connections["mysql_remoto"].cursor() as cur:
            cur.execute("""
                SELECT i.id_ingreso, u.nombre, u.avatar, i.fecha_ingreso, i.fecha_salida
                FROM tb_ingresos i
                JOIN tb_usuarios u ON i.id_usuario = u.id_usuario
                WHERE i.id_grupo = 6
                ORDER BY i.fecha_ingreso DESC
            """)
            rows = cur.fetchall()

        datos = [
            {
                "id": row[0],
                "nombre": row[1],
                "avatar": row[2],
                "ingreso": row[3],
                "salida": row[4],
            }
            for row in rows
        ]
        return render(request, "dashboard.html", {"datos": datos})

    except Exception as e:
        return HttpResponse(f"Error al cargar datos: {e}", status=500)
    
@require_GET
def logout_view(request):
    nickname = request.session.get("nickname")
    if not nickname:
        return redirect("index")

    try:
        with connections["mysql_remoto"].cursor() as cur:
            # Obtener el id_usuario
            cur.execute("SELECT id_usuario FROM tb_usuarios WHERE nickname = %s", [nickname])
            row = cur.fetchone()
            if not row:
                request.session.flush()
                return redirect("index")

            id_usuario = row[0]

            # Obtener el ingreso más reciente sin salida para el grupo 6
            cur.execute("""
                SELECT id_ingreso
                FROM tb_ingresos
                WHERE id_usuario = %s AND id_grupo = 6 AND fecha_salida IS NULL
                ORDER BY fecha_ingreso DESC
                LIMIT 1
            """, [id_usuario])
            ingreso = cur.fetchone()

            if ingreso:
                id_ingreso = ingreso[0]
                cur.execute("SET @resultado = ''")
                cur.execute("CALL registrar_salida(%s, @resultado)", [id_ingreso])
                cur.execute("SELECT @resultado")
                print("🟢 Resultado al cerrar sesión:", cur.fetchone()[0])
    except Exception as e:
        print("⚠️ Error al registrar salida:", e)

    # Cerrar sesión
    request.session.flush()
    return redirect("index")


def editor(request):
    nickname = request.session.get("nickname")
    if not nickname:
        return redirect("index")
    return render(request, "editor.html", {"nickname": nickname})

def api_compile(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "msg": "Método no permitido"}, status=405)

    code = request.POST.get("code", "")
    ast = compile_to_ast(code)

    if ast is None:
        return JsonResponse({"status": "error", "msg": compile_text(code)})

    commands = flatten_ast(ast)
    return JsonResponse({"status": "ok", "commands": commands})

@require_POST
def registro_pdf(request):
    nombre     = request.POST.get("nombre", "").strip()
    nickname   = request.POST.get("nickname", "").strip()
    password   = request.POST.get("password", "").strip()
    correo     = request.POST.get("email",    "").strip()
    telefono   = request.POST.get("phone",    "").strip()
    image_file = request.FILES.get("profile_image")

    print("▶️ Datos recibidos:")
    print("nombre:", nombre)
    print("nickname:", nickname)
    print("password:", password)
    print("correo:", correo)
    print("telefono:", telefono)
    print("imagen:", image_file)

    resultado_sp = crear_usuario(nombre, nickname, password, image_file, correo, telefono)

    buffer = io.BytesIO()
    pdf    = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    fondo_path = finders.find("img/fondo_formulario.png")
    if not fondo_path:
        return HttpResponse("No se encontró la imagen de fondo", status=500)
    pdf.drawImage(ImageReader(fondo_path), 0, 0, width=width, height=height)

    if image_file:
        try:
            pil_img = Image.open(image_file).convert("RGB")
            img_buf = io.BytesIO()
            pil_img.save(img_buf, format="JPEG", quality=90)
            img_buf.seek(0)
            img = ImageReader(img_buf)

            ow, oh = pil_img.size
            ratio  = min(200/ow, 200/oh, 1)
            w, h   = ow*ratio, oh*ratio
            x, y   = width - w - 200, height - h - 185

            path = pdf.beginPath()
            path.circle(x+w/2, y+h/2, min(w, h)/2)
            pdf.saveState()
            pdf.clipPath(path, stroke=0, fill=1)
            pdf.drawImage(img, x, y, width=w, height=h, mask="auto")
            pdf.restoreState()
        except Exception as exc:
            print("⚠️ Imagen de perfil:", exc)

    hex2rgb = lambda h: tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))
    pdf.setFont("Helvetica-Bold", 100)
    pdf.setFillColorRGB(*hex2rgb("319bd1"))
    pdf.drawString(120, height-550, nickname)
    pdf.setFont("Helvetica-Bold", 17)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.drawString(205, height-611, correo)
    pdf.drawString(223, height-645, telefono)

    # ─── Código de barras ─────────────────────────────────────
    codigo_cifrado = generar_codigo_barra(nickname)
    barcode = code128.Code128(codigo_cifrado, barHeight=40, barWidth=1.2)
    barcode.drawOn(pdf, 240, 63)

    pdf.setFont("Helvetica", 10)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.drawCentredString(220, 120, codigo_cifrado)


    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    try:
        mail = EmailMessage(
            "Constancia de registro",
            f"Hola, {nickname}.\nAdjuntamos tu constancia en PDF.",
            settings.DEFAULT_FROM_EMAIL,
            [correo],
        )
        mail.attach("registro.pdf", buffer.getvalue(), "application/pdf")
        mail.send(fail_silently=False)
    except Exception as exc:
        print("⚠️ Correo:", exc)

        # ─── Subir PDF a Cloudinary con sufijo + .pdf y enviar WhatsApp ─────────────────────
    file_base = Path(nickname).stem or "registro"
    suffix    = uuid.uuid4().hex[:8]
    public_id = f"{file_base}_{suffix}.pdf"

    upload_res = cloudinary.uploader.upload(
        buffer.getvalue(),
        resource_type="raw",
        folder=settings.CLOUDINARY_FOLDER,
        public_id=public_id,
        overwrite=True,
        access_mode="public"            # ← línea añadida
    )
    pdf_url = upload_res["secure_url"]  # termina en .pdf
    print("📄 Cloudinary URL:", pdf_url)

    vars = {"1": nickname, "2": pdf_url}
    try:
        twilio.send_whatsapp_template(
            to_e164=f"+502{telefono}",
            content_sid=settings.TWILIO_TEMPLATE_SID,
            vars=vars,
            override_media_url=pdf_url     # ← fuerza la URL de Cloudinary
        )
    except Exception as e:
        print("⚠️ WhatsApp no enviado:", e)

    # Finalmente, devolver el PDF al navegador
    buffer.seek(0)
    res = HttpResponse(buffer, content_type="application/pdf")
    res["Content-Disposition"] = 'inline; filename="registro.pdf"'
    return res


@require_POST
def api_execute(request):
    code = request.POST.get("code", "")
    ast = compile_to_ast(code)
    if ast is None:
        return JsonResponse({"status": "error", "msg": compile_text(code)})
    steps = flatten_ast(ast)
    execute(steps)
    return JsonResponse({"status": "ok"})

@require_GET
def db_ping(request):
    try:
        with connections["mysql_remoto"].cursor() as cur:
            cur.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except OperationalError as exc:
        return JsonResponse({"status": "error", "msg": str(exc)})

@require_POST
def login_view(request):
    nickname = request.POST.get("nickname", "").strip()
    password = request.POST.get("password", "").strip()

    if not nickname or not password:
        return render(request, "index.html", {"login_error": "Faltan datos"})

    try:
        with connections["mysql_remoto"].cursor() as cur:
            # Obtener el hash de la contraseña y el rol
            cur.execute("SELECT id_usuario, password, id_rol FROM tb_usuarios WHERE nickname = %s", [nickname])
            row = cur.fetchone()

        if row is None:
            return render(request, "index.html", {"login_error": "Usuario no encontrado"})

        id_usuario, hashed_password, id_rol = row

        if bcrypt.checkpw(password.encode(), hashed_password.encode()):
            # Guardar sesión
            request.session["nickname"] = nickname
            request.session["id_rol"] = id_rol
            request.session["id_usuario"] = id_usuario

            # Registrar ingreso solo si no es admin (rol diferente de 2)
            if id_rol != 2:
                try:
                    with connections["mysql_remoto"].cursor() as cur2:
                        cur2.execute("SET @resultado = ''")
                        cur2.execute("CALL insertar_ingreso(%s, %s, @resultado)", [id_usuario, 6])
                        cur2.execute("SELECT @resultado")
                        resultado = cur2.fetchone()[0]
                        print("🟢 Ingreso registrado:", resultado)
                except Exception as ex:
                    print("⚠️ Error registrando ingreso:", ex)

            # Redirigir según el rol
            if id_rol == 2:
                return redirect("dashboard")
            else:
                return redirect("editor")
        else:
            return render(request, "index.html", {"login_error": "Contraseña incorrecta"})

    except Exception as e:
        return render(request, "index.html", {"login_error": f"Error: {e}"})
