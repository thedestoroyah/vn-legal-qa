# Sprint 3 — Việc của Hùng (22/10 – 28/10/2026)

Tài liệu này gồm 5 **thẻ việc** (H8–H12). Mỗi thẻ có đủ mục tiêu, file vào/ra, các bước và lệnh kiểm tra "xong chưa". Có thể dán nguyên một thẻ cho agent CLI hoặc web chat để nhờ hỗ trợ.

- Thiết kế tổng thể: `docs/superpowers/specs/2026-10-09-agentic-legal-qa-design.md`.
- Định dạng phản hồi API: **Phụ lục A.5** trong `Đề cương DACNTT.txt`.
- Phần Đạt làm song song (tác tử LangGraph): `docs/superpowers/plans/2026-10-16-sprint3-dat.md`.

## Đọc trước: việc Sprint 2 còn dở

Thẻ H1–H7 trong `docs/sprints/2026-10-15-sprint2-hung.md` chưa xong thẻ nào thì **làm thẻ đó trước** thẻ Sprint 3. Thứ tự ưu tiên:

1. **H1, H2** (BLLĐ 2012 và `laws.json`) và **H6** (câu manual). Sprint 4 chạy RQ3/RQ4 trên các câu này. Thiếu BLLĐ 2012 thì không có thí nghiệm RQ4.
2. H4, H5 (duyệt Zalo, kiểm định synthetic), rồi H3.
3. H7 (khung Streamlit) là nền cho H8, H9.

Sau khi xong H1, H2 hoặc H6, nhắn Đạt để Đạt nạp lại chỉ mục và chạy lại `python -m eval.import_cases`.

## Thứ tự và hạn

| Thẻ | Việc | Hạn | Phụ thuộc |
|---|---|---|---|
| H8 | Panel toàn văn Điều, tô sáng Khoản được trích | 24/10 | H7 |
| H9 | Trạng thái từ chối, nhãn "chưa có căn cứ", trace dễ đọc | 25/10 | H7 |
| H10 | Bản nháp prompt chấm (judge) | 26/10 | — |
| H11 | Thang chấm tay 3 mức | 26/10 | H10 |
| H12 | Bản nháp Chương 2 báo cáo | 28/10 | — |

Nghiệm thu Sprint 3 (28/10): giao diện chạy với 3 phản hồi mẫu (trả lời, từ chối, có câu chưa có căn cứ); bấm trích dẫn thì thấy toàn văn Điều với Khoản được tô sáng; có `docs/judge_prompts.md`, `docs/rubric.md` và bản nháp Chương 2.

## Quy trình chung

Giống Sprint 2:
- Luôn `git pull` trước khi làm.
- Commit nhỏ theo từng thẻ, message dạng `feat(ui): article panel`, `docs: judge prompts draft`.
- **Không sửa** code của Đạt: `src/agent/`, `src/generation/`, `src/retrieval/`, `src/ingestion/`, `eval/*.py`. Thấy lỗi thì báo Đạt.
- File của Hùng trong sprint này: `src/ui/`, `docs/judge_prompts.md`, `docs/rubric.md`, bản nháp báo cáo.

Giao diện **vẫn dùng dữ liệu mẫu**, chưa gọi API. Sprint 4 Đạt làm FastAPI, khi đó Hùng chỉ cần thay 2 hàm `ask` và `get_article` bằng lời gọi HTTP. Vì vậy mọi chỗ đọc dữ liệu đều phải đi qua 2 hàm này.

Định dạng `trace` mà tác tử thật trả về: mỗi bước có dạng `{"node", "output", "ms", "llm_calls"}`. Các khóa trong `output` theo từng nút như sau:

| node | các khóa trong `output` |
|---|---|
| `route` | `route_type` (situational / direct / out_of_scope), `event_date`, `direct_ref` |
| `lookup_article` | `evidence` (danh sách chunk_id) |
| `retrieve` | `queries` (câu hỏi gốc rồi các truy vấn viết lại), `evidence` |
| `grade` | `sufficient`, `rewrite`, có thêm `queries`, `n_rewrites` khi viết lại |
| `generate` | `insufficient`, `n_generations` |
| `verify` | `removed` (mã trích dẫn bị gỡ), `regenerate`, `unsupported` (câu bị yêu cầu viết lại) |
| `refuse` | `refused`, `refuse_reason` (out_of_scope / no_evidence / insufficient) |

---

## H8 — Panel toàn văn Điều, tô sáng Khoản được trích

**Mục tiêu:** bấm một thẻ trích dẫn thì panel bên phải hiện toàn văn Điều, Khoản được trích tô sáng. Trích dẫn cấp Điều (câu hỏi tra cứu trực tiếp, `clause = null`) thì hiện cả Điều, không tô sáng.

**Đầu ra:** `src/ui/sample_articles.json`, `src/ui/article_view.py` (mới), sửa `src/ui/app.py`.

**Các bước:**

1. Tạo file Điều mẫu từ kho. Lệnh dưới chỉ dùng thư viện chuẩn, chạy từ thư mục gốc repo:
   ```powershell
   python -c "import json; from src.ingestion.legal_chunker import read_jsonl; arts = {c['chunk_id']: c for c in read_jsonl('data/processed/chunks_article.jsonl')}; json.dump({k: arts[k] for k in ['BLDS2015_Dieu357', 'BLDS2015_Dieu468']}, open('src/ui/sample_articles.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)"
   ```
   Mỗi Điều trong file có dạng chunk cấp Điều: `chunk_id` (vd `BLDS2015_Dieu357`), `document`, `article`, `article_title`, `content`. Trường `content` gồm dẫn nhập (nếu có), rồi từng Khoản bắt đầu bằng `1. `, `2. `… trên dòng riêng. Sprint 4, `GET /api/article/{law_id}/{article}` trả về đúng dạng này.

2. Tạo `src/ui/article_view.py`. File này không import streamlit, để kiểm tra được bằng lệnh Python thường:
   ```python
   """Tách toàn văn Điều thành dẫn nhập + từng Khoản để tô sáng Khoản được trích."""
   import re

   _CLAUSE_RE = re.compile(r"(\d+)\. ")


   def article_key(chunk_id):
       """BLDS2015_Dieu357_Khoan1 -> BLDS2015_Dieu357."""
       return re.sub(r"_Khoan\w+$", "", chunk_id)


   def split_clauses(content):
       """[(số Khoản hoặc None cho dẫn nhập, đoạn văn)]; các Điểm a), b)... nằm trong Khoản của chúng."""
       blocks = []
       for line in content.split("\n"):
           m = _CLAUSE_RE.match(line)
           if m or not blocks:
               blocks.append((m.group(1) if m else None, [line]))
           else:
               blocks[-1][1].append(line)
       return [(number, "\n".join(lines)) for number, lines in blocks]


   def clause_number(clause):
       """'Khoản 2' -> '2'; None nếu trích dẫn cấp Điều."""
       return clause.removeprefix("Khoản ").strip() if clause else None
   ```

3. Sửa `src/ui/app.py`:
   - Thêm import `from article_view import article_key, clause_number, split_clauses`. Streamlit chạy `app.py` với thư mục của nó trong `sys.path`, nên import thẳng được.
   - Thêm hằng `ARTICLES = Path(__file__).with_name("sample_articles.json")` và hàm:
     ```python
     def get_article(chunk_id):
         # shortcut: đọc file mẫu; Sprint 4 thay bằng GET /api/article/{law_id}/{article}
         articles = json.loads(ARTICLES.read_text(encoding="utf-8"))
         return articles.get(article_key(chunk_id))
     ```
   - Thay nội dung của khối `with panel_col:` (nếu chưa có thì thêm vào cuối file) bằng:
     ```python
     with panel_col:
         c = st.session_state["selected"]
         if c is None:
             st.info("Bấm vào một trích dẫn để xem nguyên văn điều luật.")
         else:
             art = get_article(c["chunk_id"])
             if art is None:
                 st.warning(f"Chưa có nguyên văn của {c['chunk_id']} trong dữ liệu mẫu.")
             else:
                 st.subheader(f"{art['document']} – {art['article']}")
                 st.caption(art["article_title"])
                 target = clause_number(c.get("clause"))
                 for number, text in split_clauses(art["content"]):
                     (st.success if number is not None and number == target else st.markdown)(text)
     ```

**Xong khi:**
- Lệnh sau in `OK`:
  ```powershell
  cd src\ui; python -c "from article_view import split_clauses, clause_number; b = split_clauses('Dẫn nhập\n1. Khoản một\na) điểm a\n2. Khoản hai'); assert b == [(None, 'Dẫn nhập'), ('1', '1. Khoản một\na) điểm a'), ('2', '2. Khoản hai')], b; assert clause_number('Khoản 2') == '2' and clause_number(None) is None; print('OK')"; cd ..\..
  ```
- `streamlit run src/ui/app.py`, hỏi một câu bất kỳ, bấm thẻ "Bộ luật Dân sự 2015 – Điều 357, Khoản 2": panel hiện Điều 357 với Khoản 2 nền xanh, các Khoản khác bình thường.

---

## H9 — Từ chối, nhãn "chưa có căn cứ", trace dễ đọc

**Mục tiêu:** giao diện hiển thị đúng cả 3 kiểu phản hồi của tác tử. Trong mục "Các bước tác tử", mỗi bước có một dòng tóm tắt dễ đọc thay vì chỉ có JSON thô.

**Đầu ra:** thư mục `src/ui/samples/` gồm 3 file JSON; sửa `src/ui/app.py`; xóa `src/ui/sample_response.json` (chuyển vào `samples/`).

**Các bước:**

1. Tạo `src/ui/samples/answered.json`: chép nội dung `src/ui/sample_response.json` sang, rồi **thay toàn bộ `trace`** bằng định dạng thật:
   ```json
   [
     {"node": "route", "output": {"route_type": "situational", "event_date": null, "direct_ref": null}, "ms": 820, "llm_calls": 1},
     {"node": "retrieve", "output": {"queries": ["Bên mua trả tiền chậm có phải trả lãi không?"], "evidence": ["BLDS2015_Dieu357_Khoan1", "BLDS2015_Dieu357_Khoan2", "BLDS2015_Dieu468_Khoan1"]}, "ms": 5400, "llm_calls": 0},
     {"node": "grade", "output": {"sufficient": true, "rewrite": false}, "ms": 760, "llm_calls": 1},
     {"node": "generate", "output": {"insufficient": false, "n_generations": 1}, "ms": 2100, "llm_calls": 1},
     {"node": "verify", "output": {"removed": [], "regenerate": false, "unsupported": [], "refused": false}, "ms": 900, "llm_calls": 1}
   ]
   ```

2. Tạo `src/ui/samples/refused.json`:
   ```json
   {
     "answer": "Câu hỏi nằm ngoài phạm vi hệ thống. Hệ thống chỉ hỗ trợ Bộ luật Dân sự, Bộ luật Lao động, Luật Doanh nghiệp và Luật Thương mại.",
     "refused": true,
     "citations": [],
     "retrieved_chunks": [],
     "trace": [
       {"node": "route", "output": {"route_type": "out_of_scope", "event_date": null, "direct_ref": null}, "ms": 900, "llm_calls": 1},
       {"node": "refuse", "output": {"refused": true, "refuse_reason": "out_of_scope"}, "ms": 0, "llm_calls": 0}
     ]
   }
   ```

3. Tạo `src/ui/samples/partial.json`: câu trả lời có một câu bị gắn nhãn, có vòng viết lại truy vấn và sinh lại. Trong file này, `citations` chỉ gồm phần tử `BLDS2015_Dieu357_Khoan1`, chép từ `answered.json`.
   ```json
   {
     "answer": "Có. Bên chậm trả tiền phải trả lãi trên số tiền chậm trả, tương ứng với thời gian chậm trả [BLDS2015_Dieu357_Khoan1]. Lãi suất chậm trả luôn cố định 20% một năm (chưa có căn cứ).",
     "refused": false,
     "citations": ["<chép phần tử BLDS2015_Dieu357_Khoan1 từ answered.json vào đây>"],
     "retrieved_chunks": [{"chunk_id": "BLDS2015_Dieu357_Khoan1", "score": 0.91}, {"chunk_id": "BLDS2015_Dieu468_Khoan1", "score": 0.62}],
     "trace": [
       {"node": "route", "output": {"route_type": "situational", "event_date": null, "direct_ref": null}, "ms": 800, "llm_calls": 1},
       {"node": "retrieve", "output": {"queries": ["Mua hàng trả chậm có bị tính lãi không?"], "evidence": ["BLDS2015_Dieu357_Khoan1"]}, "ms": 5200, "llm_calls": 0},
       {"node": "grade", "output": {"sufficient": false, "rewrite": true, "queries": ["Mua hàng trả chậm có bị tính lãi không?", "lãi suất chậm trả tiền mức tối đa"], "n_rewrites": 1}, "ms": 700, "llm_calls": 1},
       {"node": "retrieve", "output": {"queries": ["Mua hàng trả chậm có bị tính lãi không?", "lãi suất chậm trả tiền mức tối đa"], "evidence": ["BLDS2015_Dieu357_Khoan1", "BLDS2015_Dieu468_Khoan1"]}, "ms": 5100, "llm_calls": 0},
       {"node": "grade", "output": {"sufficient": true, "rewrite": false}, "ms": 650, "llm_calls": 1},
       {"node": "generate", "output": {"insufficient": false, "n_generations": 1}, "ms": 2000, "llm_calls": 1},
       {"node": "verify", "output": {"removed": ["BLDS2015_Dieu468_Khoan1"], "regenerate": true, "unsupported": ["Lãi suất chậm trả luôn cố định 20% một năm [BLDS2015_Dieu468_Khoan1]."]}, "ms": 900, "llm_calls": 1},
       {"node": "generate", "output": {"insufficient": false, "n_generations": 2}, "ms": 1900, "llm_calls": 1},
       {"node": "verify", "output": {"removed": ["BLDS2015_Dieu468_Khoan1"], "regenerate": false, "unsupported": [], "refused": false}, "ms": 850, "llm_calls": 1}
     ]
   }
   ```

4. Sửa `src/ui/app.py`:
   - Thay hằng `SAMPLE` và hàm `ask` bằng phiên bản cho chọn phản hồi mẫu:
     ```python
     SAMPLES = Path(__file__).with_name("samples")
     NO_BASIS = "(chưa có căn cứ)"
     REASONS = {"out_of_scope": "ngoài phạm vi", "no_evidence": "không có văn bản hiệu lực tại thời điểm",
                "insufficient": "không đủ căn cứ"}


     def ask(question):
         # shortcut: trả phản hồi mẫu chọn ở thanh bên; Sprint 4 thay bằng POST /api/ask
         name = st.session_state.get("sample", "answered")
         return json.loads((SAMPLES / f"{name}.json").read_text(encoding="utf-8"))


     def step_note(step):
         """Một dòng tóm tắt dễ đọc cho mỗi bước trace."""
         o = step["output"]
         if step["node"] == "route":
             return f"Loại câu hỏi: {o['route_type']}" + (f" · ngày sự việc {o['event_date']}" if o.get("event_date") else "")
         if step["node"] == "retrieve":
             extra = f" · truy vấn viết lại: “{o['queries'][-1]}”" if len(o["queries"]) > 1 else ""
             return f"Tìm được {len(o['evidence'])} đoạn{extra}"
         if step["node"] == "grade":
             return "Đủ căn cứ" if o["sufficient"] else ("Chưa đủ, viết lại truy vấn" if o["rewrite"] else "Chưa đủ, dừng")
         if step["node"] == "verify":
             removed = ", ".join(o["removed"]) or "không"
             return f"Trích dẫn bị gỡ: {removed}" + (" · yêu cầu sinh lại" if o["regenerate"] else "")
         if step["node"] == "refuse":
             return f"Từ chối: {REASONS.get(o['refuse_reason'], o['refuse_reason'])}"
         return ""
     ```
   - Thêm thanh bên ngay sau `st.set_page_config(...)`:
     ```python
     st.sidebar.selectbox("Phản hồi mẫu", ["answered", "refused", "partial"], key="sample")
     ```
   - Trong vòng lặp hiển thị lịch sử, thay dòng `(st.warning if resp["refused"] else st.markdown)(resp["answer"])` bằng:
     ```python
             if resp["refused"]:
                 st.warning(resp["answer"])
             else:
                 st.markdown(resp["answer"].replace(NO_BASIS, f":orange[{NO_BASIS}]"))
     ```
   - Trong expander "Các bước tác tử", thay dòng `st.write(f"**{step['node']}** · ...")` bằng:
     ```python
                     st.write(f"**{step['node']}** · {step['ms']} ms · {step['llm_calls']} lượt gọi LLM — {step_note(step)}")
     ```
   - Dòng lưu ý `DISCLAIMER` (đã có từ H7) giữ nguyên dưới tiêu đề.

**Xong khi:** `streamlit run src/ui/app.py`, rồi lần lượt chọn 3 mẫu ở thanh bên và hỏi một câu:
- `answered`: câu trả lời bình thường, có 2 thẻ trích dẫn bấm được.
- `refused`: khung vàng cảnh báo, không có thẻ trích dẫn; trace ghi "Từ chối: ngoài phạm vi".
- `partial`: chữ "(chưa có căn cứ)" màu cam; trace có dòng "truy vấn viết lại" và "Trích dẫn bị gỡ: BLDS2015_Dieu468_Khoan1 · yêu cầu sinh lại".

---

## H10 — Bản nháp prompt chấm (judge) → `docs/judge_prompts.md`

**Mục tiêu:** viết 2 prompt cho bộ chấm LLM (chạy trên Groq ở Sprint 4), mỗi prompt chấm một tiêu chí theo thang 0 / 0,5 / 1. Đạt duyệt và đưa vào code ở Sprint 4.

**Định nghĩa (theo RAGAS, rút gọn thành 3 mức):**
- **Faithfulness (độ trung thành):** mọi khẳng định trong câu trả lời có được suy ra từ các đoạn trích (ngữ cảnh) mà hệ thống đã dùng hay không. Không so với đáp án mẫu.
- **Answer Correctness (độ đúng):** câu trả lời có khớp với đáp án mẫu (`reference_answer`) về nội dung pháp lý hay không: kết luận, điều kiện, con số, thời hạn.

**Yêu cầu với mỗi prompt:**
1. Viết bằng tiếng Việt. Có phần "Vai trò", "Định nghĩa", "Thang điểm" (mô tả rõ khi nào cho 0, 0,5, 1) và "Định dạng trả về".
2. Đầu vào ghi bằng biến trong ngoặc nhọn:
   - Faithfulness: `{question}`, `{answer}`, `{contexts}`.
   - Answer Correctness: `{question}`, `{answer}`, `{reference_answer}`.
3. Đầu ra **chỉ là JSON**: `{"score": 0 | 0.5 | 1, "reason": "<tối đa 2 câu>"}`.
4. Có 2 ví dụ mẫu: một câu được 1 điểm, một câu được 0 hoặc 0,5 điểm. Lấy nội dung từ các Điều thật, xem bằng `python -m eval.show_article BLDS2015 357`.
5. Ghi rõ cách xử lý 2 trường hợp đặc biệt:
   - Câu trả lời là lời từ chối (`refused = true`).
   - Câu có nhãn "(chưa có căn cứ)": khẳng định đó không được tính là có căn cứ.

**Xong khi:** file có 2 prompt đủ 5 yêu cầu trên. Dán từng prompt (thay biến bằng một ví dụ thật) vào web chat bất kỳ, và nhận về đúng một JSON hợp lệ.

---

## H11 — Thang chấm tay 3 mức → `docs/rubric.md`

**Mục tiêu:** hướng dẫn để 2 người (Đạt, Hùng) chấm tay độc lập 20 câu ở Sprint 4, rồi so với bộ chấm LLM để kiểm định bộ chấm.

**Nội dung bắt buộc:**
1. Với mỗi tiêu chí (Faithfulness, Answer Correctness), một bảng 3 dòng 0 / 0,5 / 1. Mỗi mức có mô tả và **một ví dụ thật** (câu hỏi, câu trả lời, căn cứ, điểm, lý do). Định nghĩa phải giống H10.
2. Quy tắc biên:
   - Câu từ chối đúng (câu out_of_scope bị từ chối) thì Answer Correctness = 1, Faithfulness ghi "không áp dụng".
   - Từ chối sai (câu trong phạm vi mà hệ thống từ chối) thì Answer Correctness = 0.
   - Đúng kết luận nhưng sai hoặc thiếu điều kiện, con số thì Answer Correctness = 0,5.
3. Mẫu bảng chấm để điền ở Sprint 4: `id | faithfulness | correctness | ghi chú | người chấm`.
4. Quy tắc làm việc: hai người chấm độc lập, không xem điểm của nhau và không xem điểm LLM trước khi chấm xong.

**Xong khi:** Đạt đọc và đồng ý. Thử chấm 2 câu trong `src/ui/samples/answered.json` và `partial.json` theo thang, hai người ra cùng điểm.

---

## H12 — Bản nháp Chương 2 (cơ sở lý thuyết)

**Mục tiêu:** bản nháp Chương 2 khoảng 8–12 trang, viết trong file báo cáo chung (Word hoặc Google Docs, theo mẫu khoa), gửi link cho Đạt.

**Các mục:**
1. Truy xuất thông tin từ vựng: BM25.
2. Truy xuất dày đặc (dense retrieval): bi-encoder, BGE-M3.
3. Kết hợp kết quả: Reciprocal Rank Fusion (RRF).
4. Xếp hạng lại bằng cross-encoder: bge-reranker-v2-m3.
5. Retrieval-Augmented Generation (RAG).
6. Agentic-RAG: định tuyến, tự đánh giá và viết lại truy vấn (Self-RAG, CRAG), kiểm chứng trích dẫn.
7. LangGraph: đồ thị trạng thái, cạnh có điều kiện.
8. Đặc thù văn bản pháp luật Việt Nam: cấu trúc Phần/Chương/Mục/Điều/Khoản/Điểm, hiệu lực theo thời gian.

**Yêu cầu:**
- Mỗi mục có: ý tưởng chính, công thức nếu có (BM25, RRF), và vai trò của kỹ thuật đó trong hệ thống của nhóm (1–2 câu nối với Chương 3).
- Trích dẫn nguồn gốc theo danh sách tài liệu tham khảo ở mục 12 của đề cương.
- Tài liệu nào chưa có trong mục 12 thì ghi `[CẦN KIỂM TRA]` cạnh trích dẫn, để Đạt tra lại tác giả, năm, hội nghị trước khi đưa vào bản chính. **Không chép số trang hay tác giả từ AI mà không kiểm tra.**

**Xong khi:** gửi link bản nháp cho Đạt. Đủ 8 mục, mọi trích dẫn hoặc có trong mục 12, hoặc có nhãn `[CẦN KIỂM TRA]`.
