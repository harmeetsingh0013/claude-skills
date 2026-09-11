#!/usr/bin/env python3
"""
pipeline_tool.py — deterministic bookkeeping for the design pipeline.

This script owns everything that must be exact and repeatable: project
identity and storage location, hashing, version arithmetic, reading/
writing LATEST.json pointers, validating structured data documents
against their JSON Schema contracts, and deciding whether a document is
stale relative to its inputs. Claude is responsible for everything that
requires judgment (writing the documents themselves, detecting semantic
conflicts, deciding wording, and asking the user for a project name/ID) —
this script never generates or edits document content and never asks the
user anything itself.

=== Where projects live ===

Each project gets its own folder, named "<slugified-name>-<unique-id>"
(e.g. "url-shortener-curious-mango"). **Where that folder is created is
something the user is asked, not something this tool decides silently,
and there is no hardcoded absolute fallback** — see
references/pipeline-conventions.md for the exact question a skill asks
before minting a new project. Concretely, `resolve-project` (with no
--project, minting a new project) takes an optional --location <dir>: if
given, the project folder is created there. If the user has no
preference, it falls back to the current working directory — i.e.
wherever this script is actually being run from — not a system-wide
default like a home directory.

This means the "no location given" fallback is workspace-relative: a
project created with no --location from inside one working directory
(e.g. a repo) stays associated with that directory, the same way a `.git`
folder would. It's still NOT nested inside a plain "design-docs/"
subfolder and NOT inside the skills installation directory — it's a
sibling of wherever you're working, not buried inside it or scattered to
a fixed system path. Every stage's output for a project lives directly
under that one project folder:

    <chosen-or-cwd-location>/url-shortener-curious-mango/
      product-idea/
      mini-prd/
      functional-requirements/
      non-functional-requirements/
      architecture-design/
      mermaid-diagrams/

The registry itself (see below) resolves the same way — it lives under
whatever the current working directory is when a command runs (or under
an explicit --location, for resolve-project specifically), not a single
global system location. Practically: stay in the same working directory
for a given set of projects and `list-projects`/resuming by ID will find
them; a project created from a different working directory (with no
explicit --location either time) won't show up unless you're back in the
directory it was created from.

Since a project's full folder name includes a human-readable slug that a
skill doesn't know in advance, project identity is tracked through a small
registry file at <base>/.design-pipeline/projects.json, mapping each
project's unique ID (the part a user actually types, e.g. "curious-mango")
to its folder name and full path. A project ID is never guessed or
invented by a skill — every command except `resolve-project` and
`list-projects` requires `--project <id>`, and refuses to run if that ID
isn't in the registry. See references/pipeline-conventions.md for the
exact interaction pattern every skill follows, including asking the user
for a short project name when starting a brand-new project.

=== The contract: every document is TWO files, not one ===

Each pipeline stage produces:
  - vX.Y.md         a human-readable document following that stage's
                     templates/<doc-type>.md structure
  - vX.Y.data.json   a machine-readable structured summary of the same
                     content, validated against schema/<doc-type>.schema.json

The .md is for humans (and for a downstream skill's own reading/reasoning).
The .data.json is the actual contract between stages: downstream skills
should read structured fields (requirement IDs, statuses, targets) from it
rather than parsing prose, and this script validates it before letting the
pipeline treat a version as usable input. mermaid-diagrams is the one
exception where "document_path" is a directory of .mmd files rather than a
single .md — see hash_path().

Directory layout this script maintains (within one project's folder):

    <project-root>/
      product-idea/
        current.md
        LATEST.json           <- {"version", "hash", "doc_path"}
      mini-prd/
        v1.0.md
        v1.0.data.json
        v1.0.envelope.json
        LATEST.json           <- {"version","status","doc_path","data_path","envelope_path","hash"}
      functional-requirements/  (same shape)
      non-functional-requirements/  (same shape)
      architecture-design/          (same shape)
      mermaid-diagrams/
        v1.0/                  <- directory: 01-system-context.mmd, ...
        v1.0.data.json
        v1.0.envelope.json
        LATEST.json            <- doc_path points at the v1.0/ directory

Envelope schema (written by the skill, validated by `finalize`):
{
  "envelope_version": "1.0",
  "skill": "<skill-name>",
  "document_type": "<doc-type, matches folder name>",
  "status": "READY" | "ERROR" | "BLOCKED_QUESTION" | "CONFLICT",
  "version": "1.0",
  "generated_at": "<ISO-8601, filled in by finalize if missing>",
  "document_path": "<project-root>/<doc-type>/v<version>.md-or-directory",
  "data_path": "<project-root>/<doc-type>/v<version>.data.json",   (optional but expected)
  "inputs_consumed": {
      "<upstream-doc-type-or-product-idea>": {"version": "1.0", "hash": "sha256:..."}
      ...
  },
  "next_skill": "<doc-type of the next stage, or null>",
  "summary": "one paragraph, human-readable",
  "errors": [ {"code": "...", "message": "..."} ],
  "blocking_questions": [ "..." ]
}

`status` here is the generic pipeline-control status the orchestrator acts
on. It's set FROM the document's own domain-specific completeness
assessment (e.g. a functional-requirements document says
"READY_FOR_NFR" or "BLOCKED" inside the .md/.data.json) — map that to
READY / BLOCKED_QUESTION / CONFLICT / ERROR here. See
references/pipeline-conventions.md for the mapping table.

Pipeline DAG (doc_type -> required input doc_types, next doc_type):
"""

import argparse
import hashlib
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schema"

# Set by main() once --project has been validated against the registry;
# every doc_dir()/read_latest() call below operates relative to this.
# Deliberately a module global rather than threaded through every
# function — this script is always a single, short-lived CLI invocation,
# so that's a reasonable simplification, not a footgun for concurrent use.
ROOT = None

PIPELINE = {
    "mini-prd": {
        "inputs": ["product-idea"],
        "next": "functional-requirements",
        "skill": "mini-prd",
    },
    "functional-requirements": {
        "inputs": ["mini-prd"],
        "next": "non-functional-requirements",
        "skill": "functional-requirements",
    },
    "non-functional-requirements": {
        "inputs": ["functional-requirements"],
        "next": "architecture-design",
        "skill": "non-functional-requirements",
    },
    "architecture-design": {
        "inputs": ["functional-requirements", "non-functional-requirements"],
        "next": "mermaid-diagrams",
        "skill": "architecture-design",
    },
    "mermaid-diagrams": {
        "inputs": ["architecture-design"],
        "next": "project-readme",
        "skill": "mermaid-js",
    },
    "project-readme": {
        "inputs": ["mermaid-diagrams"],
        "next": None,
        "skill": "project-readme",
    },
}

REQUIRED_ENVELOPE_FIELDS = [
    "envelope_version", "skill", "document_type", "status", "version",
    "document_path", "inputs_consumed", "next_skill", "summary",
]

VALID_STATUSES = {"READY", "ERROR", "BLOCKED_QUESTION", "CONFLICT"}

# Word lists for project unique IDs. Kept modest and G-rated; ~50 x ~50 =
# 2500 combinations before a collision retry is ever needed.
ADJECTIVES = [
    "curious", "brave", "quiet", "cheerful", "bold", "gentle", "swift",
    "clever", "calm", "eager", "jolly", "kind", "lively", "mellow",
    "nimble", "proud", "sunny", "tidy", "vivid", "witty", "zesty",
    "amber", "cosmic", "dapper", "earnest", "frosty", "golden", "hardy",
    "icy", "jazzy", "keen", "lucky", "misty", "noble", "orange",
    "plucky", "quirky", "radiant", "spry", "trusty", "upbeat", "velvet",
    "wandering", "young", "zealous", "breezy", "crisp", "dreamy",
    "electric", "fearless",
]
FOODS = [
    "mango", "avocado", "pretzel", "walnut", "papaya", "biscuit",
    "noodle", "waffle", "lentil", "cherry", "ginger", "pumpkin",
    "coconut", "olive", "pepper", "radish", "turnip", "apricot",
    "fennel", "kiwi", "lychee", "mustard", "nectarine", "oregano",
    "parsnip", "quince", "raisin", "saffron", "tomato", "ube",
    "vanilla", "wasabi", "yam", "zucchini", "artichoke", "basil",
    "cardamom", "dumpling", "eggplant", "falafel", "guava", "honeydew",
    "iceberg", "jalapeno", "kumquat", "lemongrass", "muffin", "nutmeg",
    "onion", "pistachio",
]


# ---------------------------------------------------------- storage root --

def base_dir(location_override: str = None) -> Path:
    """
    Where a new project's folder is created. There is no hardcoded
    absolute fallback (no home directory, no C:\\ drive, no environment
    variable) — this always resolves to one of exactly two things:

      1. location_override: the path the user was explicitly asked for
         and gave (via --location on resolve-project).
      2. If the user had no preference: the current working directory —
         wherever this script is actually being run from. That's a
         workspace-relative choice, not a hardcoded system path, so a
         project created from one working directory naturally stays
         associated with that workspace.

    This is also where the project registry lives (see registry_path())
    when no location_override is given — the registry is workspace-local,
    matching the project-folder fallback, not a single global system
    location.
    """
    if location_override:
        return Path(location_override).expanduser()
    return Path.cwd()


def registry_path() -> Path:
    return base_dir() / ".design-pipeline" / "projects.json"


def read_registry() -> dict:
    p = registry_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def write_registry(data: dict):
    p = registry_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n")


def slugify(name: str) -> str:
    if not name:
        return "project"
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    slug = slug[:40].strip("-")
    return slug or "project"


# ---------------------------------------------------------------- hashing --

def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def hash_path(path: Path) -> str:
    """
    Hash a document that may be a single file or a directory of files
    (mermaid-diagrams' multiple .mmd outputs). For a directory, hash a
    manifest of sorted "relative/path:sha256" lines rather than trying to
    concatenate raw bytes — this keeps the result stable regardless of file
    order and makes it easy to tell which specific file changed if a
    mismatch is ever debugged by hand.
    """
    path = Path(path)
    if path.is_dir():
        entries = []
        for f in sorted(path.rglob("*")):
            if f.is_file():
                entries.append(f"{f.relative_to(path).as_posix()}:{sha256_file(f)}")
        return sha256_text("\n".join(entries))
    return sha256_file(path)


# ------------------------------------------------------ minimal JSON Schema --
# A dependency-free subset of JSON Schema: type, required, properties,
# items, enum, pattern, minItems, minLength, minimum, maximum. This is
# intentionally not a full implementation — it covers what the pipeline's
# own schemas use. Don't reach for this to validate arbitrary third-party
# schemas.

def _type_ok(value, expected):
    mapping = {
        "object": dict, "array": list, "string": str,
        "boolean": bool, "number": (int, float), "integer": int,
    }
    py_type = mapping.get(expected)
    if py_type is None:
        return True
    if expected == "integer" and isinstance(value, bool):
        return False
    return isinstance(value, py_type)


def validate_against_schema(data, schema, path="$"):
    """Returns a list of human-readable error strings (empty = valid)."""
    errors = []

    if "type" in schema and not _type_ok(data, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}, got {type(data).__name__}")
        return errors  # further checks would be noise if the base type is wrong

    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: {data!r} not in allowed values {schema['enum']}")

    if schema.get("type") == "string":
        if "pattern" in schema and not re.match(schema["pattern"], data or ""):
            errors.append(f"{path}: {data!r} does not match pattern {schema['pattern']!r}")
        if "minLength" in schema and len(data or "") < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength {schema['minLength']}")

    if schema.get("type") in ("integer", "number"):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: {data!r} is less than minimum {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: {data!r} exceeds maximum {schema['maximum']}")

    if schema.get("type") == "object":
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if not isinstance(data, dict) or req not in data:
                errors.append(f"{path}: missing required field {req!r}")
        if isinstance(data, dict):
            for key, subschema in props.items():
                if key in data:
                    errors.extend(validate_against_schema(data[key], subschema, f"{path}.{key}"))

    if schema.get("type") == "array":
        if "minItems" in schema and isinstance(data, list) and len(data) < schema["minItems"]:
            errors.append(f"{path}: array shorter than minItems {schema['minItems']}")
        if "items" in schema and isinstance(data, list):
            for i, item in enumerate(data):
                errors.extend(validate_against_schema(item, schema["items"], f"{path}[{i}]"))

    return errors


# Sprint documents use dynamically-numbered doc types ("sprints/sprint-01",
# "sprints/sprint-02", ...) rather than one fixed name — there's no bound
# on how many sprints a project ends up with. They all share one schema
# (schema/sprint.schema.json) regardless of number.
SPRINT_DOC_PATTERN = re.compile(r"^sprints/sprint-(\d+)$")


def is_known_doc_type(doc_type: str) -> bool:
    return (doc_type in PIPELINE
            or doc_type == "product-idea"
            or bool(SPRINT_DOC_PATTERN.match(doc_type)))


def schema_name_for(doc_type: str) -> str:
    if SPRINT_DOC_PATTERN.match(doc_type):
        return "sprint"
    return doc_type


def load_schema(doc_type: str):
    schema_path = SCHEMA_DIR / f"{schema_name_for(doc_type)}.schema.json"
    if not schema_path.exists():
        return None, schema_path
    return json.loads(schema_path.read_text()), schema_path


# ------------------------------------------------------------- state I/O --

def doc_dir(doc_type: str) -> Path:
    d = ROOT / doc_type
    d.mkdir(parents=True, exist_ok=True)
    return d


def read_latest(doc_type: str):
    p = doc_dir(doc_type) / "LATEST.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def write_latest(doc_type: str, data: dict):
    p = doc_dir(doc_type) / "LATEST.json"
    p.write_text(json.dumps(data, indent=2) + "\n")


def next_version(previous_version):
    if not previous_version:
        return "1.0"
    v = round(float(previous_version) + 0.1, 1)
    return f"{v:.1f}"


# --------------------------------------------------------------- backlog --
# A lightweight, persistent list of candidate items for a doc-type that
# didn't make it into the current MVP round (or that the user added
# directly). This is separate from a document's own `deferred` array
# (which is just a snapshot at the time that version was written) —
# backlog.json is the living state a skill reads from FIRST when picking
# the next MVP's batch, and the user can add to it anytime without
# triggering a full document regeneration. Not schema-validated like a
# document's data.json — this is tool-managed state, the same category as
# LATEST.json.

def backlog_path(doc_type: str) -> Path:
    return doc_dir(doc_type) / "backlog.json"


def read_backlog(doc_type: str) -> list:
    p = backlog_path(doc_type)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def write_backlog(doc_type: str, items: list):
    backlog_path(doc_type).write_text(json.dumps(items, indent=2) + "\n")


def cmd_backlog_add(args):
    items = read_backlog(args.doc_type)
    existing_nums = [int(i["id"].split("-")[-1]) for i in items if i["id"].startswith("BL-")]
    next_num = max(existing_nums, default=0) + 1
    item = {
        "id": f"BL-{next_num}",
        "text": args.text,
        "source": args.source,
        "status": "pending",
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(item)
    write_backlog(args.doc_type, items)
    print("ADDED")
    print(json.dumps(item, indent=2))


def cmd_backlog_list(args):
    items = read_backlog(args.doc_type)
    if not args.all:
        items = [i for i in items if i["status"] == "pending"]
    print(json.dumps(items, indent=2))


def cmd_backlog_resolve(args):
    items = read_backlog(args.doc_type)
    for item in items:
        if item["id"] == args.id:
            item["status"] = args.status
            if args.resulting_id:
                item["resulting_id"] = args.resulting_id
            write_backlog(args.doc_type, items)
            print("RESOLVED")
            print(json.dumps(item, indent=2))
            return
    print(f"ERROR: backlog item {args.id!r} not found for '{args.doc_type}'")
    sys.exit(1)


# ------------------------------------------------------------- projects --

def cmd_resolve_project(args):
    """
    With --project: confirm that project exists (EXISTING) or report
    PROJECT_NOT_FOUND (exit 1) — never silently creates a project for an
    ID the caller supplied, since IDs are minted by this tool, not chosen
    by users.
    With --path (and no --project): adopt an existing folder of design
    documents that isn't in the registry yet — e.g. copied from another
    machine, or the registry was lost/rebuilt. If that exact path is
    already registered, behaves like EXISTING. Otherwise, tries to infer a
    project ID from the folder name (a "<slug>-<adjective>-<food>" folder
    yields the trailing "<adjective>-<food>" as its ID); if that can't be
    inferred or is already taken, mints a fresh ID for it instead — either
    way, registers the path and reports ADOPTED so the caller can tell the
    user which ID to use going forward.
    With neither: mint a new unique ID, create "<slug>-<id>" under the
    resolved base location, register it, and report NEW. This is the
    only way a brand-new project comes into being. --name supplies the
    human-readable slug (e.g. "url-shortener"); omit it and the folder is
    just named "project-<id>". --location supplies WHERE to create it —
    the calling skill must have asked the user for this (see
    references/pipeline-conventions.md); if omitted, falls back to the
    current working directory — there is no hardcoded absolute default.
    """
    registry = read_registry()

    if args.project:
        entry = registry.get(args.project)
        if entry:
            print("EXISTING")
            print(json.dumps({"project_id": args.project, "status": "EXISTING",
                               "path": entry["path"], "folder": entry["folder"]},
                              indent=2))
        else:
            print(f"PROJECT_NOT_FOUND: no project '{args.project}' exists yet.")
            sys.exit(1)
        return

    if args.path:
        path = Path(args.path).expanduser().resolve()
        if not path.is_dir():
            print(f"PATH_NOT_FOUND: {path} does not exist or is not a directory.")
            sys.exit(1)

        for pid, entry in registry.items():
            if Path(entry["path"]).resolve() == path:
                print("EXISTING")
                print(json.dumps({"project_id": pid, "status": "EXISTING",
                                   "path": str(path), "folder": entry["folder"]},
                                  indent=2))
                return

        known_doc_types = list(PIPELINE.keys()) + ["product-idea"]
        looks_like_project = any((path / dt).is_dir() for dt in known_doc_types)

        folder_name = path.name
        parts = folder_name.split("-")
        inferred_id = None
        slug = folder_name
        if len(parts) >= 3:
            candidate_id = "-".join(parts[-2:])
            if candidate_id not in registry:
                inferred_id = candidate_id
                slug = "-".join(parts[:-2]) or "project"

        if inferred_id:
            new_id = inferred_id
        else:
            existing_ids = set(registry.keys())
            new_id = None
            for _ in range(200):
                attempt = f"{random.choice(ADJECTIVES)}-{random.choice(FOODS)}"
                if attempt not in existing_ids:
                    new_id = attempt
                    break
            if new_id is None:
                new_id = f"{random.choice(ADJECTIVES)}-{random.choice(FOODS)}-{random.randint(2, 999)}"
            slug = slugify(folder_name)

        registry[new_id] = {
            "name": None,
            "slug": slug,
            "folder": folder_name,
            "path": str(path),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "adopted_from_path": True,
        }
        write_registry(registry)

        status = "ADOPTED" if looks_like_project else "ADOPTED_EMPTY"
        print(status)
        print(json.dumps({
            "project_id": new_id, "status": status, "path": str(path),
            "folder": folder_name, "id_inferred_from_folder_name": inferred_id is not None,
        }, indent=2))
        return

    existing_ids = set(registry.keys())
    candidate = None
    for _ in range(200):
        attempt = f"{random.choice(ADJECTIVES)}-{random.choice(FOODS)}"
        if attempt not in existing_ids:
            candidate = attempt
            break
    if candidate is None:
        candidate = f"{random.choice(ADJECTIVES)}-{random.choice(FOODS)}-{random.randint(2, 999)}"

    slug = slugify(args.name)
    folder_name = f"{slug}-{candidate}"
    base = base_dir(args.location)
    root = base / folder_name
    root.mkdir(parents=True, exist_ok=True)

    registry[candidate] = {
        "name": args.name or None,
        "slug": slug,
        "folder": folder_name,
        "path": str(root),
        "location_source": "user-specified" if args.location else "default",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    write_registry(registry)

    print("NEW")
    print(json.dumps({"project_id": candidate, "status": "NEW",
                       "path": str(root), "folder": folder_name,
                       "location_source": registry[candidate]["location_source"]},
                      indent=2))


def cmd_list_projects(args):
    registry = read_registry()
    result = [
        {"project_id": pid, "name": entry.get("name"), "path": entry["path"]}
        for pid, entry in sorted(registry.items())
    ]
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------- commands --

def cmd_init(args):
    ROOT.mkdir(parents=True, exist_ok=True)
    for doc_type in list(PIPELINE.keys()) + ["product-idea"]:
        doc_dir(doc_type)
    print(f"Initialized {ROOT}/ with folders: product-idea, "
          + ", ".join(PIPELINE.keys()))


def cmd_set_idea(args):
    text = Path(args.file).read_text() if args.file else sys.stdin.read()
    d = doc_dir("product-idea")
    current_latest = read_latest("product-idea")
    new_hash = sha256_text(text)
    if current_latest and current_latest.get("hash") == new_hash:
        print("UNCHANGED")
        print(json.dumps(current_latest, indent=2))
        return
    version = next_version(current_latest["version"] if current_latest else None)
    (d / "current.md").write_text(text)
    latest = {"version": version, "hash": new_hash, "doc_path": str(d / "current.md")}
    write_latest("product-idea", latest)
    print("UPDATED")
    print(json.dumps(latest, indent=2))


def cmd_latest(args):
    latest = read_latest(args.doc_type)
    print(json.dumps(latest, indent=2) if latest else "NONE")


def cmd_check_ready(args):
    """Exit 0 and print LATEST.json if the doc_type is READY; exit 1 otherwise."""
    latest = read_latest(args.doc_type)
    if latest is None:
        print(f"NOT_READY: no version of '{args.doc_type}' has been produced yet.")
        sys.exit(1)
    if latest.get("status") != "READY":
        print(f"NOT_READY: latest '{args.doc_type}' (v{latest.get('version')}) "
              f"has status {latest.get('status')!r}, not READY.")
        sys.exit(1)
    print(json.dumps(latest, indent=2))


def cmd_next_version(args):
    latest = read_latest(args.doc_type)
    prev_version = latest["version"] if latest else None
    result = {
        "next_version": next_version(prev_version),
        "previous_version": prev_version,
        "previous_doc_path": latest.get("doc_path") if latest else None,
        "previous_data_path": latest.get("data_path") if latest else None,
        "previous_envelope_path": latest.get("envelope_path") if latest else None,
    }
    print(json.dumps(result, indent=2))


def cmd_hash_file(args):
    print(hash_path(Path(args.path)))


def cmd_hash_text(args):
    print(sha256_text(sys.stdin.read()))


def cmd_validate_data(args):
    """
    Validate a structured data.json against a doc-type's JSON Schema
    contract (schema/<doc_type>.schema.json, a sibling of this script's
    parent directory). If --path is omitted, validates the CURRENT LATEST
    data.json for that doc_type instead of a file you're about to write —
    useful for confirming an upstream document's contract before trusting
    it, separately from the check-ready status gate.
    """
    schema, schema_path = load_schema(args.doc_type)
    if schema is None:
        print(f"NO_SCHEMA: {schema_path} not found — skipping structural validation.")
        return

    if args.path:
        data_path = Path(args.path)
    else:
        latest = read_latest(args.doc_type)
        if not latest or not latest.get("data_path"):
            print(f"FAIL: no data.json available for '{args.doc_type}' yet.")
            sys.exit(1)
        data_path = Path(latest["data_path"])

    if not data_path.exists():
        print(f"FAIL: data file not found: {data_path}")
        sys.exit(1)

    data = json.loads(data_path.read_text())
    errors = validate_against_schema(data, schema)
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("PASS")


def cmd_needs_rerun(args):
    """
    Compare the hashes of doc_type's required inputs (their CURRENT LATEST)
    against the hashes recorded in doc_type's own current envelope's
    inputs_consumed. Prints RERUN_NEEDED or UP_TO_DATE plus reasons.
    Also flags GATE_BLOCKED if a required input isn't READY.
    """
    doc_type = args.doc_type
    spec = PIPELINE.get(doc_type)
    if spec is None:
        print(f"UNKNOWN_DOC_TYPE: {doc_type}")
        sys.exit(2)

    reasons = []
    blocked = []
    for input_type in spec["inputs"]:
        input_latest = read_latest(input_type)
        if input_latest is None:
            blocked.append(f"{input_type} has never been produced")
            continue
        if input_type != "product-idea" and input_latest.get("status") != "READY":
            blocked.append(f"{input_type} v{input_latest.get('version')} status is "
                            f"{input_latest.get('status')!r}, not READY")

    if blocked:
        print("GATE_BLOCKED")
        for b in blocked:
            print(f"  - {b}")
        sys.exit(1)

    own_latest = read_latest(doc_type)
    if own_latest is None:
        print("RERUN_NEEDED")
        print("  - no version exists yet")
        return

    own_envelope_path = own_latest.get("envelope_path")
    inputs_consumed = {}
    if own_envelope_path and Path(own_envelope_path).exists():
        inputs_consumed = json.loads(Path(own_envelope_path).read_text()).get(
            "inputs_consumed", {})

    stale = False
    for input_type in spec["inputs"]:
        input_latest = read_latest(input_type)
        recorded = inputs_consumed.get(input_type, {})
        if recorded.get("hash") != input_latest.get("hash"):
            stale = True
            reasons.append(
                f"{input_type} changed (was v{recorded.get('version', '?')}, "
                f"now v{input_latest.get('version', '?')})"
            )

    if own_latest.get("status") != "READY":
        stale = True
        reasons.append(f"current version has status {own_latest.get('status')!r}")

    print("RERUN_NEEDED" if stale else "UP_TO_DATE")
    for r in reasons:
        print(f"  - {r}")


def cmd_plan(args):
    """Walk the DAG in order and report which doc_types need a rerun, cascading."""
    order = ["mini-prd", "functional-requirements", "non-functional-requirements",
             "architecture-design", "mermaid-diagrams", "project-readme"]
    plan = []
    for doc_type in order:
        spec = PIPELINE[doc_type]
        blocked = []
        for input_type in spec["inputs"]:
            input_latest = read_latest(input_type)
            if input_latest is None:
                blocked.append(input_type)
            elif input_type != "product-idea" and input_latest.get("status") != "READY":
                blocked.append(f"{input_type}(status={input_latest.get('status')})")
        if blocked:
            plan.append({"doc_type": doc_type, "action": "BLOCKED", "waiting_on": blocked})
            continue

        own_latest = read_latest(doc_type)
        if own_latest is None:
            plan.append({"doc_type": doc_type, "action": "RUN", "reason": "no version yet"})
            continue

        inputs_consumed = {}
        envelope_path = own_latest.get("envelope_path")
        if envelope_path and Path(envelope_path).exists():
            inputs_consumed = json.loads(Path(envelope_path).read_text()).get(
                "inputs_consumed", {})

        stale = own_latest.get("status") != "READY"
        for input_type in spec["inputs"]:
            input_latest = read_latest(input_type)
            recorded = inputs_consumed.get(input_type, {})
            if recorded.get("hash") != input_latest.get("hash"):
                stale = True
        plan.append({"doc_type": doc_type,
                     "action": "RUN" if stale else "SKIP",
                     "current_version": own_latest.get("version")})
    print(json.dumps(plan, indent=2))


def cmd_finalize(args):
    """
    Validate an envelope JSON file (and, if it declares a data_path, the
    structured data contract behind it), then atomically update
    LATEST.json for doc_type to point at it. Only call this after the
    document (.md, and its .data.json if this doc_type has one) have
    already been written to their versioned paths.
    """
    envelope_path = Path(args.envelope_path)
    if not envelope_path.exists():
        print(f"ERROR: envelope file not found: {envelope_path}")
        sys.exit(1)
    envelope = json.loads(envelope_path.read_text())

    missing = [f for f in REQUIRED_ENVELOPE_FIELDS if f not in envelope]
    if missing:
        print(f"ERROR: envelope missing required fields: {missing}")
        sys.exit(1)
    if envelope["status"] not in VALID_STATUSES:
        print(f"ERROR: invalid status {envelope['status']!r}, must be one of {VALID_STATUSES}")
        sys.exit(1)
    doc_type = envelope["document_type"]
    if not is_known_doc_type(doc_type):
        print(f"ERROR: unknown document_type {doc_type!r}")
        sys.exit(1)

    doc_path = Path(envelope["document_path"])
    if envelope["status"] == "READY" and not doc_path.exists():
        print(f"ERROR: status is READY but document_path does not exist: {doc_path}")
        sys.exit(1)

    data_path = envelope.get("data_path")
    if data_path:
        schema, schema_path = load_schema(doc_type)
        if schema is not None:
            if not Path(data_path).exists():
                print(f"ERROR: data_path declared but not found: {data_path}")
                sys.exit(1)
            data = json.loads(Path(data_path).read_text())
            errors = validate_against_schema(data, schema)
            if errors:
                print(f"ERROR: {data_path} does not satisfy {schema_path}:")
                for e in errors:
                    print(f"  - {e}")
                sys.exit(1)

    if "generated_at" not in envelope or not envelope["generated_at"]:
        envelope["generated_at"] = datetime.now(timezone.utc).isoformat()
        envelope_path.write_text(json.dumps(envelope, indent=2) + "\n")

    doc_hash = hash_path(doc_path) if doc_path.exists() else None
    latest = {
        "version": envelope["version"],
        "status": envelope["status"],
        "doc_path": str(doc_path) if doc_path.exists() else None,
        "data_path": data_path,
        "envelope_path": str(envelope_path),
        "hash": doc_hash,
    }
    write_latest(doc_type, latest)
    print("FINALIZED")
    print(json.dumps(latest, indent=2))


# ------------------------------------------------------------ sprints --
# Sprints are fundamentally different from the other stages: each one is
# a new, non-overlapping unit of up to 10 tasks (not a growing/cumulative
# document), created on request rather than as part of the automatic
# plan/cascade. A sprint's own doc_type ("sprints/sprint-01", etc.) still
# uses the same v1.0/v1.1 revision mechanism as everything else (for
# fixing a sprint's content before any of its tasks are marked done) —
# what's different is how the NEXT sprint's number is chosen, and that
# each task within a sprint has its own separate, mutable lifecycle
# status (NOT_READY/READY/IN_PROGRESS/DONE) tracked outside the versioned
# document entirely, since task progress changes far more often than the
# plan itself and isn't a "revision" of it.

def sprints_dir() -> Path:
    d = ROOT / "sprints"
    d.mkdir(parents=True, exist_ok=True)
    return d


def status_path_for(sprint_doc_type: str) -> Path:
    return ROOT / sprint_doc_type / "status.json"


def read_task_statuses(sprint_doc_type: str) -> dict:
    p = status_path_for(sprint_doc_type)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def write_task_statuses(sprint_doc_type: str, statuses: dict):
    p = status_path_for(sprint_doc_type)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(statuses, indent=2) + "\n")


def find_task_status(task_id: str):
    """Search every known sprint's status.json for this task ID."""
    d = sprints_dir()
    for sub in sorted(d.iterdir()):
        if SPRINT_DOC_PATTERN.match(f"sprints/{sub.name}"):
            statuses = read_task_statuses(f"sprints/{sub.name}")
            if task_id in statuses:
                return statuses[task_id]
    return None


def cmd_next_sprint(args):
    """
    Find the next sprint number: the highest existing finalized sprint's
    number, plus one (or 1 if there are none yet). Also reports the
    previous sprint's doc/data paths (for reading as context — task
    numbering continues from it) and, if tracked, which of its tasks
    aren't yet DONE — a signal (not a hard block) that starting the next
    sprint might be premature.
    """
    d = sprints_dir()
    existing = []
    for sub in d.iterdir():
        if sub.is_dir():
            m = re.match(r"^sprint-(\d+)$", sub.name)
            if m and (sub / "LATEST.json").exists():
                existing.append(int(m.group(1)))

    next_num = max(existing, default=0) + 1
    result = {
        "next_sprint_number": next_num,
        "next_doc_type": f"sprints/sprint-{next_num:02d}",
        "previous_sprint_number": None,
        "previous_doc_type": None,
        "previous_doc_path": None,
        "previous_data_path": None,
        "previous_sprint_tasks_not_done": None,
    }
    if existing:
        prev_num = max(existing)
        prev_doc_type = f"sprints/sprint-{prev_num:02d}"
        prev_latest = read_latest(prev_doc_type)
        result["previous_sprint_number"] = prev_num
        result["previous_doc_type"] = prev_doc_type
        if prev_latest:
            result["previous_doc_path"] = prev_latest.get("doc_path")
            result["previous_data_path"] = prev_latest.get("data_path")
        statuses = read_task_statuses(prev_doc_type)
        not_done = [tid for tid, st in statuses.items() if st != "DONE"]
        result["previous_sprint_tasks_not_done"] = not_done if statuses else None

    print(json.dumps(result, indent=2))


def cmd_task_status_init(args):
    """
    Seed a freshly-finalized sprint's status.json from its data.json:
    a task with no prerequisites starts READY; a task with prerequisites
    starts READY only if every prerequisite is already DONE (checked
    across ALL sprints, not just this one), otherwise NOT_READY.
    """
    data = json.loads(Path(args.path).read_text())
    statuses = {}
    for task in data.get("tasks", []):
        tid = task["id"]
        prereqs = task.get("prerequisites", [])
        if not prereqs:
            statuses[tid] = "READY"
        else:
            all_done = all(find_task_status(p) == "DONE" for p in prereqs)
            statuses[tid] = "READY" if all_done else "NOT_READY"
    write_task_statuses(args.doc_type, statuses)
    print("INITIALIZED")
    print(json.dumps(statuses, indent=2))


def cmd_task_status_set(args):
    valid = {"NOT_READY", "READY", "IN_PROGRESS", "DONE"}
    if args.status not in valid:
        print(f"ERROR: status must be one of {valid}")
        sys.exit(1)
    statuses = read_task_statuses(args.doc_type)
    if args.id not in statuses:
        print(f"ERROR: task {args.id!r} not found in {args.doc_type}'s status "
              f"tracking — run task-status-init first, or check the ID.")
        sys.exit(1)
    statuses[args.id] = args.status
    write_task_statuses(args.doc_type, statuses)
    print("UPDATED")
    print(json.dumps({args.id: args.status}, indent=2))

    # Marking a task DONE may make tasks that depend on it newly READY —
    # re-derive downstream statuses across all sprints rather than leaving
    # them stale until someone happens to re-run task-status-init.
    if args.status == "DONE":
        d = sprints_dir()
        for sub in sorted(d.iterdir()):
            if not sub.is_dir():
                continue
            doc_type = f"sprints/{sub.name}"
            if not SPRINT_DOC_PATTERN.match(doc_type):
                continue
            latest = read_latest(doc_type)
            if not latest or not latest.get("data_path"):
                continue
            data_path = Path(latest["data_path"])
            if not data_path.exists():
                continue
            data = json.loads(data_path.read_text())
            sub_statuses = read_task_statuses(doc_type)
            changed = False
            for task in data.get("tasks", []):
                tid = task["id"]
                if sub_statuses.get(tid) == "NOT_READY":
                    prereqs = task.get("prerequisites", [])
                    if prereqs and all(find_task_status(p) == "DONE" for p in prereqs):
                        sub_statuses[tid] = "READY"
                        changed = True
            if changed:
                write_task_statuses(doc_type, sub_statuses)
                print(f"CASCADED: {doc_type} has newly-READY tasks")


def cmd_task_status_list(args):
    print(json.dumps(read_task_statuses(args.doc_type), indent=2))


def cmd_list_doc_types(args):
    """
    Enumerate every document type that actually exists for this project
    (has a LATEST.json), with its current version/status — including any
    sprints, which don't have a fixed doc-type name. Useful for anything
    that needs to build a complete picture of what's been produced without
    hardcoding the pipeline's doc-type list (e.g. project-readme).
    """
    result = []
    if ROOT.exists():
        for sub in sorted(ROOT.iterdir()):
            if not sub.is_dir() or sub.name.startswith("."):
                continue
            latest_path = sub / "LATEST.json"
            if latest_path.exists():
                latest = json.loads(latest_path.read_text())
                result.append({"doc_type": sub.name, **latest})
            elif sub.name == "sprints":
                for sprint_dir in sorted(sub.iterdir()):
                    sprint_latest = sprint_dir / "LATEST.json"
                    if sprint_dir.is_dir() and sprint_latest.exists():
                        latest = json.loads(sprint_latest.read_text())
                        result.append({"doc_type": f"sprints/{sprint_dir.name}", **latest})
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",
                         help="Project ID (e.g. curious-mango). Required for "
                              "every command except resolve-project and "
                              "list-projects. Must come BEFORE the subcommand.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("resolve-project",
                        help="No args: mint a new project (optionally "
                             "--name <short name> and --location <dir>). "
                             "--project <id>: confirm it exists. --path "
                             "<path>: adopt an existing design-docs folder "
                             "not yet in the registry.")
    p.add_argument("--name", help="Short human-readable project name, used "
                                   "to build the project folder's slug "
                                   "(e.g. 'url-shortener'). Only used when "
                                   "minting a brand-new project.")
    p.add_argument("--location", help="Directory to create the new "
                                       "project's folder under — the "
                                       "calling skill should have asked "
                                       "the user for this. Only used when "
                                       "minting a brand-new project; "
                                       "falls back to the current working "
                                       "directory if omitted (no hardcoded "
                                       "absolute default).")
    p.add_argument("--path", help="Path to an existing project folder to "
                                   "adopt (e.g. copied from another machine, "
                                   "or the registry was lost). Ignored if "
                                   "--project is also given.")
    p.set_defaults(func=cmd_resolve_project)

    sub.add_parser("list-projects").set_defaults(func=cmd_list_projects)

    sub.add_parser("init").set_defaults(func=cmd_init)

    p = sub.add_parser("set-idea", help="Record/update the product idea text")
    p.add_argument("--file", help="Path to a file with the idea text; omit to read stdin")
    p.set_defaults(func=cmd_set_idea)

    p = sub.add_parser("latest")
    p.add_argument("doc_type")
    p.set_defaults(func=cmd_latest)

    p = sub.add_parser("check-ready")
    p.add_argument("doc_type")
    p.set_defaults(func=cmd_check_ready)

    p = sub.add_parser("next-version")
    p.add_argument("doc_type")
    p.set_defaults(func=cmd_next_version)

    p = sub.add_parser("hash-file", help="Hashes a file, or a directory (e.g. mermaid-diagrams output)")
    p.add_argument("path")
    p.set_defaults(func=cmd_hash_file)

    p = sub.add_parser("hash-text", help="Reads text from stdin")
    p.set_defaults(func=cmd_hash_text)

    p = sub.add_parser("validate-data",
                        help="Validate a data.json against schema/<doc_type>.schema.json")
    p.add_argument("doc_type")
    p.add_argument("--path", help="Path to the data.json; defaults to the current LATEST")
    p.set_defaults(func=cmd_validate_data)

    p = sub.add_parser("needs-rerun")
    p.add_argument("doc_type")
    p.set_defaults(func=cmd_needs_rerun)

    sub.add_parser("plan").set_defaults(func=cmd_plan)

    p = sub.add_parser("backlog-add",
                        help="Add a candidate item to a doc-type's backlog "
                             "(deferred-by-skill or user-added)")
    p.add_argument("doc_type")
    p.add_argument("--text", required=True, help="Short description of the candidate item")
    p.add_argument("--source", choices=["skill", "user"], default="skill")
    p.set_defaults(func=cmd_backlog_add)

    p = sub.add_parser("backlog-list", help="List backlog items for a doc-type")
    p.add_argument("doc_type")
    p.add_argument("--all", action="store_true",
                    help="Include resolved (included/dropped) items, not just pending")
    p.set_defaults(func=cmd_backlog_list)

    p = sub.add_parser("backlog-resolve",
                        help="Mark a backlog item included or dropped")
    p.add_argument("doc_type")
    p.add_argument("--id", required=True, help="Backlog item ID, e.g. BL-3")
    p.add_argument("--status", required=True, choices=["included", "dropped"])
    p.add_argument("--resulting-id", help="The FR-N/NFR-N this became, if included")
    p.set_defaults(func=cmd_backlog_resolve)

    p = sub.add_parser("finalize")
    p.add_argument("envelope_path")
    p.set_defaults(func=cmd_finalize)

    sub.add_parser("next-sprint",
                    help="Find the next sprint number and previous sprint's "
                         "context").set_defaults(func=cmd_next_sprint)

    p = sub.add_parser("task-status-init",
                        help="Seed a sprint's task statuses from its data.json")
    p.add_argument("doc_type", help="e.g. sprints/sprint-01")
    p.add_argument("--path", required=True, help="Path to that sprint's data.json")
    p.set_defaults(func=cmd_task_status_init)

    p = sub.add_parser("task-status-set", help="Update one task's lifecycle status")
    p.add_argument("doc_type", help="e.g. sprints/sprint-01")
    p.add_argument("--id", required=True, help="Task ID, e.g. TASK-003")
    p.add_argument("--status", required=True,
                    choices=["NOT_READY", "READY", "IN_PROGRESS", "DONE"])
    p.set_defaults(func=cmd_task_status_set)

    p = sub.add_parser("task-status-list", help="List all task statuses for a sprint")
    p.add_argument("doc_type", help="e.g. sprints/sprint-01")
    p.set_defaults(func=cmd_task_status_list)

    sub.add_parser("list-doc-types",
                    help="List every document type that exists for this "
                         "project, with current version/status").set_defaults(
        func=cmd_list_doc_types)

    args = parser.parse_args()

    global ROOT
    if args.command in ("resolve-project", "list-projects"):
        pass  # these two establish/list projects and don't need ROOT
    else:
        if not args.project:
            print("ERROR: --project <project-id> is required for this command.\n"
                  "Ask the user for their project ID first. If they don't have "
                  "one, run `resolve-project` (optionally with --name) to mint "
                  "a new project.")
            sys.exit(2)
        entry = read_registry().get(args.project)
        if entry is None:
            print(f"ERROR: project '{args.project}' does not exist.\n"
                  f"Run `resolve-project --project {args.project}` to double-"
                  f"check the ID with the user, or omit --project on "
                  f"resolve-project to start a new project instead. Note: "
                  f"the project registry is tied to the current working "
                  f"directory — if this project was created from a "
                  f"different working directory (and no --location was "
                  f"given), it won't be found from here.")
            sys.exit(2)
        ROOT = Path(entry["path"])

    args.func(args)


if __name__ == "__main__":
    main()
