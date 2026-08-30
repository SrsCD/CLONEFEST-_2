"""
Dependency Intelligence (#4) + Blast Radius (#11) — built on a real graph.

Builds a directed graph from real "blocks" relationships in Person 1's
BugOff backend: an edge bug_id -> related_bug_id means bug_id BLOCKS
related_bug_id (matches their API's relationship_type="blocks" shape).

HONEST NOTE: BugOff's schema has no dedicated "workflow" concept, so
blast-radius "workflows" are approximated using each affected bug's
component name — a reasonable stand-in, not a fabricated feature.
"""

import networkx as nx
from app.bugoff_client import get_bug_raw, get_bug_dependencies, list_bugs


def _build_graph(project_id: int):
    g = nx.DiGraph()
    bugs = list_bugs(project_id=project_id)
    component_map = {}

    for bug in bugs:
        g.add_node(bug["id"])
        component_map[bug["id"]] = bug.get("component_name", "unknown")

    for bug in bugs:
        deps = get_bug_dependencies(bug["id"])
        for rel in deps.get("outgoing", []):
            if rel["relationship_type"] == "blocks":
                g.add_edge(rel["bug_id"], rel["related_bug_id"])

    return g, component_map


def get_dependencies(bug_id: int):
    raw = get_bug_raw(bug_id)
    project_id = raw["project_id"]
    g, _ = _build_graph(project_id)

    if bug_id not in g:
        return {"blockers": [], "blocked_count": 0, "critical_path": []}

    blockers = list(g.predecessors(bug_id))
    blocked_count = g.out_degree(bug_id)
    ancestors = list(nx.ancestors(g, bug_id))
    critical_path = ancestors + [bug_id] if ancestors else [bug_id]

    return {"blockers": blockers, "blocked_count": blocked_count, "critical_path": critical_path}


def get_blast_radius(bug_id: int):
    raw = get_bug_raw(bug_id)
    project_id = raw["project_id"]
    g, component_map = _build_graph(project_id)

    if bug_id not in g:
        return {"components": [], "workflows": [], "affected_bugs": [], "severity_estimate": "Low"}

    affected_bugs = list(nx.descendants(g, bug_id))
    components = sorted({component_map.get(b, "unknown") for b in affected_bugs})
    # No dedicated "workflow" concept in BugOff's schema; component name
    # is used as a reasonable stand-in.
    workflows = components

    if len(affected_bugs) >= 3:
        severity_estimate = "High"
    elif len(affected_bugs) >= 1:
        severity_estimate = "Medium"
    else:
        severity_estimate = "Low"

    return {
        "components": components,
        "workflows": workflows,
        "affected_bugs": affected_bugs,
        "severity_estimate": severity_estimate,
    }
