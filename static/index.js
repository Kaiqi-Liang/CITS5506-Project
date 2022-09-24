const SERVER_URL = 'http://127.0.0.1:5000';
const unlockButton = document.getElementById('unlock')
const alertError = async (res) => {
	if (!res.ok) {
		const text = await res.text();
		alert(text);
	}
};
unlockButton.onclick = async () => {
	unlockButton.toggleAttribute('disabled');
	const res = await fetch(`${SERVER_URL}/unlock`);
	alertError(res);
	unlockButton.toggleAttribute('disabled');
};

setInterval(() => {
	fetch(`${SERVER_URL}/poll`).then((res) => res.text()).then((text) => {
		if (text === 'True') {
			const notification = new Notification("Someone's at the door");
			notification.onclick = () => location.reload();
		}
	});
}, 5000);

const handleSuccess = (stream) => {
	const record = document.getElementById('record');
	const stop = document.getElementById('stop');
	const mediaRecorder = new MediaRecorder(stream);
	const soundClip = document.getElementById('sound-clip');
	const deleteClip = () => {
		while (soundClip.hasChildNodes()) {
			soundClip.removeChild(soundClip.firstChild);
		}
	};

	// Record button
	record.onclick = () => {
		stop.toggleAttribute('disabled');
		record.toggleAttribute('disabled');
		deleteClip();
		mediaRecorder.start();
	};

	// Stop button
	stop.onclick = () => {
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
		const audio = document.createElement('audio');
		const deleteButton = document.createElement('button');
		const sendButton = document.createElement('button');

		audio.setAttribute('controls', '');
		deleteButton.innerHTML = 'Delete';
		sendButton.innerHTML = 'Send';

		soundClip.appendChild(audio);
		soundClip.appendChild(sendButton);
		soundClip.appendChild(deleteButton);

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
};

navigator.mediaDevices
	.getUserMedia({ audio: true, video: false })
	.then(handleSuccess);
