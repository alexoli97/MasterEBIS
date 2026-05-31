"""Extrae traza estructurada de un RunResult de OpenAI Agents SDK."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from agents import RunResult
from agents.items import (
    ItemHelpers,
    MessageOutputItem,
    ReasoningItem,
    ToolCallItem,
    ToolCallOutputItem,
)


@dataclass
class TraceEvent:
    kind: str               # "tool_call" | "tool_output" | "message" | "reasoning"
    name: str | None = None  # nombre de tool / agente
    arguments: str | None = None
    output: str | None = None
    text: str | None = None


@dataclass
class AgentTrace:
    agent: str
    events: list[TraceEvent] = field(default_factory=list)
    tool_call_count: int = 0
    duration_s: float | None = None
    final_text: str | None = None

    def tool_summary(self) -> list[dict[str, Any]]:
        return [
            {"tool": e.name, "args": e.arguments}
            for e in self.events
            if e.kind == "tool_call"
        ]


def extract_trace(agent_name: str, result: RunResult, duration_s: float | None = None) -> AgentTrace:
    trace = AgentTrace(agent=agent_name, duration_s=duration_s)

    for item in result.new_items:
        try:
            if isinstance(item, ToolCallItem):
                raw = item.raw_item
                name = getattr(raw, "name", None) or "tool"
                args = getattr(raw, "arguments", None)
                if args and not isinstance(args, str):
                    args = json.dumps(args, default=str)
                trace.events.append(TraceEvent(kind="tool_call", name=name, arguments=args))
                trace.tool_call_count += 1

            elif isinstance(item, ToolCallOutputItem):
                out = item.output
                if not isinstance(out, str):
                    try:
                        out = json.dumps(out, default=str)
                    except Exception:
                        out = str(out)
                trace.events.append(TraceEvent(kind="tool_output", output=out))

            elif isinstance(item, MessageOutputItem):
                text = ItemHelpers.text_message_output(item)
                if text:
                    trace.events.append(TraceEvent(kind="message", text=text))
                    trace.final_text = text

            elif isinstance(item, ReasoningItem):
                # reasoning items rara vez exponen texto en SDK pero registramos su existencia
                trace.events.append(TraceEvent(kind="reasoning", text="<reasoning step>"))
        except Exception as e:  # nunca romper UI por traza
            trace.events.append(TraceEvent(kind="message", text=f"[trace parse error: {e}]"))

    return trace
