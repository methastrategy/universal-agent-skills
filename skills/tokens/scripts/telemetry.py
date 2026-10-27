import os
import sys
import json
import glob
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

def get_brain_dir():
    return r"~\.gemini\antigravity\brain"

def get_latest_conversation(brain_dir):
    dirs = [d for d in glob.glob(os.path.join(brain_dir, "*")) if os.path.isdir(d) and not d.endswith("tempmediaStorage")]
    if not dirs:
        return None
    valid_dirs = []
    for d in dirs:
        tpath = os.path.join(d, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(tpath):
            valid_dirs.append((d, os.path.getmtime(tpath)))
    if not valid_dirs:
        return None
    valid_dirs.sort(key=lambda x: x[1], reverse=True)
    return valid_dirs[0][0]

def analyze_transcript(conv_dir):
    tpath = os.path.join(conv_dir, ".system_generated", "logs", "transcript.jsonl")
    if not os.path.exists(tpath):
        return None
    
    total_in = 0
    total_cache = 0
    total_out = 0
    steps = 0
    turns = 0
    first_step_input = None
    last_turn_input = 0
    last_turn_cache = 0
    last_turn_out = 0
    
    with open(tpath, "r", encoding="utf-8") as f:
        for line in f:
            steps += 1
            d = json.loads(line)
            if d.get("source") == "USER_EXPLICIT" and d.get("type") == "USER_INPUT":
                turns += 1
            inp = d.get("input_tokens")
            cache = d.get("cache_read_tokens")
            out = d.get("output_tokens")
            
            if inp is not None:
                total_in += inp
                last_turn_input = inp
                if first_step_input is None:
                    first_step_input = inp + (cache or 0)
            if cache is not None:
                total_cache += cache
                last_turn_cache = cache
            if out is not None:
                total_out += out
                last_turn_out = out
                
    cache_pct = (total_cache / (total_in + total_cache) * 100) if (total_in + total_cache) > 0 else 0
    avg_out = (total_out / steps) if steps > 0 else 0
    
    return {
        "conv_id": os.path.basename(conv_dir),
        "steps": steps,
        "turns": turns,
        "base_input": first_step_input or 0,
        "fresh_input": total_in,
        "cache_read": total_cache,
        "output_tokens": total_out,
        "cache_hit_pct": round(cache_pct, 2),
        "avg_out_step": round(avg_out, 1),
        "last_step": {
            "input": last_turn_input,
            "cache": last_turn_cache,
            "output": last_turn_out
        }
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AGY Session Token Telemetry")
    parser.add_argument("--conv", type=str, default=None, help="Conversation ID (default: latest active transcript)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    brain = get_brain_dir()
    target_dir = os.path.join(brain, args.conv) if args.conv else get_latest_conversation(brain)

    if not target_dir or not os.path.exists(target_dir):
        print("Error: Conversation transcript not found.", file=sys.stderr)
        sys.exit(1)

    res = analyze_transcript(target_dir)
    if not res:
        print("Error: Could not parse transcript.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"📊 [Token Telemetry: {res['conv_id'][:8]}...]")
        print(f"• Total Steps / Turns: {res['steps']} steps | {res['turns']} user turns")
        print(f"• Base Input (Turn 1): {res['base_input']:,} tokens")
        print(f"• Fresh Input Tokens:  {res['fresh_input']:,} tokens")
        print(f"• Prompt Cache Read:   {res['cache_read']:,} tokens (Hit: {res['cache_hit_pct']}%)")
        print(f"• Output Generated:    {res['output_tokens']:,} tokens (Avg: {res['avg_out_step']}/step)")
        ls = res['last_step']
        print(f"• Latest Step Tokens:  Input={ls['input']:,} | Cache={ls['cache']:,} | Output={ls['output']:,}")
