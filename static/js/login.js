const SERVER_URL = 'http://127.0.0.1:5000';
const form = document.forms.login;

// If user has already logged in redirect to home page
const login = async () => {
	const data = new FormData();
	data.append('username', localStorage.getItem('username') || '');
	data.append('password', localStorage.getItem('password') || '');
	const res = await fetch(`${SERVER_URL}/login`, {
		method: 'POST',
		body: data,
	});
	if (res.ok) location.href = '/';
}
login();

form.onsubmit = async (event) => {
	event.preventDefault();
	const username = form.username.value;
	const password = form.password.value;
	const data = new FormData();
	data.append('username', username);
	data.append('password', password);
	const res = await fetch(`${SERVER_URL}/login`, {
		method: 'POST',
		body: data,
	});
	if (!res.ok) {
		const text = await res.text();
		alert(text);
	} else {
		localStorage.setItem('username', username);
		localStorage.setItem('password', password);
		location.href = '/';
	}
};
