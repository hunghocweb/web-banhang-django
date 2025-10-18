const passwordInput = document.getElementById("password-input");
const togglePassword = document.getElementById("toggle-password");
const toggleIcon = document.getElementById("toggle-icon");
togglePassword.addEventListener("click", () => {
    // Kiểm tra loại của input
    const isPassword = passwordInput.type === "password";

    // Chuyển đổi giữa password và text
    passwordInput.type = isPassword ? "text" : "password";

    // Đổi icon tương ứng
    toggleIcon.classList.toggle("bi-eye");
    toggleIcon.classList.toggle("bi-eye-slash");
    if (document.activeElement === togglePassword) {
      togglePassword.blur();
    } else {
      togglePassword.focus(); 
    }
});
