const openDocs = document.getElementById('open-docs');
const openApp = document.getElementById('open-app');

openDocs.addEventListener('click', () => {
  chrome.tabs.create({ url: 'https://github.com/' });
});

openApp.addEventListener('click', () => {
  window.alert('Install the desktop app and run the launcher script from the repo before using this helper.');
});
