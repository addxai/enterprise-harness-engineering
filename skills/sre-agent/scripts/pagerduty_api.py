#!/usr/bin/env python3
"""
PagerDuty API v2 客户端。
供 sre-agent 各模式调用，也可作为 CLI 独立使用。

环境变量:
  PAGERDUTY_API_TOKEN  — PagerDuty API v2 Access Key

CLI 用法:
  python3 pagerduty_api.py list-incidents --status triggered --urgency high --my-teams
  python3 pagerduty_api.py list-incidents --status triggered --status acknowledged --since 2026-03-15T21:00:00Z --until 2026-03-16T08:00:00Z --sort created_at:asc --limit 100
  python3 pagerduty_api.py get-incident Q1G0UGXKOB473G
  python3 pagerduty_api.py get-alerts Q1G0UGXKOB473G
  python3 pagerduty_api.py get-log-entries Q1G0UGXKOB473G
  python3 pagerduty_api.py list-services
  python3 pagerduty_api.py list-services --query payment
  python3 pagerduty_api.py oncall-poll                          # oncall 模式单轮拉取
  python3 pagerduty_api.py oncall-poll --since 2026-03-20T07:00:00Z  # 只拉取指定时间后的告警
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

BASE_URL = "https://api.pagerduty.com"
# Configure WEB_URL to your PagerDuty organization subdomain
WEB_URL = os.environ.get("PAGERDUTY_WEB_URL", "https://your-org.pagerduty.com")
_PATH_INCIDENTS = "/incidents"
_HELP_JSON_OUTPUT = "输出原始 JSON"
_HELP_INCIDENT_ID = "Incident ID"


def _get_token():
    token = os.environ.get("PAGERDUTY_API_TOKEN")
    if not token:
        print("Error: PAGERDUTY_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    return token


def _headers(token, from_email=None):
    h = {
        "Authorization": f"Token token={token}",
        "Accept": "application/vnd.pagerduty+json;version=2",
        "Content-Type": "application/json",
    }
    if from_email:
        h["From"] = from_email
    return h


def _request(method, path, token, params=None, body=None, from_email=None):
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)

    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method,
                                headers=_headers(token, from_email))
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"HTTP {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


def _paginate(path, token, params, key):
    """自动分页，返回所有结果。"""
    params = dict(params)
    params["limit"] = params.get("limit", 100)
    params["offset"] = 0
    params["total"] = "true"
    all_items = []
    while True:
        data = _request("GET", path, token, params)
        items = data.get(key, [])
        all_items.extend(items)
        if not data.get("more", False):
            break
        params["offset"] += params["limit"]
    return all_items, data.get("total", len(all_items))


# ─── Incidents 查询 ───

def list_incidents(token, statuses=None, urgencies=None, service_ids=None,
                   team_ids=None, since=None, until=None, sort_by=None,
                   limit=25, my_teams=False, paginate=False):
    params = {"total": "true"}
    if statuses:
        params["statuses[]"] = statuses
    if urgencies:
        params["urgencies[]"] = urgencies
    if service_ids:
        params["service_ids[]"] = service_ids
    if team_ids:
        params["team_ids[]"] = team_ids
    if since:
        params["since"] = since
    if until:
        params["until"] = until
    if sort_by:
        params["sort_by"] = sort_by
    if my_teams:
        params["on_my_teams"] = "true"
    params["limit"] = limit

    if paginate:
        incidents, total = _paginate(_PATH_INCIDENTS, token, params, "incidents")
        return {"incidents": incidents, "total": total}
    else:
        return _request("GET", _PATH_INCIDENTS, token, params)


def get_incident(token, incident_id):
    return _request("GET", f"/incidents/{incident_id}", token)


def get_alerts(token, incident_id):
    return _request("GET", f"/incidents/{incident_id}/alerts", token)


def get_log_entries(token, incident_id):
    return _request("GET", f"/incidents/{incident_id}/log_entries", token)


# ─── Incidents 变更 ───

def update_incidents(token, incidents_update, from_email):
    """批量更新 incidents 状态。
    incidents_update: [{"id": "XXX", "status": "acknowledged"}, ...]
    """
    body = {
        "incidents": [
            {"id": inc["id"], "type": "incident_reference", "status": inc["status"]}
            for inc in incidents_update
        ]
    }
    return _request("PUT", _PATH_INCIDENTS, token, body=body, from_email=from_email)


def acknowledge_incidents(token, incident_ids, from_email):
    return update_incidents(
        token, [{"id": iid, "status": "acknowledged"} for iid in incident_ids], from_email
    )


def resolve_incidents(token, incident_ids, from_email):
    return update_incidents(
        token, [{"id": iid, "status": "resolved"} for iid in incident_ids], from_email
    )


def add_note(token, incident_id, content, from_email):
    body = {"note": {"content": content}}
    return _request("POST", f"/incidents/{incident_id}/notes", token,
                    body=body, from_email=from_email)


# ─── Services ───

def list_services(token, query=None, limit=100):
    params = {"limit": limit}
    if query:
        params["query"] = query
    return _request("GET", "/services", token, params)


# ─── Oncall Poll ───

def oncall_poll(token, since=None):
    """oncall 单轮拉取：拉取 triggered 告警并返回。

    去重由 Triage 负责（标题+服务+时间窗口），Entry 无状态。

    Args:
        since: ISO 8601 时间字符串，只拉取此时间之后创建的告警（Entry 启动时间）。
    """
    now = datetime.now(timezone.utc)

    data = list_incidents(
        token, statuses=["triggered"], urgencies=["high"],
        my_teams=True, sort_by="created_at:desc", limit=25,
        since=since,
    )

    all_incidents = data.get("incidents", [])
    total = data.get("total", 0)

    return {
        "total_triggered": total,
        "new_count": len(all_incidents),
        "new_incidents": all_incidents,
        "last_poll": now.isoformat(),
    }


# ─── 格式化输出 ───

def format_incident_line(inc):
    return (
        f"#{inc['incident_number']} | {inc['created_at']} | "
        f"{inc['status']:12s} | {inc.get('urgency', ''):4s} | "
        f"{inc['service']['summary']:20s} | {inc['title']}"
    )


def format_incident_detail(inc):
    lines = [
        f"Incident #{inc['incident_number']}",
        f"  ID:       {inc['id']}",
        f"  Title:    {inc['title']}",
        f"  Status:   {inc['status']}",
        f"  Urgency:  {inc.get('urgency', 'N/A')}",
        f"  Service:  {inc['service']['summary']}",
        f"  Created:  {inc['created_at']}",
        f"  URL:      {inc.get('html_url', 'N/A')}",
    ]
    if inc.get("assignments"):
        assignees = ", ".join(
            a["assignee"]["summary"] for a in inc["assignments"] if "assignee" in a
        )
        lines.append(f"  Assigned: {assignees}")
    if inc.get("description"):
        lines.append(f"  Description: {inc['description'][:200]}")
    return "\n".join(lines)


# ─── CLI ───

def _build_parser():
    parser = argparse.ArgumentParser(description="PagerDuty API v2 客户端")
    sub = parser.add_subparsers(dest="command")

    # list-incidents
    p_list = sub.add_parser("list-incidents", help="查询告警列表")
    p_list.add_argument("--status", action="append", help="状态过滤 (可多次)")
    p_list.add_argument("--urgency", action="append", help="紧急度过滤 (可多次)")
    p_list.add_argument("--service-id", action="append", help="服务 ID 过滤 (可多次)")
    p_list.add_argument("--since", help="开始时间 (ISO 8601)")
    p_list.add_argument("--until", help="结束时间 (ISO 8601)")
    p_list.add_argument("--sort", default="created_at:desc", help="排序 (默认 created_at:desc)")
    p_list.add_argument("--limit", type=int, default=25, help="每页数量")
    p_list.add_argument("--my-teams", action="store_true", help="只看我的 team")
    p_list.add_argument("--all-pages", action="store_true", help="自动分页获取全部")
    p_list.add_argument("--json", action="store_true", help=_HELP_JSON_OUTPUT)

    # get-incident
    p_get = sub.add_parser("get-incident", help="获取 Incident 详情")
    p_get.add_argument("incident_id", help=_HELP_INCIDENT_ID)
    p_get.add_argument("--json", action="store_true", help=_HELP_JSON_OUTPUT)

    # get-alerts
    p_alerts = sub.add_parser("get-alerts", help="获取 Incident 关联的 Alerts")
    p_alerts.add_argument("incident_id", help=_HELP_INCIDENT_ID)

    # get-log-entries
    p_logs = sub.add_parser("get-log-entries", help="获取 Incident 日志条目")
    p_logs.add_argument("incident_id", help=_HELP_INCIDENT_ID)

    # list-services
    p_svc = sub.add_parser("list-services", help="查询服务列表")
    p_svc.add_argument("--query", help="按名称搜索")

    # oncall-poll
    p_poll = sub.add_parser("oncall-poll", help="oncall 单轮拉取")
    p_poll.add_argument("--since", help="只拉取此时间之后创建的告警 (ISO 8601, 如 Entry 启动时间)")
    p_poll.add_argument("--json", action="store_true", help=_HELP_JSON_OUTPUT)

    return parser


def _cmd_list_incidents(args, token):
    data = list_incidents(
        token, statuses=args.status, urgencies=args.urgency,
        service_ids=args.service_id, since=args.since, until=args.until,
        sort_by=args.sort, limit=args.limit, my_teams=args.my_teams,
        paginate=args.all_pages,
    )
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        incidents = data.get("incidents", [])
        total = data.get("total", len(incidents))
        print(f"Total: {total}, showing: {len(incidents)}\n")
        for inc in incidents:
            print(format_incident_line(inc))


def _cmd_get_incident(args, token):
    data = get_incident(token, args.incident_id)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(format_incident_detail(data.get("incident", data)))


def _cmd_get_alerts(args, token):
    data = get_alerts(token, args.incident_id)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _cmd_get_log_entries(args, token):
    data = get_log_entries(token, args.incident_id)
    for entry in data.get("log_entries", []):
        print(f"{entry['created_at']} | {entry['type']} | {entry.get('summary', '')}")


def _cmd_list_services(args, token):
    data = list_services(token, query=args.query)
    for svc in data.get("services", []):
        print(f"{svc['id']:10s} | {svc['summary']}")


def _cmd_oncall_poll(args, token):
    result = oncall_poll(token, since=args.since)
    if args.json:
        output = {
            "total_triggered": result["total_triggered"],
            "new_count": result["new_count"],
            "last_poll": result["last_poll"],
            "new_incidents": [
                {
                    "id": inc["id"],
                    "incident_number": inc["incident_number"],
                    "title": inc["title"],
                    "service": inc["service"]["summary"],
                    "urgency": inc.get("urgency"),
                    "created_at": inc["created_at"],
                    "html_url": inc.get("html_url"),
                }
                for inc in result["new_incidents"]
            ],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        if result["new_count"] == 0:
            print(f"无新告警 (triggered: {result['total_triggered']})")
        else:
            print(f"{result['new_count']} 条新告警:")
            for inc in result["new_incidents"]:
                print(f"  {format_incident_line(inc)}")


_COMMAND_HANDLERS = {
    "list-incidents": _cmd_list_incidents,
    "get-incident": _cmd_get_incident,
    "get-alerts": _cmd_get_alerts,
    "get-log-entries": _cmd_get_log_entries,
    "list-services": _cmd_list_services,
    "oncall-poll": _cmd_oncall_poll,
}


def main():
    parser = _build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    token = _get_token()
    _COMMAND_HANDLERS[args.command](args, token)


if __name__ == "__main__":
    main()
