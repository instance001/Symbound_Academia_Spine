import os, json, re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

def resolve_path(path):
    p = Path(path).expanduser()
    return p if p.is_absolute() else ROOT / p

def load_config(path=None):
    config_path = resolve_path(path or os.environ.get("ACADEMIA_SPINE_CONFIG", "spine_academia_config.json"))
    with config_path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)

def normalize(text):
    return text.replace("\r\n", "\n").strip()

def classify_topics(text, topics_cfg):
    hits = []
    lower = text.lower()
    for topic, keywords in topics_cfg.items():
        for kw in keywords:
            if kw.lower() in lower:
                hits.append(topic)
                break
    return hits

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def main():
    cfg = load_config()
    export_path = resolve_path(cfg["export_path"])
    out_base = resolve_path(os.environ.get("ACADEMIA_SPINE_OUTPUT_DIR", cfg["output_dir"]))
    min_chars = cfg.get("min_chars", 400)

    ensure_dir(out_base)

    # Load the export (OpenAI style: a list of conversations)
    with export_path.open("r", encoding="utf-8-sig") as f:
        conversations = json.load(f)

    frag_counter = 0

    for conv in conversations:
        conv_id = conv.get("id") or conv.get("conversation_id") or "unknown"
        created = conv.get("create_time") or conv.get("created_at")
        if isinstance(created, (int, float)):
            dt = datetime.fromtimestamp(created)
        else:
            try:
                dt = datetime.fromisoformat(str(created))
            except Exception:
                dt = None

        conv_stamp = dt.strftime("%Y%m%d_%H%M%S") if dt else "no_date"

        messages = conv.get("messages") or conv.get("mapping", {}).values()

        for msg in messages:
            # adapt if your export structure differs
            role = msg.get("author", {}).get("role") or msg.get("role", "unknown")
            content_raw = msg.get("content")
            if isinstance(content_raw, dict) and "parts" in content_raw:
                content = "\n".join(content_raw["parts"])
            elif isinstance(content_raw, list):
                content = "\n".join(str(p) for p in content_raw)
            else:
                content = str(content_raw) if content_raw is not None else ""

            content = normalize(content)
            if len(content) < min_chars:
                continue

            topics = classify_topics(content, cfg["topics"])
            if not topics:
                continue

            frag_counter += 1

            header = f"""---
conversation_id: {conv_id}
timestamp: {conv_stamp}
role: {role}
topics: {", ".join(topics)}
---

"""

            md = header + content + "\n"

            for topic in topics:
                topic_dir = out_base / topic
                ensure_dir(topic_dir)
                fname = f"{topic}_{conv_stamp}_{frag_counter:05d}.md"
                with (topic_dir / fname).open("w", encoding="utf-8") as out:
                    out.write(md)

    print(f"Done. Wrote {frag_counter} fragments into '{out_base}'.")

if __name__ == "__main__":
    main()
