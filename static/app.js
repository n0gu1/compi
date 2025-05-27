/* app.js */
console.log("app.js cargado correctamente");

document.addEventListener("DOMContentLoaded", () => {
  // —— Cambio de paneles ——
  const signInBtn = document.querySelector("#sign-in-btn");
  const signUpBtn = document.querySelector("#sign-up-btn");
  const container = document.querySelector(".container");
  signUpBtn.addEventListener("click", () => container.classList.add("sign-up-mode"));
  signInBtn.addEventListener("click", () => container.classList.remove("sign-up-mode"));

document.getElementById("signup-form").addEventListener("submit", function (e) {
  const fileInput = document.getElementById("file-input");

  if (!fileInput.files || fileInput.files.length === 0) {
    e.preventDefault();  // cancela el envío del formulario
    alert("⚠️ Debes subir una imagen o tomar una foto antes de registrarte.");
  }
});

  
  // —— Validaciones de registro ——
  const fields = {
    nickname: document.getElementById("reg-nickname"),
    email: document.getElementById("reg-email"),
    emailConfirm: document.getElementById("reg-email-confirm"),
    phone: document.getElementById("reg-phone"),
    phoneConfirm: document.getElementById("reg-phone-confirm"),
    password: document.getElementById("reg-password"),
    passwordConfirm: document.getElementById("reg-password-confirm"),
  };
  const errors = {
    nickname: document.getElementById("error-nickname"),
    email: document.getElementById("error-email"),
    emailConfirm: document.getElementById("error-email-confirm"),
    phone: document.getElementById("error-phone"),
    phoneConfirm: document.getElementById("error-phone-confirm"),
    password: document.getElementById("error-password"),
    passwordConfirm: document.getElementById("error-password-confirm"),
  };
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const phoneRegex = /^\d{8}$/;

  function showError(key, msg) {
    fields[key].classList.add("input-error");
    errors[key].textContent = msg;
    errors[key].classList.add("error-visible");
  }
  function clearError(key) {
    fields[key].classList.remove("input-error");
    errors[key].textContent = "";
    errors[key].classList.remove("error-visible");
  }

  function validarNickname() {
    fields.nickname.value.trim() ? clearError("nickname")
                                 : showError("nickname", "Nickname obligatorio");
  }
  function validarEmail() {
    emailRegex.test(fields.email.value.trim()) ? clearError("email")
                                               : showError("email", "Correo inválido");
    validarEmailConfirm();
  }
  function validarEmailConfirm() {
    fields.emailConfirm.value.trim() === fields.email.value.trim()
      ? clearError("emailConfirm")
      : showError("emailConfirm", "Los correos no coinciden");
  }
  function validarPhone() {
    phoneRegex.test(fields.phone.value.trim()) ? clearError("phone")
                                               : showError("phone", "Debe tener 8 dígitos");
    validarPhoneConfirm();
  }
  function validarPhoneConfirm() {
    fields.phoneConfirm.value.trim() === fields.phone.value.trim()
      ? clearError("phoneConfirm")
      : showError("phoneConfirm", "Los teléfonos no coinciden");
  }
  function validarPassword() {
    fields.password.value.length >= 6 ? clearError("password")
                                      : showError("password", "Mínimo 6 caracteres");
    validarPasswordConfirm();
  }
  function validarPasswordConfirm() {
    fields.passwordConfirm.value === fields.password.value
      ? clearError("passwordConfirm")
      : showError("passwordConfirm", "Las contraseñas no coinciden");
  }

  // Eventos de validación
  fields.nickname.addEventListener("input", validarNickname);
  fields.email.addEventListener("input", validarEmail);
  fields.emailConfirm.addEventListener("input", validarEmailConfirm);
  fields.phone.addEventListener("input", validarPhone);
  fields.phoneConfirm.addEventListener("input", validarPhoneConfirm);
  fields.password.addEventListener("input", validarPassword);
  fields.passwordConfirm.addEventListener("input", validarPasswordConfirm);

  // Solo dígitos en teléfono
  [fields.phone, fields.phoneConfirm].forEach(inp => {
    inp.addEventListener("input", () => inp.value = inp.value.replace(/\D/g,""));
  });

  // Validar antes de enviar
  document.getElementById("signup-form").addEventListener("submit", e => {
    validarNickname(); validarEmail(); validarEmailConfirm();
    validarPhone();    validarPhoneConfirm();
    validarPassword(); validarPasswordConfirm();
    const hayErrores = Object.values(errors).some(span => span.textContent !== "");
    if (hayErrores) e.preventDefault();
  });

  // —— Subida de imagen ——
  const fileInput = document.getElementById("file-input");
  fileInput.addEventListener("change", e => {
    const file = e.target.files[0];
    if (!file) return;
    console.log("Imagen seleccionada:", file.name);
    // Aquí podrías previsualizarla si lo deseas
  });

  // —— Lógica cámara (opcional) ——
  // …
});
