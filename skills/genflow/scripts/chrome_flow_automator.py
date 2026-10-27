"""
Chrome Flow Automator for /genflow
Connects to an existing Chrome browser session or persistent profile (~/.genflow_chrome_profile)
to automate prompt submission and image extraction from Google Flow (https://flow.google.com/).
Features:
- Automated navigation into Google Flow Workspace / Projects (.new-project-button)
- Direct ProseMirror rich-editor manipulation for prompt injection
- Authenticated in-page fetch pipeline for downloading high-res images (flow.google.com/asb)
- Full batch execution via production_manifest.json with live status syncing
"""

import os
import sys
import time
import json
import base64
import argparse
from playwright.sync_api import sync_playwright

DEFAULT_FLOW_URL = "https://flow.google.com/"

def ensure_in_project_workspace(page, url=DEFAULT_FLOW_URL):
    """Navigate to Google Flow and ensure we are inside a project workspace"""
    if "flow.google.com/project/" not in page.url:
        target = url or DEFAULT_FLOW_URL
        print(f"[Google Flow] Navigating to {target}...")
        page.goto(target, wait_until="networkidle")
        page.keyboard.press("Escape")
        time.sleep(2)
        
    if "flow.google.com/project/" not in page.url:
        # Click .new-project-button
        new_proj_btn = page.locator(".new-project-button, button:has-text('โปรเจกต์ใหม่'), a[aria-label='เปิดโปรเจ็กต์']").first
        if new_proj_btn.is_visible():
            print("[Google Flow] Clicking New Project button (.new-project-button)...")
            new_proj_btn.click()
            time.sleep(5)
            
    # Check if inside project workspace
    prompt_box = page.locator("div.ProseMirror").first
    if not prompt_box.is_visible():
        # Wait up to 30s
        try:
            page.wait_for_selector("div.ProseMirror", timeout=30000)
            prompt_box = page.locator("div.ProseMirror").first
        except Exception:
            pass
            
    return prompt_box

def generate_and_download_flow_image(page, prompt, output_path, timeout_sec=60):
    """Submit prompt to Google Flow and download the resulting rendered image"""
    prompt_box = page.locator("div.ProseMirror").first
    if not prompt_box.is_visible():
        raise RuntimeError("ProseMirror prompt box not visible in Google Flow workspace.")

    # Count existing images on page before generating
    prior_imgs = page.evaluate("() => Array.from(document.querySelectorAll('img')).map(i => i.src)")
    
    print(f"[Google Flow] Injecting Prompt: {prompt[:80]}...")
    prompt_box.click()
    prompt_box.fill(prompt)
    time.sleep(1)

    # Click generate icon button
    gen_btn = page.locator(".generate-icon-button, button[aria-label='เริ่มสร้าง']").first
    if gen_btn.is_visible() and "disabled" not in (gen_btn.get_attribute("class") or ""):
        gen_btn.click()
        print("[Google Flow] Clicked Generate button.")
    else:
        page.keyboard.press("Enter")
        print("[Google Flow] Sent Enter key.")

    # Wait for generation to start and finish
    print("[Google Flow] Awaiting generation completion...")
    start_time = time.time()
    time.sleep(6) # Initial debounce
    
    new_src = None
    while time.time() - start_time < timeout_sec:
        # Check if stop button is present
        stop_btn = page.locator("button:has-text('หยุด'), [aria-label*='หยุด' i]").first
        is_generating = stop_btn.is_visible() if stop_btn else False
        
        # Look for newly appeared images
        current_imgs = page.evaluate("() => Array.from(document.querySelectorAll('img')).map(i => i.src)")
        diff = [s for s in current_imgs if s not in prior_imgs and ("flow.google.com/asb" in s or "googleusercontent.com" in s)]
        
        if diff:
            new_src = diff[-1]
            if not is_generating:
                print(f"[Google Flow] Image generated successfully! ({new_src[:60]}...)")
                break
        elif not is_generating:
            # Check if any image has flow.google.com/asb
            all_flow_imgs = [s for s in current_imgs if "flow.google.com/asb" in s]
            if all_flow_imgs:
                new_src = all_flow_imgs[-1]
                print(f"[Google Flow] Found generated canvas image ({new_src[:60]}...)")
                break
                
        time.sleep(3)

    if not new_src:
        # Fallback to screenshot of main canvas or media card
        print("[Google Flow] Notice: Image URL not isolated directly. Capturing high-res card screenshot...")
        card = page.locator(".media-card, .grid-item, canvas, img[src*='asb']").first
        if card.is_visible():
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            card.screenshot(path=output_path)
            print(f"[Google Flow] Captured screenshot: {output_path} ({os.path.getsize(output_path)} bytes)")
            return output_path
        raise TimeoutError("Google Flow generation timed out or failed to render.")

    # Authenticated in-page fetch to extract high-res bytes
    print(f"[Google Flow] Downloading image via in-page authenticated fetch...")
    b64 = page.evaluate("""async (url) => {
        const res = await fetch(url, { credentials: 'include' });
        const blob = await res.blob();
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result.split(',')[1]);
            reader.readAsDataURL(blob);
        });
    }""", new_src)

    data = base64.b64decode(b64)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(data)

    print(f"[Google Flow] Done! Saved: {output_path} ({len(data)} bytes)")
    return output_path

def automate_prompt(prompt, output_file="./out.png", url=DEFAULT_FLOW_URL):
    user_data = os.path.expanduser("~/.genflow_chrome_profile")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=user_data,
            headless=True,
            channel="chrome"
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        ensure_in_project_workspace(page, url=url)
        res = generate_and_download_flow_image(page, prompt, output_file)
        ctx.close()
        return res

def automate_manifest(manifest_path, url=DEFAULT_FLOW_URL, force=False):
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    scenes = manifest.get("scenes", [])
    if not scenes:
        print("No scenes found in manifest.")
        return

    manifest_dir = os.path.dirname(os.path.abspath(manifest_path))
    assets_dir = os.path.join(manifest_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    user_data = os.path.expanduser("~/.genflow_chrome_profile")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=user_data,
            headless=True,
            channel="chrome"
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        ensure_in_project_workspace(page, url=url)

        for sc in scenes:
            sc_id = sc.get("id", "scene")
            prompt = sc.get("prompt", "")
            if not prompt:
                continue
                
            out_png = os.path.join(assets_dir, f"{sc_id}_flow.png")
            if os.path.exists(out_png) and not force:
                print(f"[Google Flow] Skipping {sc_id} (already generated: {out_png}). Use --force to overwrite.")
                continue

            print(f"\n[Google Flow] Generating Scene '{sc.get('title', sc_id)}'...")
            try:
                generate_and_download_flow_image(page, prompt, out_png)
                sc["raw_file"] = out_png
                sc["processed_file"] = out_png
                sc["status"] = "DONE"
                with open(manifest_path, "w", encoding="utf-8") as fw:
                    json.dump(manifest, fw, indent=2, ensure_ascii=False)
                print(f"[Google Flow] Manifest updated for {sc_id} -> {out_png}")
            except Exception as e:
                print(f"[Google Flow] Error generating {sc_id}: {e}")
                
        ctx.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Flow (flow.google.com) Automator for /genflow")
    parser.add_argument("--prompt", help="Image prompt text")
    parser.add_argument("--manifest", help="Path to production_manifest.json for batch generation")
    parser.add_argument("--url", default=DEFAULT_FLOW_URL, help=f"Google Flow URL (default: {DEFAULT_FLOW_URL})")
    parser.add_argument("--out", default="./out.png", help="Output image file path")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing scenes in manifest")
    args = parser.parse_args()
    
    if args.manifest:
        automate_manifest(args.manifest, url=args.url, force=args.force)
    elif args.prompt:
        automate_prompt(args.prompt, output_file=args.out, url=args.url)
    else:
        parser.print_help()
