"""
GenFlow Production Orchestrator: State Machine & Central Ledger
Manages production_manifest.json, character visual consistency, scene queues,
timecode synchronization with audio DSP timeline, and Zero-Fluff Prompt Engineering.
"""

import os
import sys
import re
import json
import time
import argparse
from datetime import datetime

# --- ZERO-FLUFF PROMPT ENGINE CONSTANTS ---

BANNED_QUALITY_WORDS = [
    "8k",
    "masterpiece",
    "hyperrealistic",
    "perfect skin",
    "smooth skin",
    "cinematic lighting"
]

CAMERA_STYLE_TOKENS = {
    "arri": "ARRI Alexa 35, Cooke S4/i prime lens",
    "hasselblad": "Hasselblad X2D 100C, micro-contrast medium format",
    "leica": "Leica M11, Summilux-M 35mm f/1.4 ASPH",
    "hero_portrait": "85mm f/1.4, shallow depth of field, subject separation",
    "macro": "100mm macro f/4.0, edge-to-edge optical resolution"
}

FLUX_POSITIVE_SUBSTITUTIONS = (
    "visible skin pores, fine vellus hair, subtle uneven skin tone, "
    "natural under-eye texture, fine expression lines, stray flyaway hair strands"
)

SD_NEGATIVE_BASELINE = (
    "plastic skin, wax figure, CGI, 3D render, oversharpened, airbrushed, "
    "cartoon, extra limbs, mutated hands, watermark, signature"
)

def sanitize_prompt(prompt: str) -> tuple[str, list[str]]:
    """Detect and remove quality-spam banned words and correct optical lens misconfigurations."""
    warnings = []
    cleaned = prompt
    for w in BANNED_QUALITY_WORDS:
        pattern = re.compile(rf"\b{re.escape(w)}\b", re.IGNORECASE)
        if pattern.search(cleaned):
            warnings.append(f"Removed banned quality-spam word: '{w}'")
            cleaned = pattern.sub("", cleaned)

    # Check for macro f/1.4 misconfiguration
    macro_f14 = re.compile(r"\bmacro\b.*?\bf/1\.4\b|\bf/1\.4\b.*?\bmacro\b", re.IGNORECASE)
    if macro_f14.search(cleaned):
        warnings.append("Macro with f/1.4 detected (DoF too shallow). Corrected to f/4.0.")
        cleaned = re.sub(r"\bf/1\.4\b", "f/4.0", cleaned, flags=re.IGNORECASE)

    # Clean redundant commas and whitespaces
    cleaned = re.sub(r"(?:,\s*){2,}", ", ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,")
    # In case there are still standalone commas
    cleaned = re.sub(r"\s*,\s*", ", ", cleaned).strip(" ,")
    return cleaned, warnings

def compile_zero_fluff_prompt(
    subject_state: str,
    setting: str,
    composition: str,
    camera_lens: str,
    light: str,
    color_grade: str,
    material_imperfection: str,
    engine_params: str = "",
    engine: str = "default"
) -> tuple[str, str]:
    """
    Assembles a prompt following the strict Zero-Fluff Formula:
    [1 Subject + State] -> [2 Setting (1 clause)] -> [3 Composition] ->
    [4 Camera + Lens] -> [5 Light] -> [6 Color Grade] ->
    [7 Material + 1 Asymmetric Imperfection] -> [8 Engine Params]
    
    Returns (positive_prompt, negative_prompt)
    """
    slots = [
        subject_state.strip(),
        setting.strip(),
        composition.strip(),
        camera_lens.strip(),
        light.strip(),
        color_grade.strip(),
        material_imperfection.strip()
    ]
    raw_positive = ", ".join([s for s in slots if s])
    sanitized_positive, _ = sanitize_prompt(raw_positive)

    engine_key = engine.lower()
    negative_prompt = ""

    if engine_key == "flux":
        # Flux.1: Zero negative prompt. Inject natural positive skin texture if humans involved
        human_keywords = ["person", "people", "woman", "man", "female", "male", "human", "face", "portrait", "character", "surveyor", "girl", "boy"]
        if any(k in raw_positive.lower() for k in human_keywords):
            if "pores" not in sanitized_positive.lower():
                sanitized_positive = f"{sanitized_positive}, {FLUX_POSITIVE_SUBSTITUTIONS}"
        # Strip any --no parameters
        engine_params = re.sub(r"--no\s+[\w\s,]+", "", engine_params).strip()
        negative_prompt = ""
    elif engine_key in ("midjourney", "mj"):
        # Midjourney v6: Enforce --style raw and --s 0-100, avoid --no spam
        engine_params = re.sub(r"--no\s+[\w\s,]+", "", engine_params).strip()
        if "--style" not in engine_params:
            engine_params = f"{engine_params} --style raw".strip()
        if not re.search(r"--s\s+\d+", engine_params):
            engine_params = f"{engine_params} --s 75".strip()
        negative_prompt = ""
    elif engine_key in ("sd", "sdxl", "stablediffusion"):
        negative_prompt = SD_NEGATIVE_BASELINE

    final_positive = f"{sanitized_positive} {engine_params}".strip()
    return final_positive, negative_prompt

# --- CORE ORCHESTRATOR CLASS ---

class GenFlowOrchestrator:
    def __init__(self, project_name="GenFlow_Project", output_dir="./project"):
        self.project_name = project_name
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.manifest_path = os.path.join(self.output_dir, "production_manifest.json")
        self.manifest = self._load_or_init_manifest()

    def _load_or_init_manifest(self):
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "project_name": self.project_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "INITIALIZED",
            "bpm": 120.0,
            "total_duration": 15.0,
            "character_bible": {},
            "scenes": []
        }

    def save_manifest(self):
        self.manifest["updated_at"] = datetime.now().isoformat()
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        return self.manifest_path

    def set_character_bible(self, name, description, visual_anchors, negative_prompt=""):
        self.manifest["character_bible"] = {
            "name": name,
            "description": description,
            "visual_anchors": visual_anchors,
            "negative_prompt": negative_prompt
        }
        self.save_manifest()

    def add_scenes(self, scene_list, sanitize=True):
        current_count = len(self.manifest["scenes"])
        for idx, sc in enumerate(scene_list, current_count + 1):
            raw_prompt = sc.get("prompt", "")
            if sanitize and raw_prompt:
                clean_prompt, warnings = sanitize_prompt(raw_prompt)
                if warnings:
                    print(f"Scene {idx} prompt sanitized: {', '.join(warnings)}")
            else:
                clean_prompt = raw_prompt

            scene_entry = {
                "id": sc.get("id", f"scene_{idx:02d}"),
                "title": sc.get("title", f"Scene {idx}"),
                "action": sc.get("action", ""),
                "camera": sc.get("camera", "medium shot"),
                "prompt": clean_prompt,
                "duration_seconds": float(sc.get("duration", 3.0)),
                "start_time": 0.0,
                "end_time": 0.0,
                "status": "PENDING",
                "raw_file": None,
                "processed_file": None,
                "error": None
            }
            self.manifest["scenes"].append(scene_entry)
        self.sync_timecodes()
        self.save_manifest()

    def lint_manifest_prompts(self) -> dict[str, list[str]]:
        results = {}
        for sc in self.manifest.get("scenes", []):
            sc_id = sc["id"]
            prompt = sc.get("prompt", "")
            _, warnings = sanitize_prompt(prompt)
            if warnings:
                results[sc_id] = warnings
        return results

    def sync_timecodes(self, total_duration=None, bpm=None):
        if total_duration:
            self.manifest["total_duration"] = float(total_duration)
        if bpm:
            self.manifest["bpm"] = float(bpm)
            
        scenes = self.manifest.get("scenes", [])
        if not scenes:
            return
            
        cur_t = 0.0
        for sc in scenes:
            dur = sc.get("duration_seconds", 3.0)
            sc["start_time"] = round(cur_t, 3)
            sc["end_time"] = round(cur_t + dur, 3)
            dur_field = sc.get("duration")
            if not dur_field:
                sc["duration"] = dur
            cur_t += dur
            
        self.manifest["total_duration"] = round(cur_t, 3)
        
        # Export compiled timeline.json contract for DSP & 3D WebGL
        timeline_path = os.path.join(self.output_dir, "timeline.json")
        timeline_contract = {
            "project_name": self.manifest.get("project_name"),
            "bpm": self.manifest.get("bpm", 120.0),
            "duration": self.manifest.get("total_duration", 15.0),
            "scenes": [
                {
                    "id": sc["id"],
                    "start": sc["start_time"],
                    "end": sc["end_time"],
                    "title": sc["title"],
                    "camera": sc["camera"]
                }
                for sc in scenes
            ]
        }
        with open(timeline_path, "w", encoding="utf-8") as f:
            json.dump(timeline_contract, f, indent=2, ensure_ascii=False)
            
        self.save_manifest()

    def update_scene_status(self, scene_id, status, raw_file=None, processed_file=None, error=None):
        for sc in self.manifest["scenes"]:
            if sc["id"] == scene_id:
                sc["status"] = status
                if raw_file: sc["raw_file"] = raw_file
                if processed_file: sc["processed_file"] = processed_file
                if error: sc["error"] = error
                break
        self.save_manifest()

    def get_pending_scenes(self):
        return [sc for sc in self.manifest["scenes"] if sc["status"] in ("PENDING", "FAILED")]

    def summary(self):
        total = len(self.manifest["scenes"])
        done = len([sc for sc in self.manifest["scenes"] if sc["status"] in ("DONE", "POST_PROCESSED")])
        lint_issues = self.lint_manifest_prompts()
        lines = [
            f"=== GenFlow Orchestrator [{self.manifest['project_name']}] ===",
            f"Directory:    {self.output_dir}",
            f"Total Scenes: {total} | Completed: {done} | Pending: {total - done}",
            f"Duration:     {self.manifest.get('total_duration', 0.0)}s @ {self.manifest.get('bpm', 120)} BPM",
            f"Prompt Lint:  {'✓ Clean (Zero quality-spam)' if not lint_issues else f'⚠ {len(lint_issues)} scenes have quality-spam'}",
            f"Manifest:     {self.manifest_path}"
        ]
        for sc in self.manifest["scenes"]:
            status_icon = "✓" if sc["status"] in ("DONE", "POST_PROCESSED") else "•"
            lines.append(f"  [{status_icon}] {sc['id']}: {sc['title']} ({sc['start_time']}s - {sc['end_time']}s) -> {sc['status']}")
        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="GenFlow Orchestrator & Zero-Fluff Prompt Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # init
    p_init = subparsers.add_parser("init", help="Initialize a new production project")
    p_init.add_argument("--project", default="GenFlow_Project", help="Project name")
    p_init.add_argument("--out", default="./project", help="Project output directory")
    p_init.add_argument("--bpm", type=float, default=120.0, help="Tempo in BPM")

    # status
    p_status = subparsers.add_parser("status", help="Show project status summary")
    p_status.add_argument("--out", default="./project", help="Project directory")

    # add-scenes
    p_add = subparsers.add_parser("add-scenes", help="Add scenes from JSON file")
    p_add.add_argument("--out", default="./project", help="Project directory")
    p_add.add_argument("--file", required=True, help="JSON file containing array of scenes")
    p_add.add_argument("--no-sanitize", action="store_true", help="Skip prompt quality-spam sanitation")

    # sync
    p_sync = subparsers.add_parser("sync", help="Recalculate timecodes and sync timeline.json")
    p_sync.add_argument("--out", default="./project", help="Project directory")
    p_sync.add_argument("--bpm", type=float, help="Override BPM")
    p_sync.add_argument("--duration", type=float, help="Override total duration")

    # lint-prompt
    p_lint = subparsers.add_parser("lint-prompt", help="Check and clean prompt against banned quality words")
    p_lint.add_argument("--prompt", required=True, help="Prompt text to inspect")

    # build-prompt
    p_build = subparsers.add_parser("build-prompt", help="Build a Zero-Fluff prompt via 8-slot formula")
    p_build.add_argument("--subject", required=True, help="[Slot 1] Subject and state")
    p_build.add_argument("--setting", default="", help="[Slot 2] Setting (1 clause)")
    p_build.add_argument("--comp", default="", help="[Slot 3] Composition")
    p_build.add_argument("--camera", default="ARRI Alexa 35, Cooke 50mm T2.0", help="[Slot 4] Camera + Lens")
    p_build.add_argument("--light", default="", help="[Slot 5] Lighting specification")
    p_build.add_argument("--color", default="", help="[Slot 6] Color Grade / Stock")
    p_build.add_argument("--material", default="", help="[Slot 7] Material + 1 Asymmetric Imperfection")
    p_build.add_argument("--params", default="", help="[Slot 8] Engine parameters")
    p_build.add_argument("--engine", default="default", choices=["default", "flux", "midjourney", "sd"], help="Target AI engine")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    if args.command == "init":
        orc = GenFlowOrchestrator(project_name=args.project, output_dir=args.out)
        orc.manifest["bpm"] = args.bpm
        orc.save_manifest()
        print(f"Project initialized at {args.out}")
        print(orc.summary())
    elif args.command == "status":
        orc = GenFlowOrchestrator(output_dir=args.out)
        print(orc.summary())
    elif args.command == "add-scenes":
        orc = GenFlowOrchestrator(output_dir=args.out)
        with open(args.file, "r", encoding="utf-8") as f:
            sc_list = json.load(f)
        orc.add_scenes(sc_list, sanitize=not args.no_sanitize)
        print(f"Added {len(sc_list)} scenes.")
        print(orc.summary())
    elif args.command == "sync":
        orc = GenFlowOrchestrator(output_dir=args.out)
        orc.sync_timecodes(total_duration=args.duration, bpm=args.bpm)
        print("Timecodes synchronized & timeline.json exported.")
        print(orc.summary())
    elif args.command == "lint-prompt":
        cleaned, warnings = sanitize_prompt(args.prompt)
        print("=== Prompt Lint Result ===")
        if warnings:
            for w in warnings:
                print(f"  [WARNING] {w}")
        else:
            print("  [OK] Clean! No quality-spam detected.")
        print(f"\nOriginal:  {args.prompt}")
        print(f"Sanitized: {cleaned}")
    elif args.command == "build-prompt":
        pos, neg = compile_zero_fluff_prompt(
            subject_state=args.subject,
            setting=args.setting,
            composition=args.comp,
            camera_lens=args.camera,
            light=args.light,
            color_grade=args.color,
            material_imperfection=args.material,
            engine_params=args.params,
            engine=args.engine
        )
        print(f"=== Zero-Fluff Prompt ({args.engine.upper()}) ===")
        print(f"Positive: {pos}")
        if neg:
            print(f"Negative: {neg}")

if __name__ == "__main__":
    main()
