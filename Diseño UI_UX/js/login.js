
document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('loginForm');
  const showPasswordBtn = document.querySelector('.show-password');
  const passwordInput = document.getElementById('password');
  

  const rootStyles = getComputedStyle(document.documentElement);
  const primaryColor = rootStyles.getPropertyValue('--primary').trim();
  const grayTextColor = rootStyles.getPropertyValue('--gray-text').trim();

  showPasswordBtn.addEventListener('click', function() {
    const icon = this.querySelector('i');
    if (passwordInput.type === 'password') {
      passwordInput.type = 'text';
      icon.classList.replace('fa-eye', 'fa-eye-slash');
      this.setAttribute('aria-label', 'Ocultar contraseña');
    } else {
      passwordInput.type = 'password';
      icon.classList.replace('fa-eye-slash', 'fa-eye');
      this.setAttribute('aria-label', 'Mostrar contraseña');
    }
  });

  loginForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = passwordInput.value.trim();
    
    if (!email || !password) {
      showError('Por favor completa todos los campos');
      return;
    }
    
    if (!validateEmail(email)) {
      showError('Ingresa un correo electrónico válido');
      return;
    }

    simulateLogin(email, password);
  });

  const inputs = document.querySelectorAll('input');
  inputs.forEach(input => {
    const icon = input.parentElement.querySelector('i');
    
    input.addEventListener('focus', function() {
      icon.style.color = primaryColor;
      this.parentElement.style.borderColor = primaryColor;
    });
    
    input.addEventListener('blur', function() {
      icon.style.color = grayTextColor;
      this.parentElement.style.borderColor = '';
    });
  });


  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  function showError(message) {
    alert(message); 
  }

  function simulateLogin(email, password) {
    console.log('Simulando login con:', { email, password });

    setTimeout(() => {
      alert('Inicio de sesión exitoso (simulado)');
    }, 1500);
  }
});