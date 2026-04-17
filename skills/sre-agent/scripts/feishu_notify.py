#!/usr/bin/env python3
"""
Webhook notification script (supports Feishu/Lark card format).
Usage: python3 feishu_notify.py --title "Title" --content "markdown content" --color red [--button-text "Button" --button-url "URL"]

Environment variables:
  ONCALL_FEISHU_WEBHOOK_URL    — Webhook URL
  ONCALL_FEISHU_WEBHOOK_SECRET — Webhook signing secret
"""

import argparse
import hashlib
import hmac
import base64
import time
import json
import os
import sys
import urllib.request

_CONTENT_TYPE_JSON = "application/json"


def compute_sign(timestamp: str, secret: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def send_card(
    webhook_url: str,
    secret: str,
    title: str,
    content: str,
    color: str = "red",
    button_text: str = None,
    button_url: str = None,
):
    timestamp = str(int(time.time()))
    sign = compute_sign(timestamp, secret)

    elements = [{"tag": "markdown", "content": content}]

    if button_text and button_url:
        elements.append(
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": button_text},
                        "url": button_url,
                        "type": "primary",
                    }
                ],
            }
        )

    payload = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": color,
            },
            "elements": elements,
        },
    }

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": _CONTENT_TYPE_JSON},
    )
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read().decode())
    return result


def send_multi_section_card(
    webhook_url: str,
    secret: str,
    title: str,
    sections: list,
    color: str = "red",
):
    """Send a multi-section card. Each section is a dict: {content, button_text?, button_url?}"""
    timestamp = str(int(time.time()))
    sign = compute_sign(timestamp, secret)

    elements = []
    for i, section in enumerate(sections):
        if i > 0:
            elements.append({"tag": "hr"})
        elements.append({"tag": "markdown", "content": section["content"]})
        if section.get("button_text") and section.get("button_url"):
            elements.append(
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": section["button_text"],
                            },
                            "url": section["button_url"],
                            "type": "primary",
                        }
                    ],
                }
            )

    payload = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": color,
            },
            "elements": elements,
        },
    }

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": _CONTENT_TYPE_JSON},
    )
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read().decode())
    return result


def _send_payload(webhook_url: str, secret: str, payload_card: dict):
    """Internal: sign and send card payload."""
    timestamp = str(int(time.time()))
    sign = compute_sign(timestamp, secret)
    payload = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "interactive",
        "card": payload_card,
    }
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": _CONTENT_TYPE_JSON},
    )
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read().decode())


def make_table(columns, rows, row_height="high", page_size=20):
    """Build a card table element.

    Args:
        columns: Column definitions list, each dict:
            {"name": "col_key", "display_name": "Display", "data_type": "text", "width": "300px"}
            width supports "auto" or "NNpx" (min 80px), do not mix in same table.
        rows: Row data list, each dict with keys matching column names.
        row_height: "low" or "high" (only these two values are valid).
        page_size: Rows per page.
    """
    return {
        "tag": "table",
        "page_size": page_size,
        "row_height": row_height,
        "header_style": {
            "text_align": "left",
            "text_size": "normal",
            "background_style": "grey",
            "text_color": "default",
            "bold": True,
            "lines": 1,
        },
        "columns": columns,
        "rows": rows,
    }


def send_elements_card(
    webhook_url: str,
    secret: str,
    title: str,
    elements: list,
    color: str = "red",
    wide_screen_mode: bool = True,
):
    """Send mixed-element card (supports markdown + table + hr + action combinations).

    Args:
        elements: Card element list, each a dict, e.g.:
            {"tag": "markdown", "content": "**Title**"}
            {"tag": "hr"}
            make_table(columns, rows)  # table element
    """
    card = {
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": color,
        },
        "elements": elements,
    }
    if wide_screen_mode:
        card["config"] = {"wide_screen_mode": True}
    return _send_payload(webhook_url, secret, card)


def _get_webhook():
    webhook_url = os.environ.get("ONCALL_FEISHU_WEBHOOK_URL")
    secret = os.environ.get("ONCALL_FEISHU_WEBHOOK_SECRET")
    if not webhook_url or not secret:
        print(
            "Error: ONCALL_FEISHU_WEBHOOK_URL and ONCALL_FEISHU_WEBHOOK_SECRET must be set",
            file=sys.stderr,
        )
        sys.exit(1)
    return webhook_url, secret


def main():
    # Detect subcommand usage
    known_commands = {"send-markdown", "send-elements"}
    use_subcommand = len(sys.argv) > 1 and sys.argv[1] in known_commands

    if not use_subcommand:
        # Legacy usage: feishu_notify.py --title ... --content ...
        parser = argparse.ArgumentParser(description="Webhook card notification")
        parser.add_argument("--title", required=True, help="Card title")
        parser.add_argument("--content", required=True, help="Markdown content")
        parser.add_argument(
            "--color", default="red",
            choices=["red", "yellow", "blue", "green", "grey"],
        )
        parser.add_argument("--button-text", help="Button text")
        parser.add_argument("--button-url", help="Button URL")
        args = parser.parse_args()
        webhook_url, secret = _get_webhook()

        content = args.content.replace("\\n", "\n")
        result = send_card(
            webhook_url=webhook_url,
            secret=secret,
            title=args.title,
            content=content,
            color=args.color,
            button_text=args.button_text,
            button_url=args.button_url,
        )
    else:
        parser = argparse.ArgumentParser(description="Webhook card notification")
        subparsers = parser.add_subparsers(dest="command")

        md_parser = subparsers.add_parser("send-markdown", help="Send Markdown card")
        md_parser.add_argument("--title", required=True)
        md_parser.add_argument("--content", required=True)
        md_parser.add_argument(
            "--color", default="red",
            choices=["red", "yellow", "blue", "green", "grey"],
        )
        md_parser.add_argument("--button-text")
        md_parser.add_argument("--button-url")

        el_parser = subparsers.add_parser("send-elements", help="Send mixed-element card")
        el_parser.add_argument("--title", required=True)
        el_parser.add_argument("--elements-file", required=True)
        el_parser.add_argument(
            "--color", default="red",
            choices=["red", "yellow", "blue", "green", "grey"],
        )
        el_parser.add_argument("--no-wide-screen", action="store_true")

        args = parser.parse_args()
        webhook_url, secret = _get_webhook()

        if args.command == "send-markdown":
            content = args.content.replace("\\n", "\n")
            result = send_card(
                webhook_url=webhook_url,
                secret=secret,
                title=args.title,
                content=content,
                color=args.color,
                button_text=args.button_text,
                button_url=args.button_url,
            )
        elif args.command == "send-elements":
            # Path validation: only allow files under cwd/.scripts/
            import pathlib
            resolved = pathlib.Path(args.elements_file).resolve()
            cwd_scripts = (pathlib.Path.cwd() / ".scripts").resolve()
            if not str(resolved).startswith(str(cwd_scripts)):
                print(f"Error: elements-file must be under .scripts/, got: {resolved}", file=sys.stderr)
                sys.exit(1)
            with open(args.elements_file, "r", encoding="utf-8") as f:
                elements = json.load(f)
            result = send_elements_card(
                webhook_url=webhook_url,
                secret=secret,
                title=args.title,
                elements=elements,
                color=args.color,
                wide_screen_mode=not args.no_wide_screen,
            )

    print(json.dumps(result))


if __name__ == "__main__":
    main()
