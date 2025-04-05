// Retrieve the JWT token from localStorage.
function getJwtToken() {
    return localStorage.getItem('jwtToken');
  }
  
  // Save the JWT token to localStorage.
  function setJwtToken(token) {
    localStorage.setItem('jwtToken', token);
  }
  
  // Remove the JWT token from localStorage.
  function removeJwtToken() {
    localStorage.removeItem('jwtToken');
  }
  
  // Attach Authorization header to fetch options if a token exists.
  function withAuth(options = {}) {
    const token = getJwtToken();
    if (!options.headers) {
      options.headers = {};
    }
    if (token) {
      options.headers['Authorization'] = 'Bearer ' + token;
    }
    return options;
  }
  
  // Logout functionality: if an element with ID "logoutLink" exists, attach event.
  document.addEventListener('DOMContentLoaded', function() {
    const logoutLink = document.getElementById('logoutLink');
    if (logoutLink) {
      logoutLink.addEventListener('click', function(e) {
        e.preventDefault();
        removeJwtToken();
        window.location.href = '/login';
      });
    }
  });
  