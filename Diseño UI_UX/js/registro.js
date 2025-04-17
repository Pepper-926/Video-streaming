
document.addEventListener('DOMContentLoaded', function() {
    const showPasswordButtons = document.querySelectorAll('.show-password');
    showPasswordButtons.forEach(button => {
      button.addEventListener('click', function() {
        const input = this.parentElement.querySelector('input');
        const icon = this.querySelector('i');
        
        if (input.type === 'password') {
          input.type = 'text';
          icon.classList.replace('fa-eye', 'fa-eye-slash');
        } else {
          input.type = 'password';
          icon.classList.replace('fa-eye-slash', 'fa-eye');
        }
      });
    });
  
    const profilePhotoInput = document.getElementById('profile-photo');
    const profilePreview = document.getElementById('profile-preview');
    const profileImage = document.getElementById('profile-image');
    
    profilePhotoInput.addEventListener('change', function() {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
          profileImage.src = e.target.result;
          profileImage.style.display = 'block';
          profilePreview.querySelector('i').style.display = 'none';
        }
        
        reader.readAsDataURL(file);
      }
    });
  
    const passwordInput = document.getElementById('password');
    const passwordRequirements = document.querySelectorAll('.password-requirements li');
    
    passwordInput.addEventListener('input', function() {
      const value = this.value;
 
      toggleRequirementClass('length', value.length >= 8);

      toggleRequirementClass('uppercase', /[A-Z]/.test(value));
   
      toggleRequirementClass('number', /\d/.test(value));
      
      toggleRequirementClass('special', /[!@#$%^&*(),.?":{}|<>]/.test(value));
      a
      updateStrengthBar(value);
    });
    
    function toggleRequirementClass(type, isValid) {
      const requirement = document.querySelector(`.password-requirements li[data-requirement="${type}"]`);
      if (isValid) {
        requirement.classList.add('valid');
      } else {
        requirement.classList.remove('valid');
      }
    }
    
    function updateStrengthBar(password) {
      const strengthBar = document.querySelector('.strength-bar');
      const strengthText = document.querySelector('.strength-text');
      let strength = 0;
      
      if (password.length >= 8) strength += 25;
      if (password.length >= 12) strength += 15;
  
      if (/[A-Z]/.test(password)) strength += 20;
      if (/\d/.test(password)) strength += 20;
      if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength += 20;
    
      strength = Math.min(strength, 100);
    
      strengthBar.style.width = `${strength}%`;
      
      if (strength < 40) {
        strengthBar.style.backgroundColor = 'var(--error-color)';
        strengthText.textContent = 'Seguridad: débil';
      } else if (strength < 70) {
        strengthBar.style.backgroundColor = '#ffcc00';
        strengthText.textContent = 'Seguridad: media';
      } else {
        strengthBar.style.backgroundColor = 'var(--success-color)';
        strengthText.textContent = 'Seguridad: fuerte';
      }
    }
    

    const confirmPasswordInput = document.getElementById('confirm-password');
    
    confirmPasswordInput.addEventListener('input', function() {
      if (this.value !== passwordInput.value) {
        this.setCustomValidity('Las contraseñas no coinciden');
      } else {
        this.setCustomValidity('');
      }
    });
 
    const birthDateInput = document.getElementById('birth-date');
    
    birthDateInput.addEventListener('change', function() {
      const birthDate = new Date(this.value);
      const today = new Date();
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      
      if (age < 13) {
        this.setCustomValidity('Debes tener al menos 13 años para registrarte');
      } else {
        this.setCustomValidity('');
      }
    });
  });