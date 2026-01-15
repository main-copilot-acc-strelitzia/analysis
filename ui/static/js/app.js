document.addEventListener('DOMContentLoaded', function(){
  const statusEl = document.getElementById('running');
  const connEl = document.getElementById('conn-status');
  const symbolSelect = document.getElementById('symbol');
  const startBtn = document.getElementById('start');
  const stopBtn = document.getElementById('stop');
  const connectBtn = document.getElementById('connect');
  const chartDiv = document.getElementById('chart');

  function safeFetch(path, opts){
    return fetch(path, opts).then(r=>r.json()).catch(e=>({error: String(e)}));
  }

  connectBtn.addEventListener('click', async ()=>{
    setConn('connecting');
    const r = await safeFetch('/connect', {method:'POST'});
    setConn(r.status === 'connected' ? 'connected' : 'not connected');
    if(r.status === 'connected'){
      const s = await safeFetch('/symbols');
      symbolSelect.innerHTML = '';
      (s.symbols || []).forEach(sym => {
        const opt = document.createElement('option'); opt.value = sym.name; opt.textContent = sym.name; symbolSelect.appendChild(opt);
      });
      // Fetch initial candles and render chart so user can view charts without starting engine
      try{
        const sym = symbolSelect.value || (s.symbols && s.symbols[0] && s.symbols[0].name) || '';
        if(sym){
          const c = await safeFetch(`/candles?symbol=${encodeURIComponent(sym)}&timeframe=${encodeURIComponent(document.getElementById('timeframe').value)}&count=200`);
          if(c && c.candles){ updateChartWithLive({candles: c.candles}); }
        }
      }catch(e){ console.warn('failed initial candles', e); }
    }
  });

  startBtn.addEventListener('click', async ()=>{
    const symbol = symbolSelect.value;
    const timeframe = document.getElementById('timeframe').value;
    const history_days = document.getElementById('history').value;
    const poll = document.getElementById('poll').value;
    const r = await safeFetch('/start', {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify({symbol, timeframe, history_days, poll_interval: poll})});
    setRunning(r.status || 'error');
  });

  stopBtn.addEventListener('click', async ()=>{
    const r = await safeFetch('/stop', {method:'POST'});
    setRunning(r.status || 'stopped');
  });

  // Initialize TradingView Lightweight Charts
  let chart = null;
  let candleSeries = null;
  function initChart(){
    const chartContainer = document.getElementById('chart-canvas');
    chart = LightweightCharts.createChart(chartContainer, {layout: {background: {color:'#05040a'}, textColor:'#9fa8b2'}, timeScale: {timeVisible: true, secondsVisible: false}});
    candleSeries = chart.addCandlestickSeries({upColor: '#26a69a', downColor: '#ef5350', borderUpColor: '#26a69a', borderDownColor: '#ef5350', wickUpColor: '#26a69a', wickDownColor: '#ef5350'});
    chart.timeScale().fitContent();
  }

  // Open WebSocket and handle live updates
  function initWebSocket(){
    const ws = new WebSocket(`ws://${location.host}/ws`);
    ws.onopen = ()=> console.log('ws open');
    ws.onmessage = function(evt){
      try{
        const msg = JSON.parse(evt.data);
        if(msg.type === 'analysis_update'){
          const res = msg.result;
          renderSignals(res);
          updateChartWithLive(res);
        }
      }catch(err){ console.error('ws msg', err); }
    };
    ws.onclose = ()=> console.log('ws closed');
  }

  function setRunning(status){
    const s = String(status).toLowerCase();
    statusEl.textContent = s;
    statusEl.classList.remove('badge-running','badge-stopped');
    if(s === 'connected' || s === 'running' || s === 'started'){
      statusEl.classList.add('badge-running');
    } else {
      statusEl.classList.add('badge-stopped');
    }
  }

  function setConn(status){
    const s = String(status).toLowerCase();
    connEl.textContent = s === 'connected' ? 'connected' : (s === 'connecting' ? 'connecting' : 'not connected');
    connEl.classList.remove('badge-running','badge-stopped');
    if(s === 'connected') connEl.classList.add('badge-running'); else connEl.classList.add('badge-stopped');
  }

  function renderSignals(res){
    const el = document.getElementById('signals');
    if(!res) return;
    const cur = res.analysis && res.analysis.current_analysis ? res.analysis.current_analysis : {};
    const hist = res.analysis && res.analysis.historical_structure_analysis ? res.analysis.historical_structure_analysis : {};
    el.innerHTML = `<pre>${JSON.stringify({confluence: res.confluence_score, rating: res.rating, current_count: Object.keys(cur).length, history_keys: Object.keys(hist)}, null, 2)}</pre>`;
    const statusEl2 = document.getElementById('setup_status');
    const status = res.setup_status || 'unknown';
    const dir = res.direction || 'neutral';
    const reason = res.reasoning || {};
    let color = '#555';
    if (status === 'valid') color = 'green'; else if (status === 'forming') color = 'orange'; else if (status === 'no_setup') color = 'red';
    statusEl2.innerHTML = `<strong>Status:</strong> <span style='color:${color}'>${status.toUpperCase()}</span> — <strong>Bias:</strong> ${dir.toUpperCase()} <br/><pre>${JSON.stringify(reason, null, 2)}</pre>`;
  }

  function renderChart(res){
    const raw = (res && res.raw_candles) || (res && res.analysis && res.analysis.current_analysis && res.analysis.current_analysis.raw_candles) || (res && res.candles);
    if(!raw || raw.length === 0) return;
    // Don't call updateChartWithLive to avoid recursion; chart will update on next WebSocket message
  }

  // Load Plotly via loader then init websocket
  // Initialize TradingView chart and WebSocket (wait for library to load)
  function initChartWhenReady(){
    if(typeof LightweightCharts === 'undefined'){
      setTimeout(initChartWhenReady, 500);
      return;
    }
    try{ initChart(); } catch(e){ console.error('chart init failed', e); }
  }
  initChartWhenReady();
  initWebSocket();

  function toCandlePoint(r){
    const ts = Math.floor(new Date(r.Timestamp || r.timestamp).getTime() / 1000);
    return {time: ts, open: r.Open != null ? r.Open : r.open, high: r.High != null ? r.High : r.high, low: r.Low != null ? r.Low : r.low, close: r.Close != null ? r.Close : r.close};
  }

  function updateChartWithLive(res){
    try{
      // Wait for LightweightCharts library to be available
      if(typeof LightweightCharts === 'undefined'){
        console.warn('LightweightCharts not yet loaded, retrying...');
        setTimeout(()=>updateChartWithLive(res), 500);
        return;
      }
      const raw = (res && res.raw_candles) || (res && res.analysis && res.analysis.current_analysis && res.analysis.current_analysis.raw_candles) || (res && res.candles) || [];
      if(!raw || raw.length === 0) return;
      if(!chart || !candleSeries){ initChart(); }
      if(!chart || !candleSeries) return;
      const data = raw.map(r => toCandlePoint(r));
      candleSeries.setData(data);
      chart.timeScale().fitContent();

      // Add entry/TP/SL overlay if analysis provides direction
      const dir = res && res.direction;
      if(dir && data.length > 0){
        const high = data.map(d=>d.high);
        const low = data.map(d=>d.low);
        const close = data.map(d=>d.close);
        const ranges = [];
        for(let i=Math.max(0, high.length-14); i<high.length; i++) ranges.push(Math.abs(high[i]-low[i]));
        const atr = ranges.length ? ranges.reduce((a,b)=>a+b,0)/ranges.length : 0;
        const entryPrice = close[close.length-1];
        let tp=null, sl=null;
        if(String(dir).toLowerCase().includes('bull')){ sl = entryPrice - atr*1.5; tp = entryPrice + atr*3; }
        else if(String(dir).toLowerCase().includes('bear')){ sl = entryPrice + atr*1.5; tp = entryPrice - atr*3; }
        
        // Add entry line (blue) - dashed
        candleSeries.createPriceLine({price: entryPrice, color: '#2dd4bf', lineStyle: 2, lineWidth: 2, title: 'Entry'});
        // Add TP line (green) - dotted
        if(tp!=null) candleSeries.createPriceLine({price: tp, color: '#26a69a', lineStyle: 3, lineWidth: 2, title: 'TP'});
        // Add SL line (red) - dotted
        if(sl!=null) candleSeries.createPriceLine({price: sl, color: '#ef5350', lineStyle: 3, lineWidth: 2, title: 'SL'});
      }
    }catch(e){ console.warn('updateChartWithLive', e); }
  }

});
