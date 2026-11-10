# Đổi khung báo cáo sang mẫu Dự án của khoa: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `build_report.py` sinh báo cáo từ mẫu đúng của khoa (`TemplateCacMonDuAnVaThucTap_KhoaCNTT.dotx`) thay cho `khung_TDTU.docx`, với bìa, phần đầu và lề trang theo mẫu.

**Architecture:** Dùng thẳng file `.dotx` làm khung (đã kiểm 11/11: mọi style script cần đều có, định nghĩa trùng khung cũ trừ `numId` của tiêu đề; pandoc nhận `.dotx` làm reference; mọi section đã có lề 3,5 / 2 / 3 / 3,5 cm; có đúng 3 trường TOC). Khi ghép, đổi content type template → document để Word mở như docx. `fill_front_matter` thay các đoạn chữ mẫu (bìa, tên đề tài, chuyên ngành, GVHD, năm, lời cảm ơn) bằng cách thay **cả đoạn**, vì chữ mẫu bị tách qua nhiều run. Phần từ Chương 1 trở xuống không đổi cách làm.

**Tech Stack:** Python 3.14 thư viện chuẩn, pandoc, pytest; render kiểm bằng `docs/managements/tools/topdf.sh` (OnlyOffice x2t).

**Spec:** `docs/HANDOFF.md` mục 8 + quyết định của Đạt ngày 11/11 (ghi dưới đây).

## Global Constraints

- Khung: `docs/managements/HƯỚNG DẪN BÁO CÁO/3. Template báo cáo/DỰ ÁN CNTT/TemplateCacMonDuAnVaThucTap_KhoaCNTT.dotx`, đọc, không sửa (test `test_rebuild_is_stable_and_khung_untouched` giữ điều này).
- Theo mẫu của khoa, không thêm trang (Đạt, 11/11): **bỏ trang "PHẦN XÁC NHẬN VÀ ĐÁNH GIÁ CỦA GIẢNG VIÊN"** (mẫu không có); lề trang là lề của mẫu.
- Chuyên ngành: `KHOA HỌC MÁY TÍNH`.
- Sinh viên theo thứ tự MSSV (khớp tên file nộp `52300098_52300106`): `PHẠM HUỲNH QUỐC ĐẠT - 52300098`, `HOÀNG SINH HÙNG - 52300106` (dấu gạch như mẫu).
- Tên đề tài tiếng Việt nguyên văn đề cương mục 1, in hoa: `PHÁT TRIỂN HỆ THỐNG HỎI ĐÁP PHÁP LUẬT VIỆT NAM DỰA TRÊN AGENTIC-RAG VỚI TRUY XUẤT CĂN CỨ THEO HIỆU LỰC VÀ KIỂM CHỨNG TRÍCH DẪN`; tiếng Anh giữ `EN_TITLE` hiện có.
- GVHD: `PGS.TS. Lê Anh Cường`. Năm: `2026`. Ngày, tháng ở trang cảm ơn và cam đoan để trống (`…`), ký tay ở bản nộp.
- Cam đoan xưng "chúng tôi" (Đạt đã chọn 10/11), giữ logic hiện có.
- Không sửa nội dung 6 chương, không sửa code ngoài `docs/report/build_report.py`.
- Chỉ commit khi Đạt yêu cầu; Đạt tự push.

## Review Focus

- Mẫu đổi hoặc chữ mẫu gõ khác (vd "..." và "…") → build phải dừng bằng `ValueError` nêu chữ mẫu không thấy, không lặng lẽ để chữ mẫu trong bản nộp (test trong Task 1, Step 1).
- File ra bị Word coi là template (content type `.dotx`) → không mở được như docx hoặc mở thành "Document1" (test Task 1).
- Nội dung ví dụ của mẫu (chương NLP, VLSP, Hochreiter, Hình 2.1 Attention) lọt vào bản nộp (test Task 1).
- Chữ có `&`, `<` trong lời cảm ơn hay tên đề tài làm hỏng XML (test Task 1, Step 1).
- Tên đề tài dài xuống nhiều dòng làm bìa tràn sang trang 2 → chỉ thấy khi render (Task 2, Step 2).

---

### Task 1: Ghép báo cáo vào mẫu khoa, điền bìa và phần đầu

**Files:**
- Modify: `docs/report/build_report.py` (hằng `KHUNG` dòng 240; `set_paragraph_text` dòng 423; `fill_front_matter` dòng 469–504; `build` dòng 548–604)
- Modify: `docs/report/phan_dau.md` (thêm mục `## Lời cảm ơn`)
- Test: `tests/test_build_report.py`

**Interfaces:**
- Produces: `KHUNG: Path` (trỏ `.dotx`), `FIRST_CHAPTER = "MỞ ĐẦU VÀ TỔNG QUAN ĐỀ TÀI"` (Heading1 đầu tiên của phần thân trong mẫu, dùng ở `splice`), `VI_TITLE: str`, `FRONT_TEXT: dict[str, str]` (chữ mẫu, so khớp cả đoạn sau `strip()` → chữ thay), `replace_paragraphs(document: str, mapping: dict[str, str]) -> str`.

- [ ] **Step 1: Viết test RED**

Trong `tests/test_build_report.py`: đổi `KHUNG = br.KHUNG`. Thêm và sửa:

```python
def test_replace_paragraphs_swaps_every_exact_match_and_escapes():
    p = '<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>TÊN </w:t></w:r><w:r><w:t>ĐỀ TÀI</w:t></w:r></w:p>'
    doc = p + '<w:p><w:r><w:t>TÊN ĐỀ TÀI dài hơn</w:t></w:r></w:p>' + p
    out = br.replace_paragraphs(doc, {"TÊN ĐỀ TÀI": "A & B"})
    assert out.count("A &amp; B") == 2 and "TÊN ĐỀ TÀI dài hơn" in out      # chỉ thay đoạn khớp nguyên văn
    with pytest.raises(ValueError, match="TITLE"):
        br.replace_paragraphs(doc, {"TITLE": "x"})                          # chữ mẫu không còn: dừng, nêu tên


def test_set_paragraph_text_takes_format_of_first_run_with_text():
    p = '<w:p><w:r><w:rPr><w:i/></w:rPr><w:t></w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>X</w:t></w:r></w:p>'
    assert "<w:b/>" in br.set_paragraph_text(p, "Y") and "<w:i/>" not in br.set_paragraph_text(p, "Y")


def test_output_is_a_document_with_template_margins(built):
    types = read_part(built, "[Content_Types].xml")
    assert "document.main+xml" in types and "template.main+xml" not in types
    margins = re.findall(r"<w:pgMar [^>]*/>", read_part(built, "word/document.xml"))
    assert len(margins) == 5
    assert all('w:top="1985"' in m and 'w:right="1134"' in m and 'w:bottom="1701"' in m and 'w:left="1985"' in m
               for m in margins)
```

Sửa `test_front_matter_filled` (giữ các assert về Tóm tắt, viết tắt, tài liệu, cam đoan "chúng tôi"), bỏ assert về "đã tận tình đã tận tình" và "DEVELOPMENT OF A VIETNAMESE", thêm:

```python
    for sample in ("HỌ VÀ TÊN SINH VIÊN", "TÊN ĐỀ TÀI", "TÊN CHUYÊN NGÀNH", "Nguyễn Văn A", "NĂM …", "20..",
                   "TITLE", "……", "PHẦN XÁC NHẬN", "Hochreiter", "Scaled Dot-Product"):   # không dùng "VLSP": Chương 2 có nhắc
        assert sample not in text, sample
    assert text.count("PHẠM HUỲNH QUỐC ĐẠT - 52300098") == 2 and text.count("HOÀNG SINH HÙNG - 52300106") == 2
    assert text.count(br.VI_TITLE) == 3 and text.count("KHOA HỌC MÁY TÍNH") == 2
    assert "PGS.TS. Lê Anh Cường" in text and text.count("NĂM 2026") == 2 and text.count("năm 2026") == 2
    assert "hướng dẫn chúng em hoàn thành" in text
```

- [ ] **Step 2: Chạy test, thấy hỏng**

Run: `.venv/bin/python -m pytest -q tests/test_build_report.py`
Expected: FAIL (`replace_paragraphs` chưa có; `built` lỗi `ValueError: không thấy tiêu đề Heading1 'TỔNG QUAN ĐỀ TÀI'` hoặc thiếu đoạn mẫu).

- [ ] **Step 3: Sửa `build_report.py`**

- `KHUNG = REPORT_DIR.parent / "managements" / "HƯỚNG DẪN BÁO CÁO" / "3. Template báo cáo" / "DỰ ÁN CNTT" / "TemplateCacMonDuAnVaThucTap_KhoaCNTT.dotx"`; sửa docstring module và `build` (chữ "khung TDTU" → "mẫu Dự án của khoa").
- `build`: sau khi đọc zip, thay trong `files["[Content_Types].xml"]` chuỗi `wordprocessingml.template.main+xml` bằng `wordprocessingml.document.main+xml`; `splice(..., FIRST_CHAPTER, "TÀI LIỆU THAM KHẢO", body)`.
- `set_paragraph_text`: rPr lấy từ run đầu tiên có `<w:t>` không rỗng (mẫu hay mở đoạn bằng run rỗng mang định dạng khác).
- `replace_paragraphs`: duyệt `_INNER_PARAGRAPH`, đoạn có `_text(p).strip() == key` thì thay bằng `set_paragraph_text(p, xml.sax.saxutils.escape(value))`; key không khớp đoạn nào thì `ValueError(f"không thấy đoạn mẫu '{key}' trong khung")`.
- `FRONT_TEXT` (khóa là chữ mẫu, đã đọc từ `.dotx` ngày 11/11):

```python
FRONT_TEXT = {
    "HỌ VÀ TÊN SINH VIÊN 1 - MSSV": "PHẠM HUỲNH QUỐC ĐẠT - 52300098",
    "HỌ VÀ TÊN SINH VIÊN 2 - MSSV": "HOÀNG SINH HÙNG - 52300106",
    "TÊN ĐỀ TÀI": VI_TITLE,                       # bìa chính, bìa phụ, đầu trang Tóm tắt
    "TITLE": EN_TITLE,                            # đầu trang Abstract
    "TÊN CHUYÊN NGÀNH": "KHOA HỌC MÁY TÍNH",
    "TS. Nguyễn Văn A": "PGS.TS. Lê Anh Cường",   # dòng dưới "Người hướng dẫn" ở bìa phụ
    "THÀNH PHỐ HỒ CHÍ MINH, NĂM …": "THÀNH PHỐ HỒ CHÍ MINH, NĂM 2026",
    "TP. Hồ Chí Minh, ngày ... tháng … năm 20..": "TP. Hồ Chí Minh, ngày … tháng … năm 2026",   # trang cảm ơn
    "TP. Hồ Chí Minh, ngày … tháng … năm 20..": "TP. Hồ Chí Minh, ngày … tháng … năm 2026",    # trang cam đoan
}
```

- `fill_front_matter`: bỏ phần thay "DEVELOPMENT OF A VIETNAMESE" và phần sửa "đã tận tình đã tận tình"; gọi `replace_paragraphs(document, FRONT_TEXT)` trước khi chèn Tóm tắt/Abstract; đoạn mẫu cảm ơn (`_find_paragraph(document, "Chúng em xin chân thành cảm ơn")`) thay bằng một bản `set_paragraph_text` của chính đoạn đó cho mỗi đoạn của mục `## Lời cảm ơn` (tách theo dòng trống, escape); trong khoảng cam đoan, thay `TS. Nguyễn Văn A` → `PGS.TS. Lê Anh Cường` theo từng run (run này nguyên vẹn trong mẫu) cùng chỗ đổi "tôi" → "chúng tôi" đang có. Docstring nêu nguồn mục `Lời cảm ơn`.
- `phan_dau.md`: thêm `## Lời cảm ơn` với 2 đoạn của khung cũ đã sửa lỗi ("đã tận tình giảng dạy, giúp đỡ và hướng dẫn chúng em hoàn thành báo cáo này…"; "…nên vẫn còn nhiều thiếu sót, chúng em rất mong…").

- [ ] **Step 4: Chạy test, thấy qua**

Run: `.venv/bin/python -m pytest -q tests/test_build_report.py && .venv/bin/python -m pytest -q`
Expected: PASS hết (khoảng 374 test).

- [ ] **Step 5: Commit (khi Đạt yêu cầu)**

```bash
git add docs/report/build_report.py docs/report/phan_dau.md tests/test_build_report.py
git commit -m "feat: build the report on the faculty IT project template"
```

### Task 2: Build, render kiểm, bỏ khung cũ, đồng bộ tài liệu

**Files:**
- Modify: `docs/report/final_52300098_52300106.docx` (sinh lại)
- Delete: `docs/report/khung_TDTU.docx` (còn trong git)
- Modify: `AGENTS.md` (quy ước báo cáo), `docs/HANDOFF.md` (mục 1, 2, 7, 8), `docs/PLAN.md` + Phụ lục B `docs/managements/Đề cương DACNTT.md` (dòng nhắc khung), `docs/sprints/2026-11-16-sprint6-hung.md` (chỗ nhắc `khung_TDTU.docx`)

**Interfaces:**
- Consumes: `KHUNG`, `build` của Task 1.

- [ ] **Step 1: Build**

Run: `.venv/bin/python docs/report/build_report.py`
Expected: `Đã ghi docs/report/final_52300098_52300106.docx (5 cảnh báo)`, cả 5 là thiếu ảnh Hình 3.1–3.5 (H26).

- [ ] **Step 2: Render và xem**

Run: `bash docs/managements/tools/topdf.sh "$PWD/docs/report/final_52300098_52300106.docx" <scratchpad>/final.pdf`, rồi chuyển trang 1–10 và một trang chương sang PNG để xem.
Expected: bìa chính và bìa phụ mỗi bìa vừa 1 trang, tên SV trước tên đề tài, có "DỰ ÁN CÔNG NGHỆ THÔNG TIN", "KHOA HỌC MÁY TÍNH", "Người hướng dẫn / PGS.TS. Lê Anh Cường"; không còn trang xác nhận GV; Tóm tắt có tên đề tài tiếng Việt ở đầu, Abstract có tên tiếng Anh; chương có lề trái rộng hơn lề phải; ảnh và bảng không tràn lề. Số trang khoảng 71–80.

- [ ] **Step 3: Bỏ khung cũ, sửa tài liệu**

`git rm docs/report/khung_TDTU.docx`. Thay mọi chỗ nhắc `khung_TDTU.docx` là khung đang dùng (trong các file ở **Files**) bằng đường dẫn mẫu mới; plan cũ `2026-11-10-h23-report-dat.md` giữ nguyên (lịch sử). HANDOFF mục 8 ghi "đã làm" và các quyết định của Đạt; mục 2 bỏ việc 2.1.

- [ ] **Step 4: Kiểm lại**

Run: `.venv/bin/python -m pytest -q && grep -rn "khung_TDTU" AGENTS.md docs --include=*.md | grep -v "plans/2026-11-10"`
Expected: test PASS hết; grep chỉ còn các dòng lịch sử trong HANDOFF hoặc không còn dòng nào.

- [ ] **Step 5: Commit (khi Đạt yêu cầu)**

```bash
git add -A docs/report AGENTS.md docs/HANDOFF.md docs/PLAN.md "docs/managements/Đề cương DACNTT.md" docs/sprints/2026-11-16-sprint6-hung.md
git commit -m "docs: report rebuilt on the faculty template, old frame removed"
```
