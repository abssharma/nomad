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

// Logout functionality: attach event to element with ID "logoutLink"
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

// ---------------------
// Voice Recording Code (Toggle on click)
// ---------------------
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
const recordButton = document.getElementById('recordButton');

if (recordButton) {
  recordButton.addEventListener('click', async () => {
    if (!isRecording) {
      // Start recording
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Audio recording not supported in your browser.");
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        mediaRecorder.ondataavailable = event => {
          console.log("Data available:", event.data.size, "bytes");
          audioChunks.push(event.data);
        };
        mediaRecorder.start();
        console.log("Recording started");
        recordButton.textContent = "Stop Recording";
        isRecording = true;
      } catch (err) {
        console.error("Error accessing microphone:", err);
        alert("Could not access microphone.");
      }
    } else {
      // Stop recording
      if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
          console.log("Recorded audio blob size:", audioBlob.size, "bytes");
          if (audioBlob.size === 0) {
            console.error("Audio blob is empty");
          }
          const reader = new FileReader();
          reader.onloadend = function() {
            const base64Audio = reader.result;
            console.log("Base64 audio length:", base64Audio.length);
            const recordedAudioField = document.getElementById('recordedAudio');
            if (recordedAudioField) {
              recordedAudioField.value = base64Audio;
            }
            recordButton.textContent = "Hold to Record";
            isRecording = false;
          };
          reader.readAsDataURL(audioBlob);
        };
        mediaRecorder.stop();
        console.log("Recording stopped");
      }
    }
  });
}

// ---------------------
// Geolocation Code
// ---------------------
const geoButton = document.getElementById('geoButton');
if (geoButton) {
  geoButton.addEventListener('click', () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        document.getElementById('lat').value = position.coords.latitude;
        document.getElementById('lon').value = position.coords.longitude;
        alert("Location acquired: " + position.coords.latitude + ", " + position.coords.longitude);
      }, (error) => {
        console.error("Error getting location:", error);
        alert("Unable to retrieve your location.");
      });
    } else {
      alert("Geolocation is not supported by your browser.");
    }
  });
}
