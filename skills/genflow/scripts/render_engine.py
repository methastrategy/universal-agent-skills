"""
Universal Headless Video Render Engine for /genflow
High-Performance Dual-Engine Video Pipeline:
1. In-Memory Pipe: Playwright WebGL2 -> Synchronous MJPEG -> FFmpeg libx264
2. WebCodecs Zero-IPC: Native In-Browser GPU H.264 (avc1) -> mp4-muxer -> Binary Transfer
Zero disk clutter, hardware-accelerated GPU canvas capture, and automatic audio multiplexing.
"""

import os
import sys
import time
import base64
import argparse
import subprocess
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

VENDOR_MUXER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "mp4-muxer.min.js")

def render_scene_webcodecs(
    html_path,
    output_video,
    audio_path=None,
    fps=60,
    duration=15.0,
    width=1920,
    height=1080,
    selector="#masterCanvas",
    bitrate=16_000_000
):
    """
    Zero-IPC WebCodecs Render Engine:
    Encodes H.264/AVC1 directly on the GPU within Chromium, eliminating CDP screenshot overhead.
    """
    html_abs = os.path.abspath(html_path)
    if not os.path.exists(html_abs):
        raise FileNotFoundError(f"HTML scene file not found: {html_abs}")
    if not os.path.exists(VENDOR_MUXER_PATH):
        raise FileNotFoundError(f"mp4-muxer vendor bundle not found: {VENDOR_MUXER_PATH}")
        
    out_video_abs = os.path.abspath(output_video)
    os.makedirs(os.path.dirname(out_video_abs), exist_ok=True)
    
    total_frames = int(duration * fps)
    print(f"[1/4] Initializing WebCodecs Zero-IPC GPU Engine...")
    print(f"      Scene:      {html_abs}")
    print(f"      Resolution: {width}x{height} @ {fps} FPS")
    print(f"      Duration:   {duration:.2f}s ({total_frames} frames)")
    print(f"      Audio:      {audio_path if audio_path else '(None / Silent)'}")
    print(f"      Output:     {out_video_abs}")
    
    t_start = time.time()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(args=[
            "--use-angle=d3d11",
            "--enable-webgl",
            "--ignore-gpu-blocklist"
        ])
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"file:///{html_abs}")
        page.wait_for_selector(selector, timeout=15000)
        try:
            page.wait_for_function("() => typeof window.imagesReady === 'undefined' || window.imagesReady === true", timeout=15000)
        except Exception:
            pass
            
        page.add_script_tag(path=VENDOR_MUXER_PATH)
        
        # Telemetry callback from page
        def on_progress(frame_num):
            elapsed = time.time() - t_start
            sec_rendered = frame_num / fps
            fps_render = frame_num / (elapsed + 1e-6)
            pct = (frame_num / total_frames) * 100
            print(f"      [WebCodecs GPU] Frame {frame_num:04d}/{total_frames} ({sec_rendered:4.1f}s / {pct:5.1f}%) | Speed: {fps_render:4.1f} fps | Elapsed: {elapsed:4.1f}s")
            sys.stdout.flush()
            
        page.expose_function("onProgress", on_progress)
        
        print(f"[2/4] Executing GPU-accelerated WebCodecs encode in Chromium...")
        b64_video = page.evaluate("""async ({ W, H, FPS, N, targetBitrate, sel }) => {
            const { Muxer, ArrayBufferTarget } = window.Mp4Muxer;
            const target = new ArrayBufferTarget();
            const muxer = new Muxer({
                target,
                fastStart: 'in-memory',
                firstTimestampBehavior: 'strict',
                video: { codec: 'avc', width: W, height: H }
            });

            let cfg = {
                codec: 'avc1.64002A',
                width: W, height: H, framerate: FPS, bitrate: targetBitrate,
                latencyMode: 'quality', avc: { format: 'avc' },
                hardwareAcceleration: 'prefer-hardware'
            };
            let sup = await VideoEncoder.isConfigSupported(cfg);
            if (!sup.supported) {
                cfg.hardwareAcceleration = 'no-preference';
                sup = await VideoEncoder.isConfigSupported(cfg);
            }
            if (!sup.supported) {
                throw new Error('H.264 WebCodecs encoder not supported on this platform');
            }

            let encErr = null;
            const enc = new VideoEncoder({
                output: (chunk, meta) => muxer.addVideoChunk(chunk, meta),
                error: e => { encErr = e; }
            });
            enc.configure(sup.config);

            const canvas = document.querySelector(sel) || document.querySelector('canvas');
            for (let i = 0; i < N; i++) {
                const t = i / FPS;
                if (window.renderFrame) window.renderFrame(t);
                
                const ts = Math.round(i * 1e6 / FPS);
                const dur = Math.round((i + 1) * 1e6 / FPS) - ts;
                const frame = new VideoFrame(canvas, { timestamp: ts, duration: dur });
                enc.encode(frame, { keyFrame: i % (FPS * 2) === 0 });
                frame.close();
                
                while (enc.encodeQueueSize > 4) {
                    await new Promise(r => enc.addEventListener('dequeue', r, { once: true }));
                }
                if (encErr) throw encErr;

                if ((i + 1) % 60 === 0 || i === N - 1) {
                    await window.onProgress(i + 1);
                }
            }

            await enc.flush();
            muxer.finalize();

            // Transfer ArrayBuffer as base64 over IPC once
            const blob = new Blob([target.buffer], { type: 'video/mp4' });
            return await new Promise((res) => {
                const fr = new FileReader();
                fr.onload = () => res(fr.result.split(',')[1]);
                fr.readAsDataURL(blob);
            });
        }""", {
            "W": width,
            "H": height,
            "FPS": fps,
            "N": total_frames,
            "targetBitrate": bitrate,
            "sel": selector
        })
        
        browser.close()

    raw_mp4_bytes = base64.b64decode(b64_video)
    
    # Check if audio multiplexing is requested
    if audio_path and os.path.exists(audio_path):
        print("[3/4] Multiplexing audio track with FFmpeg (Lossless Video Copy)...")
        temp_video = out_video_abs + ".temp_v.mp4"
        with open(temp_video, "wb") as f:
            f.write(raw_mp4_bytes)
            
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_exe, "-y",
            "-i", temp_video,
            "-i", os.path.abspath(audio_path),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "256k",
            "-t", str(duration),
            "-movflags", "+faststart",
            out_video_abs
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        try:
            os.remove(temp_video)
        except Exception:
            pass
            
        if res.returncode != 0:
            print(f"FFmpeg mux error:\n{res.stderr}")
            raise RuntimeError("Audio muxing failed")
    else:
        print("[3/4] Writing pure WebCodecs MP4 to disk...")
        with open(out_video_abs, "wb") as f:
            f.write(raw_mp4_bytes)
            
    total_time = time.time() - t_start
    file_size_mb = os.path.getsize(out_video_abs) / (1024 * 1024)
    print(f"[4/4] COMPLETE! WebCodecs zero-IPC rendered in {total_time:.1f}s")
    print(f"      Output: {out_video_abs} ({file_size_mb:.2f} MB)")
    return out_video_abs

def render_scene_ffmpeg(
    html_path,
    output_video,
    audio_path=None,
    fps=60,
    duration=15.0,
    width=1920,
    height=1080,
    selector="#masterCanvas",
    crf=18,
    preset="medium",
    keyframe_time=None,
    keyframe_out=None
):
    """
    In-Memory Pipe Render Engine:
    Playwright WebGL2 -> Synchronous MJPEG -> FFmpeg libx264
    """
    html_abs = os.path.abspath(html_path)
    if not os.path.exists(html_abs):
        raise FileNotFoundError(f"HTML scene file not found: {html_abs}")
        
    out_video_abs = os.path.abspath(output_video)
    os.makedirs(os.path.dirname(out_video_abs), exist_ok=True)
    
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    # --- KEYFRAME PREVIEW MODE ---
    if keyframe_time is not None:
        target_out = keyframe_out or (os.path.splitext(out_video_abs)[0] + "_keyframe.png")
        print(f"[Keyframe Mode] Rendering snapshot at t={keyframe_time:.2f}s...")
        with sync_playwright() as p:
            browser = p.chromium.launch(args=[
                "--use-angle=d3d11",
                "--enable-webgl",
                "--ignore-gpu-blocklist"
            ])
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(f"file:///{html_abs}")
            page.wait_for_selector(selector, timeout=15000)
            try:
                page.wait_for_function("() => typeof window.imagesReady === 'undefined' || window.imagesReady === true", timeout=15000)
            except Exception:
                pass
            page.evaluate(f"window.renderFrame ? window.renderFrame({keyframe_time}) : null")
            elem = page.locator(selector)
            elem.screenshot(path=target_out)
            browser.close()
        print(f"[Keyframe Mode] Saved: {target_out} ({os.path.getsize(target_out)} bytes)")
        return target_out

    # --- FULL VIDEO RENDER MODE ---
    total_frames = int(duration * fps)
    print(f"[1/4] Initializing FFmpeg Pipe Render Engine...")
    print(f"      Scene:      {html_abs}")
    print(f"      Resolution: {width}x{height} @ {fps} FPS")
    print(f"      Duration:   {duration:.2f}s ({total_frames} frames)")
    print(f"      Audio:      {audio_path if audio_path else '(None / Silent)'}")
    print(f"      Output:     {out_video_abs}")
    
    cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "image2pipe",
        "-vcodec", "mjpeg",
        "-framerate", str(fps),
        "-i", "-"
    ]
    
    if audio_path and os.path.exists(audio_path):
        cmd.extend(["-i", os.path.abspath(audio_path)])
        
    cmd.extend([
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-pix_fmt", "yuv420p"
    ])
    
    if audio_path and os.path.exists(audio_path):
        cmd.extend(["-c:a", "aac", "-b:a", "256k"])
        
    cmd.extend(["-t", str(duration), "-movflags", "+faststart", out_video_abs])
    
    ffmpeg_proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE
    )
    
    t_start = time.time()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=[
                "--use-angle=d3d11",
                "--enable-webgl",
                "--ignore-gpu-blocklist"
            ])
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(f"file:///{html_abs}")
            page.wait_for_selector(selector, timeout=15000)
            try:
                page.wait_for_function("() => typeof window.imagesReady === 'undefined' || window.imagesReady === true", timeout=15000)
            except Exception:
                pass
            locator = page.locator(selector)
            
            print(f"[2/4] Rendering & streaming {total_frames} frames into FFmpeg...")
            for frame in range(total_frames):
                t = frame / fps
                page.evaluate(f"window.renderFrame ? window.renderFrame({t}) : null")
                frame_bytes = locator.screenshot(type="jpeg", quality=95)
                ffmpeg_proc.stdin.write(frame_bytes)
                
                if (frame + 1) % 60 == 0 or frame == total_frames - 1:
                    elapsed = time.time() - t_start
                    sec_rendered = (frame + 1) / fps
                    fps_render = (frame + 1) / (elapsed + 1e-6)
                    pct = ((frame + 1) / total_frames) * 100
                    print(f"      Frame {frame + 1:04d}/{total_frames} ({sec_rendered:4.1f}s / {pct:5.1f}%) | Speed: {fps_render:4.1f} fps | Elapsed: {elapsed:4.1f}s")
                    sys.stdout.flush()
                    
            browser.close()
    except Exception as e:
        ffmpeg_proc.kill()
        raise e
    finally:
        if ffmpeg_proc.stdin and not ffmpeg_proc.stdin.closed:
            try:
                ffmpeg_proc.stdin.close()
            except Exception:
                pass
        
    print("[3/4] Finalizing FFmpeg encoding...")
    stderr_out = ffmpeg_proc.stderr.read()
    ffmpeg_proc.wait()
    
    if ffmpeg_proc.returncode != 0:
        err_msg = stderr_out.decode('utf-8', errors='ignore')
        print(f"FFmpeg error:\n{err_msg}")
        raise RuntimeError("FFmpeg encoding failed")
        
    total_time = time.time() - t_start
    file_size_mb = os.path.getsize(out_video_abs) / (1024 * 1024)
    print(f"[4/4] COMPLETE! Rendered in {total_time:.1f}s")
    print(f"      Output: {out_video_abs} ({file_size_mb:.2f} MB)")
    return out_video_abs

def render_scene(
    html_path,
    output_video,
    audio_path=None,
    fps=60,
    duration=15.0,
    width=1920,
    height=1080,
    selector="#masterCanvas",
    engine="ffmpeg",
    crf=18,
    preset="medium",
    keyframe_time=None,
    keyframe_out=None
):
    if keyframe_time is not None or engine == "ffmpeg":
        return render_scene_ffmpeg(
            html_path=html_path,
            output_video=output_video,
            audio_path=audio_path,
            fps=fps,
            duration=duration,
            width=width,
            height=height,
            selector=selector,
            crf=crf,
            preset=preset,
            keyframe_time=keyframe_time,
            keyframe_out=keyframe_out
        )
    elif engine == "webcodecs":
        return render_scene_webcodecs(
            html_path=html_path,
            output_video=output_video,
            audio_path=audio_path,
            fps=fps,
            duration=duration,
            width=width,
            height=height,
            selector=selector
        )
    else:
        raise ValueError(f"Unknown render engine: {engine}. Choose 'ffmpeg' or 'webcodecs'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Video Render Engine for /genflow")
    parser.add_argument("--html", required=True, help="Path to WebGL/HTML scene")
    parser.add_argument("--out", default="output.mp4", help="Output MP4 file path")
    parser.add_argument("--audio", default=None, help="Path to audio file (WAV/MP3)")
    parser.add_argument("--engine", choices=["ffmpeg", "webcodecs"], default="ffmpeg", help="Rendering engine backend")
    parser.add_argument("--fps", type=int, default=60, help="Framerate (default: 60)")
    parser.add_argument("--duration", type=float, default=15.0, help="Duration in seconds (default: 15.0)")
    parser.add_argument("--width", type=int, default=1920, help="Width in pixels (default: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Height in pixels (default: 1080)")
    parser.add_argument("--selector", default="#masterCanvas", help="Canvas CSS selector (default: #masterCanvas)")
    parser.add_argument("--keyframe", type=float, default=None, help="If set, renders single PNG keyframe at time t")
    parser.add_argument("--keyframe-out", default=None, help="Keyframe PNG output path")
    args = parser.parse_args()
    
    render_scene(
        html_path=args.html,
        output_video=args.out,
        audio_path=args.audio,
        fps=args.fps,
        duration=args.duration,
        width=args.width,
        height=args.height,
        selector=args.selector,
        engine=args.engine,
        keyframe_time=args.keyframe,
        keyframe_out=args.keyframe_out
    )
