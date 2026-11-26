import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

def get_brain_dir():
    return Path.home() / ".gemini" / "antigravity" / "brain"

def find_transcript(brain_dir, conversation_id=None):
    """Return the conversation identity and the exact transcript path to read."""
    brain_dir = brain_dir.resolve()
    if conversation_id is not None:
        if (not conversation_id or conversation_id in {".", ".."} or
                any(char in conversation_id for char in "/\\:")):
            raise ValueError("Invalid conversation ID.")
        directories = [brain_dir / conversation_id]
    elif brain_dir.is_dir():
        directories = [path for path in brain_dir.iterdir() if not path.name.startswith(".")]
    else:
        directories = []

    matches = []
    for directory in directories:
        if directory.resolve() != directory:
            continue
        for preference, relative in enumerate(("transcript.jsonl", ".system_generated/logs/transcript.jsonl")):
            candidate = directory / relative
            if candidate.is_file() and candidate.resolve().is_relative_to(directory):
                matches.append((candidate.stat().st_mtime_ns, directory.name, preference, candidate))
    if matches:
        _, name, _, path = max(matches)
        return name, path
    return None
    
def analyze_transcript(conversation_id, transcript):
    total_in = 0
    total_cache = 0
    total_out = 0
    steps = 0
    turns = 0
    first_step_input = None
    last_step = {}
    incomplete_tail = False
    observed = set()

    with transcript.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError as error:
                if not line.endswith("\n"):
                    incomplete_tail = True
                    break
                raise ValueError(f"Invalid JSON at line {number}.") from error
            if not isinstance(d, dict):
                raise ValueError(f"Expected an object at line {number}.")
            recorded = {}
            for field in ("input_tokens", "cache_read_tokens", "output_tokens"):
                value = d.get(field)
                if value is not None:
                    if type(value) is not int or value < 0:
                        raise ValueError(f"Invalid {field} at line {number}.")
                    recorded[field] = value
            if recorded:
                observed.update(recorded)
                last_step = recorded
            steps += 1
            if d.get("source") == "USER_EXPLICIT" and d.get("type") == "USER_INPUT":
                turns += 1
            inp = d.get("input_tokens")
            cache = d.get("cache_read_tokens")
            out = d.get("output_tokens")
            
            if inp is not None:
                total_in += inp
                if first_step_input is None:
                    first_step_input = inp + (cache or 0)
            if cache is not None:
                total_cache += cache
            if out is not None:
                total_out += out
                
    cache_pct = (total_cache / (total_in + total_cache) * 100) if (total_in + total_cache) > 0 else 0
    avg_out = (total_out / steps) if steps > 0 else 0
    
    return {
        "conv_id": conversation_id,
        "status": "partial" if incomplete_tail else "ok" if observed else "no_usage" if steps else "empty",
        "observed_metrics": sorted(observed),
        "last_step_observed_metrics": sorted(last_step),
        "steps": steps,
        "turns": turns,
        "base_input": first_step_input or 0,
        "fresh_input": total_in,
        "cache_read": total_cache,
        "output_tokens": total_out,
        "cache_hit_pct": round(cache_pct, 2),
        "avg_out_step": round(avg_out, 1),
        "last_step": {
            "input": last_step.get("input_tokens", 0),
            "cache": last_step.get("cache_read_tokens", 0),
            "output": last_step.get("output_tokens", 0)
        }
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AGY Session Token Telemetry")
    parser.add_argument("--conv", type=str, default=None, help="Conversation ID (default: latest active transcript)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    try:
        selection = find_transcript(get_brain_dir(), args.conv)
        if selection is None:
            raise ValueError("Conversation transcript not found.")
        res = analyze_transcript(*selection)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"📊 [Token Telemetry: {res['conv_id'][:8]}...]")
        if res["status"] != "ok":
            print(f"• Data status: {res['status']}")
        if len(res["observed_metrics"]) < 3:
            print(f"• Recorded metrics: {', '.join(res['observed_metrics']) or 'none'}")
        print(f"• Total Steps / Turns: {res['steps']} steps | {res['turns']} user turns")
        print(f"• Base Input (Turn 1): {res['base_input']:,} tokens")
        print(f"• Fresh Input Tokens:  {res['fresh_input']:,} tokens")
        print(f"• Prompt Cache Read:   {res['cache_read']:,} tokens (Hit: {res['cache_hit_pct']}%)")
        print(f"• Output Generated:    {res['output_tokens']:,} tokens (Avg: {res['avg_out_step']}/step)")
        ls = res['last_step']
        print(f"• Latest Step Tokens:  Input={ls['input']:,} | Cache={ls['cache']:,} | Output={ls['output']:,}")
        if len(res["last_step_observed_metrics"]) < 3:
            metrics = ", ".join(res["last_step_observed_metrics"]) or "none"
            print(f"• Latest step recorded metrics: {metrics}")
