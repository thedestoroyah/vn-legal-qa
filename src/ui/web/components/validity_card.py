"""Khu vực hiệu lực văn bản: thời điểm tra cứu (từ trace route) và thông tin văn bản (từ data/raw/laws.json).

Không tự tính hiệu lực: backend đã lọc bằng chứng theo hiệu lực (src/retrieval/filters.py) trước khi trả lời;
ở đây chỉ hiển thị lại ngày sự việc backend trích được và các trường có sẵn trong laws.json.
"""
from __future__ import annotations

from nicegui import ui

from src.ui.web.api.client import parse_chunk_id
from src.ui.web.api.schemas import AskResponse
from src.ui.web.config import LAWS_CATALOG


def _fmt(date: str | None) -> str:
    """'2021-01-01' -> '01/01/2021'; None -> '—'."""
    if not date:
        return "—"
    y, m, d = (date.split("-") + ["", ""])[:3]
    return f"{d}/{m}/{y}" if d else date


def cited_laws(resp: AskResponse) -> list[str]:
    """Mã văn bản xuất hiện trong citations, giữ thứ tự, bỏ trùng."""
    seen: list[str] = []
    for c in resp.citations:
        parsed = parse_chunk_id(c.chunk_id)
        if parsed and parsed[0] not in seen:
            seen.append(parsed[0])
    return seen


def validity_card(resp: AskResponse) -> None:
    with ui.column().classes("w-full gap-3 py-1"):
        # Banner tóm tắt thời điểm tra cứu
        with ui.card().classes("w-full bg-blue-50/70 border border-blue-200 shadow-none p-3"):
            with ui.row().classes("items-center gap-2 flex-wrap"):
                ui.icon("event_available", color="primary", size="sm")
                if resp.event_date:
                    ui.label("Thời điểm pháp lý của tình huống:").classes("text-sm font-medium text-slate-700")
                    ui.badge(_fmt(resp.event_date), color="primary").classes("text-xs font-semibold px-2 py-0.5")
                    ui.badge("Lọc theo mốc thời gian sự việc", color="indigo-2", text_color="indigo-9").classes("text-xs")
                elif resp.route_type is None:
                    ui.label("Chế độ chạy không qua bước định tuyến:").classes("text-sm font-medium text-slate-700")
                    ui.badge("Mặc định lọc văn bản đang có hiệu lực", color="blue-grey-2", text_color="blue-grey-9").classes("text-xs")
                else:
                    ui.label("Thời điểm pháp lý áp dụng:").classes("text-sm font-medium text-slate-700")
                    ui.badge("Hiện hành (văn bản đang còn hiệu lực)", color="positive").classes("text-xs font-semibold px-2 py-0.5")

            if resp.event_date:
                ui.label(
                    f"Hệ thống đã đối chiếu ngày sự việc ({_fmt(resp.event_date)}) với khoảng hiệu lực của văn bản "
                    "tại tầng truy xuất (src/retrieval/filters.py) trước khi sinh câu trả lời."
                ).classes("text-xs text-slate-600 mt-1")
            else:
                ui.label(
                    "Câu hỏi không nêu ngày xảy ra sự việc cụ thể; hệ thống chỉ sử dụng các văn bản có trạng thái "
                    "'Còn hiệu lực' trong cơ sở dữ liệu."
                ).classes("text-xs text-slate-600 mt-1")

        laws = cited_laws(resp)
        if not laws:
            ui.label("Câu trả lời không có văn bản được trích dẫn.").classes("text-sm text-slate-500 italic")
            return

        columns = [
            {"name": "doc", "label": "Văn bản pháp luật", "field": "doc", "align": "left"},
            {"name": "number", "label": "Số hiệu", "field": "number", "align": "left"},
            {"name": "issued", "label": "Ban hành", "field": "issued", "align": "center"},
            {"name": "effective", "label": "Có hiệu lực", "field": "effective", "align": "center"},
            {"name": "expiry", "label": "Hết hiệu lực", "field": "expiry", "align": "center"},
            {"name": "status", "label": "Trạng thái hiện hành", "field": "status", "align": "center"},
            {"name": "note", "label": "Áp dụng cho câu hỏi", "field": "note", "align": "left"},
        ]
        rows = []
        for law_id in laws:
            info = LAWS_CATALOG.get(law_id, {})
            status = info.get("status") or "Không xác định"
            if resp.event_date:
                note = f"Hợp lệ tại thời điểm {_fmt(resp.event_date)}"
            elif status == "Còn hiệu lực":
                note = "Đang có hiệu lực thi hành"
            else:
                note = "Đối chiếu lịch sử"
            rows.append(
                {
                    "doc": info.get("document", law_id),
                    "number": info.get("number") or "—",
                    "issued": _fmt(info.get("issued_date")),
                    "effective": _fmt(info.get("effective_date")),
                    "expiry": _fmt(info.get("expiry_date")) if info.get("expiry_date") else "Chưa có",
                    "status": status,
                    "note": note,
                }
            )
        table = (
            ui.table(columns=columns, rows=rows, row_key="doc")
            .props("dense flat bordered")
            .classes("w-full validity-table")
        )
        table.add_slot(
            "body-cell-status",
            """
            <q-td :props="props">
              <q-badge :color="props.value === 'Còn hiệu lực' ? 'positive'
                               : (props.value === 'Hết hiệu lực' ? 'negative' : 'grey-7')"
                       class="px-2 py-0.5 text-weight-medium">
                {{ props.value }}
              </q-badge>
            </q-td>""",
        )
        ui.label(
            "Nguồn đối chiếu: data/raw/laws.json. Trạng thái hiện hành phản ánh hiệu lực của văn bản ở thời điểm hiện tại; "
            "khi câu hỏi có mốc thời gian trong quá khứ, văn bản đã hết hiệu lực hiện nay vẫn là căn cứ đúng nếu đang có hiệu lực vào ngày sự việc."
        ).classes("text-xs text-slate-500 leading-relaxed")
