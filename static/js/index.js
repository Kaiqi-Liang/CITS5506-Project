const SERVER_URL = 'http://127.0.0.1:5000';
const unlockButton = document.getElementById('unlock')
const lock = document.querySelector('.lock')
const recordButton = document.getElementById('record');
const stop = document.getElementById('stop');
const soundClip = document.getElementById('sound-clip');
const recordIcon = document.getElementById('circle');
const main = document.querySelector('main');
const form = document.getElementById('form');
const logo = document.getElementById('logo');
const account = document.getElementById('account');
const edit = document.forms.edit;
const cancel = document.forms.edit.cancel;

const hideEditForm = () => {
	main.style.display = 'block';
	form.style.display = 'none';
};
logo.onclick = hideEditForm;
cancel.onclick = hideEditForm;

// If user has not yet logged in redirect to login page
const login = async () => {
	const data = new FormData();
	data.append('username', localStorage.getItem('username') || '');
	data.append('password', localStorage.getItem('password') || '');
	const res = await fetch(`${SERVER_URL}/login`, {
		method: 'POST',
		body: data,
	});
	if (!res.ok) location.href = 'login';
}
login();

// Alert the error message if backend returns a non 200 status code
const alertError = async (res) => {
	if (!res.ok) {
		const text = await res.text();
		alert(text);
	}
};

// Remote unlock the door
const unlock = async () => {
	const locked = () => {
		lock.classList.remove('unlocked');
		lock.addEventListener('click', unlock);
		lock.removeAttribute('disabled');
		unlockButton.removeAttribute('disabled');
	};
	if (confirm('Would you like to unlock the door?')) {
		setTimeout(() => {
			if (lock.hasAttribute('disabled')) locked();
		}, 3000);
		lock.classList.add('unlocked');
		lock.removeEventListener('click', unlock);
		lock.toggleAttribute('disabled');
		unlockButton.toggleAttribute('disabled');

		const res = await fetch(`${SERVER_URL}/unlock`);
		setTimeout(() => {
			alertError(res);
		}, 100);
		locked();
	}
};

// Unlock button and icon
unlockButton.onclick = unlock;
lock.addEventListener('click', unlock);

// Poll the backend every 5 seconds to check for updates
setInterval(async () => {
	const res = await fetch(`${SERVER_URL}/poll`);
	const text = await res.text();
	if (text === 'True') {
		const refresh = () => {
			const audio = document.querySelector('audio');
			audio.src = 'static/assets/out.wav';
			audio.src = 'static/assets/in.wav';

			document.querySelectorAll('img').forEach((img) => {
				const src = img.src;
				img.src = 'static/assets/spinner.svg';
				setTimeout(() => {
					img.src = src;
				}, 1000);
			});
		};

		// Play a doorbell ringing sound and send a notification to the browser
		new Audio('static/assets/doorbell.mp3').play();
		new Notification("Someone's at the door").onclick = refresh;

		// Refresh the audio and images then play the new audio after 2 seconds
		refresh();
		setTimeout(() => new Audio('static/assets/in.wav').play(), 2000);
	}
}, 5000);

// Delete the recorded audio section
const deleteClip = () => {
	while (soundClip.hasChildNodes()) {
		soundClip.removeChild(soundClip.firstChild);
	}
};

const startRecording = () => {
	navigator.mediaDevices.getUserMedia({ audio: true, video: false }).then((stream) => {
		// Start media stream
		const mediaRecorder = new MediaRecorder(stream);
		mediaRecorder.start();

		const stopRecording = () => {
			recordIcon.classList.remove('recording');
			recordIcon.onclick = startRecording;
			recordButton.innerText = 'Record';
			recordButton.toggleAttribute('disabled');
			stop.toggleAttribute('disabled');
			mediaRecorder.stop();
		};

		recordIcon.classList.add('recording');
		recordIcon.onclick = stopRecording;
		recordButton.innerText += 'ing...';
		recordButton.toggleAttribute('disabled');
		stop.toggleAttribute('disabled');
		stop.onclick = stopRecording;
		deleteClip();

		// Get audio data
		let data;
		mediaRecorder.ondataavailable = (event) => {
			data = event.data;
		};

		mediaRecorder.onstop = () => {
			// Create recording playback section
			const audio = document.createElement('audio');
			const buttons = document.createElement('div');
			const deleteButton = document.createElement('button');
			const sendButton = document.createElement('button');

			audio.setAttribute('controls', '');
			audio.className = 'space-above';
			buttons.className = 'space-above';
			deleteButton.innerHTML = 'Delete';
			sendButton.innerHTML = 'Send';

			soundClip.appendChild(audio);
			soundClip.appendChild(buttons);
			buttons.appendChild(sendButton);
			buttons.appendChild(deleteButton);

			// Convert audio data to a URL
			const blob = new Blob([data], { type: 'audio/wav' });
			const audioURL = window.URL.createObjectURL(blob);
			audio.src = audioURL;

			deleteButton.onclick = deleteClip;

			sendButton.onclick = async () => {
				sendButton.toggleAttribute('disabled');
				sendButton.innerText += 'ing...';
				const data = new FormData();
				data.append('audio', blob);
				const res = await fetch(`${SERVER_URL}/audio`, {
					method: 'POST',
					body: data,
				});
				alertError(res);
				sendButton.toggleAttribute('disabled');
				sendButton.innerHTML = 'Send';
			};
		};
	});
}

// Record button
recordButton.onclick = startRecording;
recordIcon.onclick = startRecording;

account.onclick = () => {
	main.style.display = 'none';
	form.style.display = 'block';
	edit.onsubmit = async (event) => {
		const username = edit.username.value;
		const password = edit.password.value;
		event.preventDefault();
		if (username && password) {
			const res = await fetch(`${SERVER_URL}/edit?username=${username}&password=${password}`);
			alertError(res);
			if (res.ok) location.reload();
		} else {
			alert('Please enter username and password');
		}
	}
};
