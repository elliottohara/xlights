(() => {
  const dialog = document.querySelector('#elf-card');
  const talk = document.querySelector('#pip-talk');
  const line = document.querySelector('#elf-line');
  const mouth = document.querySelector('#pip-mouth');
  const smile = document.querySelector('#pip-smile');
  const requestPanel = document.querySelector('#pip-request');
  const requestTitle = document.querySelector('#pip-request-title');
  const requestYes = document.querySelector('#pip-request-yes');
  const requestNo = document.querySelector('#pip-request-no');
  let turn;

  function toolResult(session, callId, result) {
    send(session, 'conversation.item.create', {item: {
      type: 'function_call_output', call_id: callId, output: JSON.stringify(result),
    }});
    send(session, 'response.create');
  }

  async function confirmSong(confirmed) {
    const session = turn;
    const pending = session?.request;
    if (!pending) return;
    session.request = undefined;
    requestPanel.hidden = true;
    let result = {message: 'The visitor canceled the request.'};
    if (confirmed) {
      try {
        const response = await fetch('/request', {
          method: 'POST', headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({seqId: pending.song.seqId}),
        });
        const data = await response.json();
        result = {accepted: response.status === 202, message: data.message, title: pending.song.title};
        if (result.accepted) {
          localStorage.setItem('last-request', JSON.stringify({...data, title: result.title, status: 'received'}));
        }
      } catch {
        result = {message: 'Could not confirm the queue received the request.'};
      }
    }
    if (turn === session && session.socket.readyState === WebSocket.OPEN) toolResult(session, pending.callId, result);
  }

  requestYes.onclick = () => confirmSong(true);
  requestNo.onclick = () => confirmSong(false);

  function finish(message) {
    if (!turn) return;
    const previous = turn;
    turn = undefined;
    requestPanel.hidden = true;
    dialog.classList.remove('chatting');
    clearTimeout(previous.timer);
    previous.stream?.getTracks().forEach(track => track.stop());
    previous.socket?.close();
    previous.audio.close().catch(() => {});
    mouth.style.visibility = 'hidden';
    smile.style.visibility = '';
    talk.textContent = 'Talk to Pip';
    talk.disabled = false;
    if (message) line.textContent = message;
  }

  function send(session, type, fields = {}) {
    session.socket.send(JSON.stringify({type, ...fields}));
  }

  function animate(session) {
    if (turn !== session) return;
    const playing = session.audio.currentTime < session.nextAudio;
    session.analyser.getFloatTimeDomainData(session.samples);
    const level = Math.sqrt(session.samples.reduce((sum, value) => sum + value * value, 0) / session.samples.length);
    mouth.style.visibility = playing ? 'visible' : 'hidden';
    smile.style.visibility = playing ? 'hidden' : '';
    mouth.setAttribute('ry', Math.min(10, 1 + level * 40));
    if (session.replyDone && !playing && !session.interrupted) {
      session.replyDone = false;
      line.textContent = 'I’m listening!';
    }
    requestAnimationFrame(() => animate(session));
  }

  function handle(session, event) {
    if (turn !== session) return;
    const data = JSON.parse(event.data);
    if (data.type === 'session.created') {
      const format = {type: 'audio/pcm', rate: 24000};
      send(session, 'session.update', {session: {
        voice: 'iris', turn_detection: {type: 'server_vad', silence_duration_ms: 400, create_response: true, interrupt_response: true},
        instructions: 'You are Pip Peppermint, a playful elf at the O’Hara Family Light Show. Speak like a friendly kid in one or two short, family-friendly sentences. Use the public show facts below. If you don’t know, say so. Never ask for names, contact details, or other personal information. You have no guest profiles or past conversations. When asked what can play or what is playing, use the show snapshot below. For a clear song request, call request_song with the exact catalog title. If there are several matches, ask which one. The screen asks for confirmation. Say it was requested only after the tool confirms acceptance. A request goes into the shared queue and does not interrupt the current song. Public show context: ' + JSON.stringify(session.context),
        tools: [{
          type: 'function', name: 'request_song',
          description: 'Offer a matching available song for the visitor to confirm on screen.',
          parameters: {type: 'object', properties: {title: {type: 'string'}}, required: ['title']},
        }],
        audio: {input: {format}, output: {format}},
      }});
    } else if (data.type === 'session.updated' && session.stream && !session.recording) {
      session.recording = true;
      session.source = session.audio.createMediaStreamSource(session.stream);
      session.processor = session.audio.createScriptProcessor(2048, 1, 1);
      session.processor.onaudioprocess = audioEvent => {
        if (!session.recording || turn !== session) return;
        const samples = audioEvent.inputBuffer.getChannelData(0);
        const pcm = new DataView(new ArrayBuffer(samples.length * 2));
        samples.forEach((sample, index) => pcm.setInt16(index * 2, Math.max(-1, Math.min(1, sample)) * 32767, true));
        send(session, 'input_audio_buffer.append', {audio: btoa(String.fromCharCode(...new Uint8Array(pcm.buffer)))});

      };
      session.source.connect(session.processor);
      session.processor.connect(session.audio.destination);
      line.textContent = 'I’m listening!';
      talk.textContent = 'End chat';
      talk.disabled = false;
      clearTimeout(session.timer);
      session.timer = setTimeout(() => finish('Thanks for chatting!'), 120000);
    } else if (data.type === 'input_audio_buffer.speech_started') {
      for (const source of session.sources) source.stop();
      session.sources.clear();
      session.nextAudio = 0;
      session.interrupted = true;
      line.textContent = 'I’m listening!';
    } else if (data.type === 'input_audio_buffer.speech_stopped') {
      line.textContent = 'Pip is thinking…';
    } else if (data.type === 'response.created') {
      session.interrupted = false;
      session.replyDone = false;
      session.responseId = data.response?.id;
    } else if (data.type === 'response.output_audio.delta' || data.type === 'response.audio.delta') {
      if (session.interrupted || (session.responseId && data.response_id && data.response_id !== session.responseId)) return;
      const bytes = Uint8Array.from(atob(data.delta), char => char.charCodeAt(0));
      const pcm = new DataView(bytes.buffer);
      const buffer = session.audio.createBuffer(1, bytes.length / 2, 24000);
      const channel = buffer.getChannelData(0);
      for (let i = 0; i < channel.length; i++) channel[i] = pcm.getInt16(i * 2, true) / 32768;
      const source = session.audio.createBufferSource();
      source.buffer = buffer;
      source.connect(session.analyser);
      const start = Math.max(session.audio.currentTime + .035, session.nextAudio);
      session.sources.add(source);
      source.onended = () => session.sources.delete(source);
      source.start(start);
      session.nextAudio = start + buffer.duration;
      line.textContent = 'Pip is talking…';
    } else if (data.type === 'response.function_call_arguments.done' && data.name === 'request_song') {
      let title;
      try { title = JSON.parse(data.arguments).title; } catch {}
      const song = session.context.live.songs.find(item => item.title === title);
      if (!session.context.live.open || !song || session.request) {
        toolResult(session, data.call_id, {accepted: false, message: session.context.live.open
          ? 'That song could not be selected.' : 'Requests open during the show.'});
        return;
      }
      session.request = {song, callId: data.call_id};
      requestTitle.textContent = 'Add ' + song.title + ' to the show queue?';
      requestPanel.hidden = false;
    } else if (data.type === 'response.done') {
      session.replyDone = true;
    } else if (data.type === 'error') {
      finish('Pip lost his train of thought. Try again!');
    }
  }

  talk.onclick = async () => {
    if (turn?.recording) {
      finish('Thanks for chatting!');
      return;
    }
    if (turn) return;
    const audio = new AudioContext({sampleRate: 24000});
    const session = {audio, sources: new Set(), nextAudio: 0, analyser: audio.createAnalyser()};
    session.samples = new Float32Array(session.analyser.fftSize);
    session.analyser.connect(audio.destination);
    turn = session;
    dialog.classList.add('chatting');
    talk.disabled = true;
    line.textContent = 'Getting Pip ready…';
    try {
      await audio.resume();
      const [response, context] = await Promise.all([
        fetch('/pip/session', {method: 'POST', signal: AbortSignal.timeout(10000)}),
        fetch('/pip/context', {signal: AbortSignal.timeout(12000)}).then(result => result.json()),
      ]);
      session.context = context;
      const result = await response.json();
      if (turn !== session) return;
      if (!response.ok) throw Error(result.message);
      const stream = await navigator.mediaDevices.getUserMedia({audio: {echoCancellation: true}});
      if (turn !== session) {
        stream.getTracks().forEach(track => track.stop());
        return;
      }
      session.stream = stream;
      session.socket = new WebSocket('wss://api.x.ai/v1/realtime', ['xai-client-secret.' + result.token]);
      session.socket.onmessage = event => handle(session, event);
      session.socket.onclose = () => { if (turn === session) finish('Pip got disconnected. Try again!'); };
      session.timer = setTimeout(() => finish('Pip couldn’t connect. Try again!'), 10000);
      animate(session);
    } catch (error) {
      if (turn === session) finish(error.name === 'NotAllowedError' ? 'Allow the microphone to talk to Pip.' : error.message);
    }
  };
  dialog.addEventListener('close', () => finish());
  addEventListener('pagehide', () => finish());
})();
