from html.parser import HTMLParser
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.assets = []
        self.meta_names = set()
        self.has_title = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.append(values["id"])
        if tag == "a" and values.get("href", "").startswith("#"):
            self.links.append(values["href"][1:])
        if tag in {"img", "script"} and values.get("src") and "://" not in values["src"]:
            self.assets.append(values["src"])
        if tag == "meta" and values.get("name"):
            self.meta_names.add(values["name"])
        if tag == "title":
            self.has_title = True


def main():
    parser = SiteParser()
    parser.feed(INDEX.read_text(encoding="utf-8"))
    errors = []
    duplicate_ids = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
    missing_targets = sorted({item for item in parser.links if item and item not in parser.ids})
    missing_assets = sorted({item for item in parser.assets if not (ROOT / item).exists()})
    if duplicate_ids:
        errors.append(f"Duplicate IDs: {', '.join(duplicate_ids)}")
    if missing_targets:
        errors.append(f"Missing navigation targets: {', '.join(missing_targets)}")
    if missing_assets:
        errors.append(f"Missing local assets: {', '.join(missing_assets)}")
    if not parser.has_title:
        errors.append("Missing page title")
    for name in {"description", "viewport"} - parser.meta_names:
        errors.append(f"Missing meta tag: {name}")
    if errors:
        print("\n".join(errors))
        return 1
    print("Site validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

