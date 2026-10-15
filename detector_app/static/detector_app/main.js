async function apiFetch(path, method='GET'){
  const res = await fetch(path, {method: method});
  return await res.json();
}

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const runningSpan = document.getElementById('running');
const msg = document.getElementById('msg');

startBtn.onclick = async () => {
  msg.textContent = 'Starting...';
  const res = await apiFetch('/api/start/', 'POST');
  if (res.error){ msg.textContent = 'Error: ' + res.error; }
  else if (res.started){ msg.textContent='Started'; }
  else { msg.textContent = 'Already running'; }
  updateStatus();
}

stopBtn.onclick = async () => {
  msg.textContent = 'Stopping...';
  const res = await apiFetch('/api/stop/', 'POST');
  if (res.stopped){ msg.textContent = 'Stopped'; }
  else { msg.textContent = 'Was not running'; }
  updateStatus();
}

async function updateStatus(){
  try{
    const s = await apiFetch('/api/status/');
    runningSpan.textContent = s.running ? 'Running' : 'Stopped';
  }catch(e){ runningSpan.textContent = 'Unknown'; }
}

setInterval(updateStatus, 2000);
updateStatus();
