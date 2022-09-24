const SERVER_URL = 'http://127.0.0.1:5000';
document.getElementById('unlock').onclick = () => fetch(`${SERVER_URL}unlock`);

setInterval(() => {
	fetch(`${SERVER_URL}/poll`).then((res) => res.text()).then((text) => {
		if (text === 'True') {
			new Notification("Someone's at the door");
			// TODO refresh the images and recording
			// location.reload();
		} else {
			console.log(text);
		}
	});
}, 5000);

const handleSuccess = (stream) => {
	const record = document.getElementById('record');
	const stop = document.getElementById('stop');
	const soundClips = document.getElementById('sound-clips');

	const mediaRecorder = new MediaRecorder(stream);
	let chunks = [];

	// Record button
	record.onclick = () => {
		mediaRecorder.start();
		console.log(mediaRecorder.state);
	};

	// Stop button
	stop.onclick = () => {
		mediaRecorder.stop();
		console.log(mediaRecorder.state);
	};

	// Add data
	mediaRecorder.ondataavailable = (e) => {
		chunks.push(e.data);
	};

	// Data to sound file
	mediaRecorder.onstop = (e) => {
		const audio = document.createElement('audio');
		const deleteButton = document.createElement('button');
		const sendButton = document.createElement('button');

		audio.setAttribute('controls', '');
		deleteButton.innerHTML = 'Delete';
		sendButton.innerHTML = 'Send';

		soundClips.appendChild(audio);
		soundClips.appendChild(deleteButton);
		soundClips.appendChild(sendButton);

		const blob = new Blob(chunks, { type: 'audio/wav' });
		chunks = [];
		const audioURL = window.URL.createObjectURL(blob);
		audio.src = audioURL;

		// Delete button
		deleteButton.onclick = (event) => {
			let target = event.target;
			target.parentNode.parentNode.removeChild(target.parentNode);
		};

		// Send button
		sendButton.onclick = () => {
			const data = new FormData();
			data.append('audio', blob);
			fetch(`${SERVER_URL}/audio`, {
				method: 'POST',
				body: data,
			});
		}
	};
};

navigator.mediaDevices
	.getUserMedia({ audio: true, video: false })
	.then(handleSuccess);
