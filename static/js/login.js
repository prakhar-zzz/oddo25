document.querySelectorAll('.login-form input').forEach(input => {
  input.addEventListener('focus', () => {
    input.style.boxShadow = '0 0 8px rgba(76, 175, 80, 0.5)';
  });

  input.addEventListener('blur', () => {
    input.style.boxShadow = 'none';
  });
});
