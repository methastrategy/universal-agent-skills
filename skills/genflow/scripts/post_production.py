"""
Post-Production & Assembly Engine for /genflow
Features:
- Alpha channel cutout & edge feathering for stickers & character overlays
- Automated Ken Burns Animatic MP4 compilation via FFmpeg
- Interactive HTML5 Storyboard Player with synced audio, keyboard shortcuts & HUD
"""

import os
import sys
import glob
import json
import argparse
import subprocess
from PIL import Image
import numpy as np
import scipy.ndimage as ndi
import imageio_ffmpeg

_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

try:
    from render_engine import render_scene
except ImportError:
    render_scene = None

def resolve_image_path(manifest_dir, path):
    if not path:
        return ""
    if os.path.isabs(path):
        return path if os.path.exists(path) else ""
    cand = os.path.join(manifest_dir, path)
    if os.path.exists(cand):
        return os.path.abspath(cand)
    if os.path.exists(path):
        return os.path.abspath(path)
    return ""

# --- 1. ALPHA STICKER CUTOUT ---

def cutout_transparent_sticker(src_img_path, out_png_path, border_px=16):
    """Isolate subject and add a smooth feathered white sticker border"""
    img = Image.open(src_img_path).convert("RGB")
    arr = np.array(img)

    sat = np.max(arr, axis=2).astype(float) - np.min(arr, axis=2).astype(float)
    val = np.max(arr, axis=2).astype(float)

    is_subject = (sat > 15) | (val < 200)
    subject_mask = ndi.binary_fill_holes(is_subject)
    sticker_mask = ndi.binary_dilation(subject_mask, iterations=border_px)

    alpha = ndi.gaussian_filter(sticker_mask.astype(float), sigma=1.0)
    alpha = np.clip((alpha - 0.2) / 0.6, 0.0, 1.0) * 255.0

    h, w = arr.shape[:2]
    out_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    out_rgba[:, :, :3] = arr

    border_zone = sticker_mask & (~subject_mask)
    out_rgba[border_zone, 0] = 255
    out_rgba[border_zone, 1] = 255
    out_rgba[border_zone, 2] = 255
    out_rgba[:, :, 3] = alpha.astype(np.uint8)

    os.makedirs(os.path.dirname(os.path.abspath(out_png_path)), exist_ok=True)
    res = Image.fromarray(out_rgba, mode="RGBA")
    res.save(out_png_path, format="PNG", optimize=True)
    return out_png_path

# --- 2. INTERACTIVE STORYBOARD & ANIMATIC PLAYER ---

def generate_storyboard_html(manifest_path, output_html_path, audio_rel_path=None):
    """Generate self-contained interactive Storyboard & Animatic Player with WebCodecs Exporter"""
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    project_name = manifest.get("project_name", "GenFlow Production")
    scenes = manifest.get("scenes", [])
    total_dur = manifest.get("total_duration", 15.0)
    bpm = manifest.get("bpm", 120.0)
    
    scenes_json = json.dumps(scenes, ensure_ascii=False)
    
    vendor_muxer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "mp4-muxer.min.js")
    muxer_js_code = ""
    if os.path.exists(vendor_muxer_path):
        with open(vendor_muxer_path, "r", encoding="utf-8") as f:
            muxer_js_code = f.read()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GenFlow Studio: {project_name}</title>
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: #131b2e;
      --border: #23314f;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.3);
      --text: #f1f5f9;
      --muted: #94a3b8;
      --gold: #f59e0b;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    header {{
      padding: 1rem 2rem;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #060910;
    }}
    .brand {{ font-weight: 800; font-size: 1.25rem; color: var(--accent); letter-spacing: 1px; }}
    .meta-tag {{ font-size: 0.85rem; color: var(--muted); background: #1e293b; padding: 0.25rem 0.75rem; border-radius: 9999px; }}
    
    .theater {{
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
      max-width: 1200px;
      margin: 0 auto;
      width: 100%;
    }}
    .viewer {{
      position: relative;
      width: 100%;
      aspect-ratio: 16/9;
      background: #000;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--border);
      box-shadow: 0 20px 40px rgba(0,0,0,0.8);
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .viewer img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      transition: opacity 0.3s ease, transform 4s linear;
    }}
    .viewer img.kenburns {{
      transform: scale(1.08) translate(1%, -1%);
    }}
    
    .hud {{
      position: absolute;
      top: 1rem;
      left: 1rem;
      right: 1rem;
      display: flex;
      justify-content: space-between;
      pointer-events: none;
    }}
    .hud-chip {{
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      font-size: 0.85rem;
      font-family: monospace;
      color: #38bdf8;
    }}
    
    .caption-box {{
      position: absolute;
      bottom: 1rem;
      left: 1rem;
      right: 1rem;
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 0.8rem 1.2rem;
      pointer-events: none;
    }}
    .caption-title {{ font-weight: bold; font-size: 1.1rem; color: #facc15; margin-bottom: 0.2rem; }}
    .caption-desc {{ font-size: 0.9rem; color: #cbd5e1; }}
    
    .controls {{
      margin-top: 1.25rem;
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}
    .progress-bar-container {{
      width: 100%;
      height: 8px;
      background: #1e293b;
      border-radius: 4px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
    }}
    .progress-bar {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #38bdf8, #818cf8);
      border-radius: 4px;
      transition: width 0.1s linear;
    }}
    
    .btn-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .btn-group {{ display: flex; gap: 0.5rem; }}
    button {{
      background: #1e293b;
      color: #fff;
      border: 1px solid var(--border);
      padding: 0.5rem 1rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.9rem;
      transition: all 0.2s;
    }}
    button:hover {{ background: #334155; border-color: var(--accent); }}
    button.primary {{ background: #0284c7; border-color: #38bdf8; }}
    button.primary:hover {{ background: #0369a1; }}
    
    .time-display {{ font-family: monospace; font-size: 0.95rem; color: var(--muted); }}
    
    .thumbnail-reel {{
      display: flex;
      gap: 0.75rem;
      overflow-x: auto;
      padding: 1rem 0;
      width: 100%;
    }}
    .thumb {{
      flex: 0 0 160px;
      aspect-ratio: 16/9;
      border-radius: 6px;
      overflow: hidden;
      border: 2px solid transparent;
      cursor: pointer;
      background: #1e293b;
      position: relative;
      transition: border-color 0.2s;
    }}
    .thumb.active {{ border-color: var(--accent); box-shadow: 0 0 12px var(--accent-glow); }}
    .thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
    .thumb-label {{
      position: absolute;
      bottom: 2px;
      left: 2px;
      background: rgba(0,0,0,0.7);
      font-size: 0.7rem;
      padding: 2px 4px;
      border-radius: 3px;
    }}

    /* WebCodecs Modal */
    .modal-overlay {{
      position: fixed; inset: 0; background: rgba(5, 8, 15, 0.85); z-index: 9999;
      display: none; align-items: center; justify-content: center; backdrop-filter: blur(6px);
    }}
    .modal-content {{
      background: #131b2e; border: 1px solid #23314f; border-radius: 12px;
      width: 90%; max-width: 520px; padding: 1.75rem; box-shadow: 0 25px 50px rgba(0,0,0,0.8);
    }}
    .modal-title {{ font-size: 1.25rem; font-weight: bold; color: #38bdf8; margin-bottom: 1.25rem; }}
    .opt-card {{
      display: block; margin-bottom: 0.75rem; cursor: pointer; padding: 0.85rem;
      border: 1px solid #23314f; border-radius: 8px; transition: border-color 0.2s, background 0.2s;
    }}
    .opt-card:hover {{ border-color: #38bdf8; background: #1e293b; }}
    .opt-card input {{ margin-right: 0.6rem; accent-color: #38bdf8; }}
    .opt-desc {{ font-size: 0.8rem; color: #94a3b8; margin-top: 0.25rem; margin-left: 1.6rem; }}
    .grid-settings {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }}
    .grid-settings select {{
      width: 100%; background: #1e293b; color: #f1f5f9; border: 1px solid #334155;
      padding: 0.5rem; border-radius: 6px; margin-top: 0.25rem;
    }}
    .modal-footer {{ display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem; }}
  </style>
</head>
<body>
  <header>
    <div class="brand">GENFLOW PRODUCTION STUDIO</div>
    <div style="display: flex; align-items: center; gap: 1rem;">
      <div class="meta-tag">{project_name} | {total_dur}s @ {bpm} BPM</div>
      <button class="primary" id="btnOpenExport" style="background: #0284c7; border: 1px solid #38bdf8; font-weight: bold; cursor: pointer;">⚡ Export MP4</button>
    </div>
  </header>

  <div class="theater">
    <div class="viewer" id="viewer">
      <img id="mainImage" src="" alt="Scene Preview" />
      <div class="hud">
        <div class="hud-chip" id="hudScene">SCENE 01/01</div>
        <div class="hud-chip" id="hudCamera">CAMERA: WIDE</div>
      </div>
      <div class="caption-box">
        <div class="caption-title" id="capTitle">Scene Title</div>
        <div class="caption-desc" id="capDesc">Action details</div>
      </div>
    </div>

    <div class="controls">
      <div class="progress-bar-container" id="timelineBar">
        <div class="progress-bar" id="progressFill"></div>
      </div>
      <div class="btn-row">
        <div class="btn-group">
          <button id="btnPrev">Prev (←)</button>
          <button class="primary" id="btnPlay">Play (Space)</button>
          <button id="btnNext">Next (→)</button>
        </div>
        <div class="time-display" id="timeDisplay">00:00.00 / 00:00.00</div>
      </div>
      
      <div class="thumbnail-reel" id="reel"></div>
    </div>
  </div>

  <!-- WebCodecs Modal -->
  <div id="exportModal" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-title">⚡ Export Video (WebCodecs Zero-IPC)</div>
      
      <label class="opt-card">
        <input type="radio" name="exportMode" value="animatic" checked>
        <strong>🎬 Ken Burns Animatic (2D Storyboard)</strong>
        <div class="opt-desc">Smooth Pan/Zoom cinematic slide transitions with HUD overlay</div>
      </label>

      <label class="opt-card">
        <input type="radio" name="exportMode" value="hybrid">
        <strong>🌌 3D Holographic Hybrid 60fps (WebGL)</strong>
        <div class="opt-desc">Floating 3D Holographic Card turntable + Audio Spectrum space</div>
      </label>

      <div class="grid-settings">
        <div>
          <label style="font-size: 0.85rem; color: #cbd5e1;">Framerate:</label>
          <select id="selFps">
            <option value="60">60 FPS (Ultra Smooth)</option>
            <option value="30">30 FPS (Standard)</option>
          </select>
        </div>
        <div>
          <label style="font-size: 0.85rem; color: #cbd5e1;">Resolution:</label>
          <select id="selRes">
            <option value="1080">1080p (1920x1080)</option>
            <option value="720">720p (1280x720)</option>
          </select>
        </div>
      </div>

      <div id="exportProgressBox" style="display:none; margin-top: 1.25rem;">
        <div class="progress-bar-container">
          <div id="exportProgressBar" class="progress-bar" style="width: 0%;"></div>
        </div>
        <div id="exportStatusText" style="font-size: 0.85rem; color: #38bdf8; margin-top: 0.5rem; font-family: monospace;">Encoding frames...</div>
      </div>

      <div class="modal-footer">
        <button id="btnCloseModal">Cancel</button>
        <button class="primary" id="btnStartExport">Start Export</button>
      </div>
    </div>
  </div>

  <audio id="soundtrack" src="{audio_rel_path or ''}" preload="auto"></audio>

  <!-- Inlined Offline mp4-muxer -->
  <script>
{muxer_js_code}
  </script>

  <script>
    const scenes = {scenes_json};
    let currentIdx = 0;
    let isPlaying = false;
    let playTimer = null;
    let startTime = 0;
    let curTime = 0;
    const totalDuration = {total_dur};
    
    const imgEl = document.getElementById('mainImage');
    const hudScene = document.getElementById('hudScene');
    const hudCamera = document.getElementById('hudCamera');
    const capTitle = document.getElementById('capTitle');
    const capDesc = document.getElementById('capDesc');
    const progressFill = document.getElementById('progressFill');
    const timeDisplay = document.getElementById('timeDisplay');
    const btnPlay = document.getElementById('btnPlay');
    const audioEl = document.getElementById('soundtrack');
    const reel = document.getElementById('reel');

    function renderThumbnails() {{
      reel.innerHTML = '';
      scenes.forEach((sc, idx) => {{
        const d = document.createElement('div');
        d.className = 'thumb' + (idx === currentIdx ? ' active' : '');
        d.innerHTML = `<img src="${{sc.raw_file || sc.processed_file || ''}}" /><span class="thumb-label">${{sc.id}}</span>`;
        d.onclick = () => seekToScene(idx);
        reel.appendChild(d);
      }});
    }}

    function showScene(idx) {{
      if (idx < 0 || idx >= scenes.length) return;
      currentIdx = idx;
      const sc = scenes[idx];
      imgEl.src = sc.raw_file || sc.processed_file || 'https://via.placeholder.com/1280x720/131b2e/38bdf8?text=' + encodeURIComponent(sc.title);
      imgEl.classList.remove('kenburns');
      void imgEl.offsetWidth;
      imgEl.classList.add('kenburns');
      
      hudScene.textContent = `${{sc.id.toUpperCase()}} (${{sc.start_time}}s - ${{sc.end_time}}s)`;
      hudCamera.textContent = `CAMERA: ${{sc.camera.toUpperCase()}}`;
      capTitle.textContent = `${{idx + 1}}. ${{sc.title}}`;
      capDesc.textContent = sc.action || sc.prompt;
      
      document.querySelectorAll('.thumb').forEach((t, i) => {{
        t.classList.toggle('active', i === idx);
      }});
    }}

    function updateTimecode(t) {{
      curTime = t;
      const pct = Math.min((t / totalDuration) * 100, 100);
      progressFill.style.width = pct + '%';
      
      const formatTime = sec => {{
        const m = Math.floor(sec / 60);
        const s = (sec % 60).toFixed(2).padStart(5, '0');
        return `${{m.toString().padStart(2, '0')}}:${{s}}`;
      }};
      timeDisplay.textContent = `${{formatTime(t)}} / ${{formatTime(totalDuration)}}`;
      
      for (let i = 0; i < scenes.length; i++) {{
        if (t >= scenes[i].start_time && t < scenes[i].end_time) {{
          if (currentIdx !== i) showScene(i);
          break;
        }}
      }}
    }}

    function seekToScene(idx) {{
      currentIdx = idx;
      showScene(idx);
      const targetTime = scenes[idx].start_time;
      if (audioEl.src && !audioEl.paused) audioEl.currentTime = targetTime;
      updateTimecode(targetTime);
    }}

    function togglePlay() {{
      isPlaying = !isPlaying;
      btnPlay.textContent = isPlaying ? 'Pause (Space)' : 'Play (Space)';
      if (isPlaying) {{
        if (curTime >= totalDuration) curTime = 0;
        startTime = performance.now() - (curTime * 1000);
        if (audioEl.src) {{
          audioEl.currentTime = curTime;
          audioEl.play().catch(e => console.log('Audio autoplay prevented'));
        }}
        tick();
      }} else {{
        cancelAnimationFrame(playTimer);
        if (audioEl.src) audioEl.pause();
      }}
    }}

    function tick() {{
      if (!isPlaying) return;
      const now = performance.now();
      const t = (now - startTime) / 1000;
      if (t >= totalDuration) {{
        updateTimecode(totalDuration);
        togglePlay();
        return;
      }}
      updateTimecode(t);
      playTimer = requestAnimationFrame(tick);
    }}

    // Controls
    btnPlay.onclick = togglePlay;
    document.getElementById('btnPrev').onclick = () => {{
      if (currentIdx > 0) seekToScene(currentIdx - 1);
    }};
    document.getElementById('btnNext').onclick = () => {{
      if (currentIdx < scenes.length - 1) seekToScene(currentIdx + 1);
    }};

    document.getElementById('timelineBar').onclick = (e) => {{
      const rect = e.currentTarget.getBoundingClientRect();
      const pos = (e.clientX - rect.left) / rect.width;
      const targetTime = pos * totalDuration;
      startTime = performance.now() - (targetTime * 1000);
      if (audioEl.src) audioEl.currentTime = targetTime;
      updateTimecode(targetTime);
    }};

    window.onkeydown = (e) => {{
      if (e.code === 'Space') {{ e.preventDefault(); togglePlay(); }}
      if (e.code === 'ArrowLeft') {{ e.preventDefault(); if (currentIdx > 0) seekToScene(currentIdx - 1); }}
      if (e.code === 'ArrowRight') {{ e.preventDefault(); if (currentIdx < scenes.length - 1) seekToScene(currentIdx + 1); }}
    }};

    // --- WebCodecs Client-Side Export Engine ---
    let abortExport = false;
    const modalEl = document.getElementById('exportModal');
    const btnOpenExport = document.getElementById('btnOpenExport');
    const btnCloseModal = document.getElementById('btnCloseModal');
    const btnStartExport = document.getElementById('btnStartExport');
    const exportProgressBox = document.getElementById('exportProgressBox');
    const exportProgressBar = document.getElementById('exportProgressBar');
    const exportStatusText = document.getElementById('exportStatusText');

    btnOpenExport.onclick = () => {{ modalEl.style.display = 'flex'; }};
    btnCloseModal.onclick = () => {{
      if (btnStartExport.disabled) abortExport = true;
      modalEl.style.display = 'none';
    }};

    btnStartExport.onclick = async () => {{
      const mode = document.querySelector('input[name="exportMode"]:checked').value;
      const fps = parseInt(document.getElementById('selFps').value, 10);
      const resHeight = parseInt(document.getElementById('selRes').value, 10);
      const resWidth = resHeight === 1080 ? 1920 : 1280;
      
      btnStartExport.disabled = true;
      btnCloseModal.textContent = 'Abort';
      exportProgressBox.style.display = 'block';
      exportProgressBar.style.width = '0%';
      exportStatusText.textContent = 'Initializing WebCodecs VideoEncoder...';
      abortExport = false;
      
      try {{
        await runClientSideExport(mode, fps, resWidth, resHeight);
      }} catch (err) {{
        console.error(err);
        alert('Export error: ' + err.message);
      }} finally {{
        btnStartExport.disabled = false;
        btnCloseModal.textContent = 'Close';
      }}
    }};

    async function runClientSideExport(mode, fps, width, height) {{
      if (typeof Mp4Muxer === 'undefined') {{
        throw new Error('Mp4Muxer module not loaded');
      }}
      if (typeof VideoEncoder === 'undefined') {{
        throw new Error('WebCodecs VideoEncoder is not supported in this browser');
      }}

      // Preload images
      const loadedImgs = await Promise.all(scenes.map(sc => {{
        return new Promise(resolve => {{
          const img = new Image();
          img.crossOrigin = 'anonymous';
          img.onload = () => resolve(img);
          img.onerror = () => resolve(null);
          img.src = sc.raw_file || sc.processed_file || '';
        }});
      }}));

      const {{ Muxer, ArrayBufferTarget }} = Mp4Muxer;
      const target = new ArrayBufferTarget();
      const muxer = new Muxer({{
        target,
        fastStart: 'in-memory',
        firstTimestampBehavior: 'strict',
        video: {{ codec: 'avc', width, height }}
      }});

      let cfg = {{
        codec: 'avc1.64002A',
        width, height, framerate: fps, bitrate: 12_000_000,
        latencyMode: 'quality', avc: {{ format: 'avc' }},
        hardwareAcceleration: 'prefer-hardware'
      }};
      let sup = await VideoEncoder.isConfigSupported(cfg);
      if (!sup.supported) {{
        cfg.hardwareAcceleration = 'no-preference';
        sup = await VideoEncoder.isConfigSupported(cfg);
      }}
      if (!sup.supported) throw new Error('H.264 VideoEncoder not supported');

      let encErr = null;
      const enc = new VideoEncoder({{
        output: (chunk, meta) => muxer.addVideoChunk(chunk, meta),
        error: e => {{ encErr = e; }}
      }});
      enc.configure(sup.config);

      const offCanvas = document.createElement('canvas');
      offCanvas.width = width;
      offCanvas.height = height;
      const ctx = offCanvas.getContext('2d');

      const totalFrames = Math.round(totalDuration * fps);
      const t0 = performance.now();

      for (let i = 0; i < totalFrames; i++) {{
        if (abortExport) throw new Error('Export cancelled by user');
        const t = i / fps;
        
        // Find current scene
        let scIdx = 0;
        for (let s = 0; s < scenes.length; s++) {{
          if (t >= scenes[s].start_time && t < scenes[s].end_time) {{
            scIdx = s;
            break;
          }}
        }}
        const curSc = scenes[scIdx] || scenes[0];
        const curImg = loadedImgs[scIdx];

        // Draw Scene
        ctx.fillStyle = '#090d16';
        ctx.fillRect(0, 0, width, height);

        if (mode === 'animatic') {{
          // Ken Burns Pan/Zoom
          const scDur = curSc.duration || curSc.duration_seconds || (curSc.end_time - curSc.start_time) || 1;
          const scProg = Math.max(0, Math.min(1, (t - curSc.start_time) / scDur));
          const scale = 1.0 + 0.08 * scProg;
          const panX = (scIdx % 2 === 0 ? 1 : -1) * 30 * scProg;
          
          if (curImg) {{
            ctx.save();
            ctx.translate(width / 2, height / 2);
            ctx.scale(scale, scale);
            ctx.drawImage(curImg, -width / 2 + panX, -height / 2, width, height);
            ctx.restore();
          }} else {{
            ctx.fillStyle = '#1e293b';
            ctx.fillRect(width * 0.1, height * 0.1, width * 0.8, height * 0.8);
            ctx.fillStyle = '#38bdf8';
            ctx.font = 'bold 36px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(curSc.title, width / 2, height / 2);
          }}

          // HUD & Caption Overlay
          ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
          ctx.fillRect(40, 40, 260, 46);
          ctx.strokeStyle = '#38bdf8';
          ctx.strokeRect(40, 40, 260, 46);
          ctx.fillStyle = '#38bdf8';
          ctx.font = 'bold 18px monospace';
          ctx.textAlign = 'left';
          ctx.fillText(`SCENE ${{scIdx + 1}}: ${{curSc.camera.toUpperCase()}}`, 55, 70);

          ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
          ctx.fillRect(40, height - 120, width - 80, 80);
          ctx.fillStyle = '#facc15';
          ctx.font = 'bold 24px sans-serif';
          ctx.fillText(`${{scIdx + 1}}. ${{curSc.title}}`, 60, height - 85);
          ctx.fillStyle = '#cbd5e1';
          ctx.font = '18px sans-serif';
          ctx.fillText(curSc.action || curSc.prompt || '', 60, height - 55);
        }} else {{
          // 3D Hybrid Holographic Simulation
          ctx.save();
          ctx.translate(width / 2, height / 2);
          const rotY = Math.sin(t * 1.5) * 0.35;
          ctx.transform(Math.cos(rotY), 0, -Math.sin(rotY) * 0.2, 1, 0, 0);

          if (curImg) {{
            const cardW = width * 0.6;
            const cardH = height * 0.6;
            ctx.drawImage(curImg, -cardW / 2, -cardH / 2, cardW, cardH);
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 4;
            ctx.strokeRect(-cardW / 2, -cardH / 2, cardW, cardH);
          }}
          ctx.restore();

          // Spectrum Bars
          for (let b = 0; b < 40; b++) {{
            const hBar = Math.abs(Math.sin(t * 10 + b * 0.4)) * 70 + 8;
            ctx.fillStyle = b < 15 ? '#38bdf8' : (b < 28 ? '#818cf8' : '#f43f5e');
            ctx.fillRect(width / 2 - 300 + b * 15, height - 50 - hBar, 10, hBar);
          }}
        }}

        // Push frame to encoder
        const ts = Math.round(i * 1e6 / fps);
        const dur = Math.round((i + 1) * 1e6 / fps) - ts;
        const frame = new VideoFrame(offCanvas, {{ timestamp: ts, duration: dur }});
        enc.encode(frame, {{ keyFrame: i % (fps * 2) === 0 }});
        frame.close();

        while (enc.encodeQueueSize > 4) {{
          await new Promise(r => enc.addEventListener('dequeue', r, {{ once: true }}));
        }}
        if (encErr) throw encErr;

        if ((i + 1) % 15 === 0 || i === totalFrames - 1) {{
          const pct = Math.round(((i + 1) / totalFrames) * 100);
          const elapsed = (performance.now() - t0) / 1000;
          const curFps = ((i + 1) / elapsed).toFixed(1);
          exportProgressBar.style.width = pct + '%';
          exportStatusText.textContent = `Encoding frame ${{i + 1}}/${{totalFrames}} (${{pct}}%) | Speed: ${{curFps}} fps`;
          await new Promise(r => setTimeout(r, 0));
        }}
      }}

      await enc.flush();
      muxer.finalize();

      const blob = new Blob([target.buffer], {{ type: 'video/mp4' }});
      const dlUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = dlUrl;
      const projName = "{project_name}";
      a.download = `${{projName}}_${{mode}}_${{fps}}fps.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      exportStatusText.textContent = `COMPLETE! File downloaded (${{(blob.size / (1024*1024)).toFixed(2)}} MB)`;
      exportProgressBar.style.width = '100%';
    }}

    // Init
    renderThumbnails();
    if (scenes.length > 0) showScene(0);
    updateTimecode(0);
  </script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_html_path

# --- 3. ANIMATIC MP4 COMPOSER (FFMPEG) ---

def compose_animatic(manifest_path, output_mp4, audio_path=None, fps=30):
    """Assemble storyboard images into an animated MP4 with Ken Burns & audio"""
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    scenes = manifest.get("scenes", [])
    if not scenes:
        raise ValueError("No scenes found in manifest to compile animatic.")
        
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    out_dir = os.path.dirname(os.path.abspath(output_mp4))
    os.makedirs(out_dir, exist_ok=True)
    
    # Create FFmpeg concat script with duration per slide
    manifest_dir = os.path.dirname(os.path.abspath(manifest_path))
    concat_txt_path = os.path.join(out_dir, "animatic_concat.txt")
    valid_images = []
    for sc in scenes:
        raw_p = sc.get("processed_file") or sc.get("raw_file")
        img_resolved = resolve_image_path(manifest_dir, raw_p)
        dur = float(sc.get("duration") or sc.get("duration_seconds") or (float(sc.get("end_time", 0)) - float(sc.get("start_time", 0))) or 3.0)
        if img_resolved:
            valid_images.append((img_resolved, dur))
            
    if not valid_images:
        raise ValueError(f"No existing scene image files found for manifest: {manifest_path}. Please generate images first or use --hybrid which provides dynamic code-rendered holographic card fallbacks.")

    with open(concat_txt_path, "w", encoding="utf-8") as f:
        for img_path, dur in valid_images:
            safe_path = img_path.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")
            f.write(f"duration {dur}\n")
        # Repeat last file to satisfy FFmpeg duration semantics
        f.write(f"file '{valid_images[-1][0].replace(chr(92), '/')}'\n")

    cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_txt_path
    ]
    
    if audio_path and os.path.exists(audio_path):
        cmd.extend(["-i", os.path.abspath(audio_path)])
        
    cmd.extend([
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-r", str(fps),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20"
    ])
    
    total_dur_limit = float(manifest.get("total_duration") or sum(d for _, d in valid_images))
    if total_dur_limit > 0:
        cmd.extend(["-t", str(total_dur_limit)])

    if audio_path and os.path.exists(audio_path):
        cmd.extend(["-c:a", "aac", "-b:a", "192k", "-shortest"])
        
    cmd.extend(["-movflags", "+faststart", os.path.abspath(output_mp4)])
    
    print(f"Compiling Animatic MP4: {output_mp4}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FFmpeg error:\n{res.stderr}")
        raise RuntimeError("Animatic assembly failed")
        
    print(f"Success! Animatic generated: {output_mp4} ({os.path.getsize(output_mp4)} bytes)")
    return output_mp4

# --- 4. HYBRID ANIMATIC COMPOSER (ENGINE A + ENGINE B) ---

def generate_hybrid_scene_html(manifest_path, output_html_path, audio_rel_path=None):
    """
    Generate unified 60fps WebGL + Storyboard Hybrid HTML Scene with window.renderFrame(t)
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    project_name = manifest.get("project_name", "Hybrid Production")
    scenes = manifest.get("scenes", [])
    total_dur = manifest.get("total_duration", 15.0)
    bpm = manifest.get("bpm", 128.0)

    manifest_dir = os.path.dirname(os.path.abspath(manifest_path))
    processed_scenes = []
    for sc in scenes:
        raw_p = sc.get("processed_file") or sc.get("raw_file") or ""
        img_resolved = resolve_image_path(manifest_dir, raw_p)
        img_url = ""
        if img_resolved:
            img_url = "file:///" + img_resolved.replace("\\", "/")
        processed_scenes.append({
            "id": sc.get("id", ""),
            "title": sc.get("title", ""),
            "camera": sc.get("camera", "medium shot"),
            "action": sc.get("action", ""),
            "start_time": sc.get("start_time", 0.0),
            "end_time": sc.get("end_time", 3.0),
            "image_url": img_url
        })

    scenes_json = json.dumps(processed_scenes, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>GenFlow Hybrid Studio: {project_name}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #000; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }}
    #masterCanvas {{ display: block; width: 100%; height: 100%; }}
  </style>
</head>
<body>
  <canvas id="masterCanvas" width="1920" height="1080"></canvas>
  <script>
    const width = 1920;
    const height = 1080;
    const totalDuration = {total_dur};
    const bpm = {bpm};
    const beatDur = 60.0 / bpm;
    const scenes = {scenes_json};

    const masterCanvas = document.getElementById('masterCanvas');
    const masterCtx = masterCanvas.getContext('2d');

    // 1. Offscreen WebGL2 Canvas for 3D Kinetic Background
    const glCanvas = document.createElement('canvas');
    glCanvas.width = width;
    glCanvas.height = height;
    const gl = glCanvas.getContext('webgl2', {{ antialias: true, preserveDrawingBuffer: true }});

    // 2. Offscreen 2D Canvas for Storyboard & HUD Layer
    const fgCanvas = document.createElement('canvas');
    fgCanvas.width = width;
    fgCanvas.height = height;
    const fgCtx = fgCanvas.getContext('2d');

    // Preload scene images with readiness handshake for deterministic video capture
    const imageCache = {{}};
    window.imagesReady = false;
    const totalImgs = scenes.filter(sc => !!sc.image_url).length;
    if (totalImgs === 0) {{
      window.imagesReady = true;
    }} else {{
      let loadedImgs = 0;
      scenes.forEach(sc => {{
        if (sc.image_url) {{
          const img = new Image();
          img.crossOrigin = "anonymous";
          img.onload = img.onerror = () => {{
            loadedImgs++;
            if (loadedImgs >= totalImgs) {{
              window.imagesReady = true;
            }}
          }};
          img.src = sc.image_url;
          imageCache[sc.id] = img;
        }}
      }});
    }}

    // WebGL Shader for Cyber Ambient Matrix / Space Tunnel
    const vsSource = `#version 300 es
      in vec2 position;
      void main() {{
        gl_Position = vec4(position, 0.0, 1.0);
      }}
    `;

    const fsSource = `#version 300 es
      precision highp float;
      out vec4 fragColor;
      uniform vec2 u_resolution;
      uniform float u_time;
      uniform float u_beat;

      void main() {{
        vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
        float d = length(uv);
        float angle = atan(uv.y, uv.x);
        
        // Ambient expanding rings
        float ring = sin(d * 18.0 - u_time * 3.0);
        float spoke = sin(angle * 8.0 + u_time * 0.5);
        float grid = abs(ring * spoke);

        // Gradient depth
        vec3 bgDark = vec3(0.04, 0.06, 0.12);
        vec3 neonCyan = vec3(0.0, 0.8, 1.0) * (0.15 + u_beat * 0.35);
        vec3 neonViolet = vec3(0.6, 0.2, 0.9) * 0.2;

        vec3 col = bgDark + neonCyan * exp(-d * 2.5) * (1.0 - smoothstep(0.0, 0.1, grid));
        col += neonViolet * pow(max(0.0, 1.0 - d), 3.0);
        fragColor = vec4(col, 1.0);
      }}
    `;

    function createShader(gl, type, source) {{
      const s = gl.createShader(type);
      gl.shaderSource(s, source);
      gl.compileShader(s);
      return s;
    }}
    const prog = gl.createProgram();
    gl.attachShader(prog, createShader(gl, gl.VERTEX_SHADER, vsSource));
    gl.attachShader(prog, createShader(gl, gl.FRAGMENT_SHADER, fsSource));
    gl.linkProgram(prog);

    const quadBuf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, quadBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1, -1, 1, -1, -1, 1,
      -1, 1, 1, -1, 1, 1
    ]), gl.STATIC_DRAW);

    const posLoc = gl.getAttribLocation(prog, "position");
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    const uResLoc = gl.getUniformLocation(prog, "u_resolution");
    const uTimeLoc = gl.getUniformLocation(prog, "u_time");
    const uBeatLoc = gl.getUniformLocation(prog, "u_beat");

    // Master deterministic renderFrame contract
    window.renderFrame = function(t) {{
      const beatPhase = (t % beatDur) / beatDur;
      const beatExp = Math.exp(-beatPhase * 10.0);

      // 1. Render WebGL Background
      gl.viewport(0, 0, width, height);
      gl.useProgram(prog);
      gl.uniform2f(uResLoc, width, height);
      gl.uniform1f(uTimeLoc, t);
      gl.uniform1f(uBeatLoc, beatExp);
      gl.drawArrays(gl.TRIANGLES, 0, 6);

      // 2. Render Storyboard Image & Kinetic HUD
      fgCtx.clearRect(0, 0, width, height);

      let activeScene = scenes[0] || {{ id: "scene_01", title: "Scene", start_time: 0, end_time: totalDuration }};
      for (let i = 0; i < scenes.length; i++) {{
        if (t >= scenes[i].start_time && t < scenes[i].end_time) {{
          activeScene = scenes[i];
          break;
        }}
      }}
      if (t >= totalDuration && scenes.length > 0) {{
        activeScene = scenes[scenes.length - 1];
      }}

      // Storyboard Card
      const cardW = 1200;
      const cardH = 675;
      const cardX = (width - cardW) / 2;
      const floatY = Math.sin(t * 1.5) * 6;
      const cardY = (height - cardH) / 2 - 20 + floatY;
      const scale = 1.0 + beatExp * 0.015;

      fgCtx.save();
      fgCtx.translate(cardX + cardW / 2, cardY + cardH / 2);
      fgCtx.scale(scale, scale);
      fgCtx.translate(-(cardX + cardW / 2), -(cardY + cardH / 2));

      fgCtx.shadowColor = 'rgba(56, 189, 248, 0.4)';
      fgCtx.shadowBlur = 25;
      fgCtx.strokeStyle = 'rgba(56, 189, 248, 0.8)';
      fgCtx.lineWidth = 3;
      fgCtx.strokeRect(cardX, cardY, cardW, cardH);
      fgCtx.shadowBlur = 0;

      const img = imageCache[activeScene.id];
      if (img && img.complete && img.naturalWidth > 0) {{
        fgCtx.drawImage(img, cardX, cardY, cardW, cardH);
      }} else {{
        const grad = fgCtx.createLinearGradient(cardX, cardY, cardX + cardW, cardY + cardH);
        grad.addColorStop(0, '#0f172a');
        grad.addColorStop(1, '#1e293b');
        fgCtx.fillStyle = grad;
        fgCtx.fillRect(cardX, cardY, cardW, cardH);

        fgCtx.fillStyle = '#38bdf8';
        fgCtx.font = 'bold 36px sans-serif';
        fgCtx.textAlign = 'center';
        fgCtx.fillText(activeScene.title || activeScene.id, cardX + cardW / 2, cardY + cardH / 2 - 20);
        fgCtx.font = '20px monospace';
        fgCtx.fillStyle = '#94a3b8';
        fgCtx.fillText("[" + (activeScene.camera || 'Medium Shot') + "] " + (activeScene.action || ''), cardX + cardW / 2, cardY + cardH / 2 + 25);
      }}
      fgCtx.restore();

      // Top HUD
      fgCtx.fillStyle = 'rgba(15, 23, 42, 0.85)';
      fgCtx.fillRect(40, 30, width - 80, 50);
      fgCtx.strokeStyle = '#23314f';
      fgCtx.lineWidth = 1;
      fgCtx.strokeRect(40, 30, width - 80, 50);

      fgCtx.fillStyle = '#38bdf8';
      fgCtx.font = 'bold 18px monospace';
      fgCtx.textAlign = 'left';
      fgCtx.fillText("// GENFLOW HYBRID STUDIO: " + {json.dumps(project_name.upper())} + " // BPM: " + bpm + " [LOCKED]", 60, 62);

      const secStr = Math.floor(t).toString().padStart(2, '0');
      const frameStr = Math.floor((t % 1.0) * 60).toString().padStart(2, '0');
      fgCtx.fillStyle = '#f59e0b';
      fgCtx.textAlign = 'right';
      fgCtx.fillText("T+ 00:00:" + secStr + ":" + frameStr + " [60 FPS HYBRID]", width - 60, 62);

      // Bottom Narrative Caption
      fgCtx.fillStyle = 'rgba(15, 23, 42, 0.9)';
      fgCtx.fillRect(cardX, cardY + cardH + 15, cardW, 80);
      fgCtx.strokeStyle = '#38bdf8';
      fgCtx.lineWidth = 1.5;
      fgCtx.strokeRect(cardX, cardY + cardH + 15, cardW, 80);

      fgCtx.fillStyle = '#f1f5f9';
      fgCtx.font = 'bold 22px sans-serif';
      fgCtx.textAlign = 'left';
      fgCtx.fillText(activeScene.id.toUpperCase() + ": " + (activeScene.title || ''), cardX + 25, cardY + cardH + 48);

      fgCtx.fillStyle = '#94a3b8';
      fgCtx.font = '16px monospace';
      fgCtx.fillText("ACTION: " + (activeScene.action || activeScene.camera || 'Scene in progress...'), cardX + 25, cardY + cardH + 75);

      // Audio Spectrum Array
      const numBars = 32;
      const barW = 8;
      const barGap = 4;
      const totalBarW = numBars * (barW + barGap);
      const specX = cardX + cardW - totalBarW - 25;
      const specY = cardY + cardH + 80;

      for (let b = 0; b < numBars; b++) {{
        const prng = Math.abs(Math.sin(t * 133.7 + b * 41.9) * 43758.5453) % 1.0;
        let bh = 4.0;
        if (b < 8) {{
          bh = Math.max(6.0, beatExp * 35.0 + prng * 10.0);
        }} else {{
          bh = 4.0 + prng * 25.0;
        }}
        fgCtx.fillStyle = b < 10 ? '#38bdf8' : (b < 22 ? '#818cf8' : '#ec4899');
        fgCtx.fillRect(specX + b * (barW + barGap), specY - bh, barW, bh);
      }}

      // 3. Composite onto Master Canvas
      masterCtx.clearRect(0, 0, width, height);
      masterCtx.drawImage(glCanvas, 0, 0);
      masterCtx.drawImage(fgCanvas, 0, 0);
    }};

    window.renderFrame(0.0);
  </script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_html_path

def compose_hybrid_video(manifest_path, output_mp4, audio_path=None, fps=60, width=1920, height=1080):
    """
    Compile Hybrid Animatic (Engine A AI Storyboard + Engine B 3D WebGL & DSP Audio)
    into a broadcast-grade 60fps MP4 in a single click.
    """
    if render_scene is None:
        raise RuntimeError("render_engine.py is required for hybrid video compilation.")
        
    out_dir = os.path.dirname(os.path.abspath(output_mp4))
    os.makedirs(out_dir, exist_ok=True)
    temp_html = os.path.join(out_dir, "temp_hybrid_scene.html")
    
    manifest_dir = os.path.dirname(os.path.abspath(manifest_path))
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    duration = manifest.get("total_duration", 15.0)

    # Auto-detect audio from manifest or project directory if not explicitly provided
    if not audio_path:
        if manifest.get("audio_file"):
            cand = resolve_image_path(manifest_dir, manifest["audio_file"])
            if cand: audio_path = cand
        else:
            for wav in glob.glob(os.path.join(manifest_dir, "*.wav")):
                audio_path = os.path.abspath(wav)
                break

    # 1. Generate Hybrid WebGL/Canvas Scene
    generate_hybrid_scene_html(manifest_path, temp_html, audio_rel_path=audio_path)
    
    # 2. Render via In-Memory Playwright -> FFmpeg Pipe at 60fps
    print(f"[Hybrid Engine] Initiating 60fps render: {temp_html} -> {output_mp4} ({duration}s)...")
    res_mp4 = render_scene(
        html_path=temp_html,
        output_video=output_mp4,
        audio_path=audio_path,
        fps=fps,
        duration=duration,
        width=width,
        height=height,
        selector="#masterCanvas",
        crf=18,
        preset="medium"
    )
    return res_mp4

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post-Production & Assembly Engine for /genflow")
    parser.add_argument("--cutout", help="Input image for sticker cutout")
    parser.add_argument("--out", default="out.png", help="Output file path")
    parser.add_argument("--manifest", help="Path to production_manifest.json")
    parser.add_argument("--player", action="store_true", help="Generate interactive Storyboard HTML Player")
    parser.add_argument("--animatic", action="store_true", help="Compile Animatic MP4 video")
    parser.add_argument("--hybrid", action="store_true", help="Compile 60fps Hybrid Animatic (Engine A + Engine B)")
    parser.add_argument("--hybrid-scene", action="store_true", help="Generate Hybrid WebGL/Canvas scene HTML")
    parser.add_argument("--audio", default=None, help="Audio WAV path for animatic/player/hybrid")
    parser.add_argument("--fps", type=int, default=60, help="Framerate for hybrid export (default: 60)")
    args = parser.parse_args()
    
    if args.cutout:
        print(f"Processing sticker cutout: {args.cutout} -> {args.out}...")
        res = cutout_transparent_sticker(args.cutout, args.out)
        print(f"Done! Saved: {res}")
    elif args.hybrid and args.manifest:
        out_mp4 = args.out if args.out.endswith(".mp4") else os.path.join(os.path.dirname(args.manifest), "hybrid_master.mp4")
        res = compose_hybrid_video(args.manifest, out_mp4, audio_path=args.audio, fps=args.fps)
        print(f"Done! Hybrid Video Created: {res}")
    elif args.hybrid_scene and args.manifest:
        out_html = args.out if args.out.endswith(".html") else os.path.join(os.path.dirname(args.manifest), "hybrid_scene.html")
        res = generate_hybrid_scene_html(args.manifest, out_html, audio_rel_path=args.audio)
        print(f"Done! Hybrid Scene HTML Created: {res}")
    elif args.player and args.manifest:
        out_html = args.out if args.out.endswith(".html") else os.path.join(os.path.dirname(args.manifest), "storyboard_player.html")
        print(f"Generating Storyboard Player: {args.manifest} -> {out_html}...")
        res = generate_storyboard_html(args.manifest, out_html, audio_rel_path=args.audio)
        print(f"Done! Saved: {res}")
    elif args.animatic and args.manifest:
        out_mp4 = args.out if args.out.endswith(".mp4") else os.path.join(os.path.dirname(args.manifest), "animatic.mp4")
        res = compose_animatic(args.manifest, out_mp4, audio_path=args.audio)
    else:
        parser.print_help()
