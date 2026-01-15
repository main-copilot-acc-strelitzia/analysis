"""FastAPI web UI exposing the continuous analysis dashboard and WebSocket updates."""
from __future__ import annotations

import os
import sys
import json
import threading
from typing import Any, Dict, List

# Ensure the project root (the `trader` folder) is on sys.path so imports like
# `analysis` and `mt5` resolve when running the webapp.
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(THIS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from analysis.engine import AnalysisEngine
from mt5.connector import MT5Connector
from core.logger import get_logger


class WebSocketManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: Dict[str, Any]):
        dead = []
        data = json.dumps(message, default=str)
        for ws in list(self.active):
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.disconnect(d)


app = FastAPI()
# Serve local static files (JS/CSS) for the web UI
static_dir = os.path.join(THIS_DIR, 'static')
if not os.path.exists(static_dir):
    try:
        os.makedirs(static_dir)
    except Exception:
        pass
app.mount('/static', StaticFiles(directory=static_dir), name='static')
logger = get_logger()
ws_mgr = WebSocketManager()
engine = AnalysisEngine()
connector = MT5Connector()
MAIN_LOOP = None


@app.on_event('startup')
async def _capture_loop():
    global MAIN_LOOP
    try:
        MAIN_LOOP = asyncio.get_event_loop()
        logger.debug('Captured main asyncio loop for cross-thread scheduling')
    except Exception:
        logger.exception('Failed to capture main loop')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    tpl_path = os.path.join(THIS_DIR, 'templates', 'index.html')
    if not os.path.exists(tpl_path):
        # Fallback to project-root relative path
        tpl_path = os.path.join(PROJECT_ROOT, 'ui', 'templates', 'index.html')
    html = open(tpl_path, 'r', encoding='utf-8').read()
    return HTMLResponse(html)


@app.get('/favicon.ico')
async def favicon():
    # Serve an existing image as favicon to avoid 404 noise
    cand = os.path.join(THIS_DIR, 'wxJWxaU6_big.png')
    if os.path.exists(cand):
        return FileResponse(cand, media_type='image/png')
    return FileResponse(os.path.join(THIS_DIR, 'static', 'css', 'styles.css'))


@app.post('/start')
async def start(payload: Dict[str, Any]):
    symbol = payload.get('symbol')
    timeframe = payload.get('timeframe')
    history_days = int(payload.get('history_days', 7))
    poll_interval = int(payload.get('poll_interval', 30))

    if not symbol or not timeframe:
        return {'status': 'error', 'detail': 'symbol and timeframe required'}

    def _cb(result):
        # Schedule broadcast in main event loop if available (safe from background thread)
        try:
            payload = {'type': 'analysis_update', 'result': result}
            if MAIN_LOOP is not None and MAIN_LOOP.is_running():
                try:
                    asyncio.run_coroutine_threadsafe(ws_mgr.broadcast(payload), MAIN_LOOP)
                except Exception:
                    logger.exception('Failed to schedule broadcast on main loop')
            else:
                # Fallback: try running directly (may block)
                try:
                    asyncio.run(ws_mgr.broadcast(payload))
                except Exception:
                    logger.exception('Failed to run broadcast coroutine')
        except Exception:
            logger.exception('Failed to broadcast update')

    # Start engine in background thread
    engine.start(symbol, timeframe, history_days=history_days, poll_interval=poll_interval, update_cb=_cb)
    return {'status': 'started', 'symbol': symbol, 'timeframe': timeframe}


@app.post('/connect')
async def connect():
    ok = connector.connect()
    if not ok:
        return {'status': 'error', 'detail': 'Failed to connect to MT5'}
    return {'status': 'connected'}


@app.get('/symbols')
async def symbols():
    syms = connector.get_symbols()
    return {'symbols': syms}


@app.get('/connection_status')
async def connection_status():
    try:
        return {'connected': bool(connector.is_connected())}
    except Exception:
        logger.exception('Failed to fetch connection status')
        return {'connected': False}


@app.get('/candles')
async def candles(symbol: str, timeframe: str = 'M15', count: int = 200):
    """Return recent candles for a symbol/timeframe (used by the UI to render charts).

    Tries cached data first, then fetches from MT5 if needed.
    """
    try:
        from mt5.market_data import MarketDataManager
        md = MarketDataManager()
        cached = md.get_cached_data(symbol, timeframe)
        if cached is not None and len(cached) > 0:
            df = cached.tail(count).copy()
        else:
            df = md.get_candles(symbol, timeframe, count)
            if df is None:
                return {'error': 'no_data'}
        df['Timestamp'] = df['Timestamp'].astype(str)
        return {'candles': df.to_dict(orient='records')}
    except Exception:
        logger.exception('Failed to return candles')
        return {'error': 'exception'}


@app.post('/stop')
async def stop():
    engine.stop()
    return {'status': 'stopped'}


@app.get('/status')
async def status():
    try:
        return {
            'running': bool(engine._thread is not None and engine._thread.is_alive()),
            'connected': bool(connector.is_connected())
        }
    except Exception:
        logger.exception('Failed to fetch status')
        return {'running': False, 'connected': False}


@app.websocket('/ws')
async def websocket_endpoint(ws: WebSocket):
    await ws_mgr.connect(ws)
    try:
        while True:
            # Keep connection alive; client may send pings or commands
            msg = await ws.receive_text()
            # No-op echo for now
            await ws.send_text(json.dumps({'type': 'echo', 'payload': msg}))
    except WebSocketDisconnect:
        ws_mgr.disconnect(ws)


def run(host: str = '0.0.0.0', port: int = 8000):
    # Run uvicorn in-process to make starting from python easy
    uvicorn.run(app, host=host, port=port, log_level='info')


if __name__ == '__main__':
    run()
