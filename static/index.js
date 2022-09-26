// Global variables
const SERVER_URL = 'http://127.0.0.1:5000';
const unlockButton = document.getElementById('unlock')
const record = document.getElementById('record');
const stop = document.getElementById('stop');
const soundClip = document.getElementById('sound-clip');

// Alert the error message if backend returns a non 200 status code
const alertError = async (res) => {
	if (!res.ok) {
		const text = await res.text();
		alert(text);
	}
};

// Remote unlock the door
unlockButton.onclick = async () => {
	if (confirm('Would you like to unlock the door?')) {
		unlockButton.toggleAttribute('disabled');
		const res = await fetch(`${SERVER_URL}/unlock`);
		alertError(res);
		unlockButton.toggleAttribute('disabled');
	}
};

// Poll the backend every 5 seconds to check for updates
setInterval(() => {
	fetch(`${SERVER_URL}/poll`).then((res) => res.text()).then((text) => {
		if (text === 'True') {
			// Play a doorbell ringing sound and send a notification to the browser
			new Audio('static/doorbell.mp3').play();
			new Notification("Someone's at the door").onclick = () => {
				// Refresh the audio
				const audio = document.querySelector('audio');
				audio.src = 'static/out.wav';
				audio.src = 'static/in.wav';

				// Reload the images
				document.querySelectorAll('img').forEach((img) => {
					const src = img.src;
					img.src = 'static/spinner.svg';
					setTimeout(() => {
						img.src = src;
					}, 1000);
				});
			};
		}
	});
}, 5000);

// Delete the recorded audio section
const deleteClip = () => {
	while (soundClip.hasChildNodes()) {
		soundClip.removeChild(soundClip.firstChild);
	}
};

// Record button
record.onclick = () => {
	navigator.mediaDevices
	.getUserMedia({ audio: true, video: false })
	.then((stream) => {
		// Start media stream
		const mediaRecorder = new MediaRecorder(stream);
		record.innerText += 'ing...';
		stop.toggleAttribute('disabled');
		record.toggleAttribute('disabled');
		deleteClip();
		mediaRecorder.start();

		// Stop button
		stop.onclick = () => {
			record.innerText = 'Record';
			stop.toggleAttribute('disabled');
			record.toggleAttribute('disabled');
			mediaRecorder.stop();
		};

		// Add data
		let chunks = [];
		mediaRecorder.ondataavailable = (e) => {
			chunks.push(e.data);
		};

		// Data to sound file
		mediaRecorder.onstop = () => {
			// Create elements
			const audio = document.createElement('audio');
			const buttons = document.createElement('div');
			const deleteButton = document.createElement('button');
			const sendButton = document.createElement('button');

			audio.setAttribute('controls', '');
			audio.className = 'space-above';
			buttons.className = 'space-above';
			deleteButton.innerHTML = 'Delete';
			sendButton.innerHTML = 'Send';

			// Append elements
			soundClip.appendChild(audio);
			soundClip.appendChild(buttons);
			buttons.appendChild(sendButton);
			buttons.appendChild(deleteButton);

			// Create blob
			const blob = new Blob(chunks, { type: 'audio/wav' });
			chunks = [];
			const audioURL = window.URL.createObjectURL(blob);
			audio.src = audioURL;

			// Delete button
			deleteButton.onclick = deleteClip;

			// Send button
			sendButton.onclick = async () => {
				const data = new FormData();
				data.append('audio', blob);
				const res = await fetch(`${SERVER_URL}/audio`, {
					method: 'POST',
					body: data,
				});
				alertError(res);
			};
		};
	})
	.catch((err) => {
		alertError(err);
	});
};