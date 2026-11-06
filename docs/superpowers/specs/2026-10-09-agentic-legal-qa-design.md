# Thiết kế: Hỏi đáp pháp luật Việt Nam dựa trên Agentic-RAG

Ngày: 2026-10-09 (cập nhật 2026-10-16) · Trạng thái: đã duyệt · Nguồn gốc: brainstorming, đã chốt cùng đề cương (`docs/managements/Đề cương DACNTT.md`)

## 1. Mục tiêu và tiêu chí thành công

Hệ thống trả lời câu hỏi pháp luật tiếng Việt, trích dẫn tới Điều/Khoản **đúng phiên bản văn bản có hiệu lực tại thời điểm của tình huống**, có tác tử tự kiểm chứng trích dẫn. Mỗi câu hỏi nghiên cứu có một bảng số liệu trả lời nó.

Ràng buộc: 2 người, hạn 04/12/2026 (dời từ 21/11), LLM qua API miễn phí (Gemini / Groq), embedding và reranker chạy local trên CPU, không fine-tune.

Chỉ tiêu: Hit@5 ≥ 80%, Recall@10 ≥ 75%, Citation Precision ≥ 85%.

## 2. Câu hỏi nghiên cứu

| RQ | Thí nghiệm | Chỉ số |
|---|---|---|
| RQ1 Truy xuất | BM25 / Dense / Hybrid RRF / Hybrid + Rerank | Hit@5, Recall@10, MRR@10 |
| RQ2 Phân đoạn | Fixed / Điều (+ tiêu đề) / Khoản / Khoản + tiêu đề (so ở cấp Điều) | Hit@5, Recall@10, DRM@5 |
| RQ3 Agentic | baseline / full / no_router / no_grading / no_verify | Citation P/R, Faithfulness, Answer Correctness, latency, số lượt gọi LLM |
| RQ4 Hiệu lực | Không lọc / lọc "còn hiệu lực" / lọc theo `event_date` (corpus có BLLD2012 + BLLD2019) | Tỷ lệ trích đúng phiên bản |

## 3. Dữ liệu

- Corpus: BLDS2015, BLLD2019, LDN2020, LTM2005 (văn bản gốc, chưa hợp nhất sửa đổi — ghi là giới hạn) + BLLD2012 (hết hiệu lực 2021-01-01, chỉ phục vụ RQ4). Không có Nghị định/Thông tư.
- Văn bản có hiệu lực tại ngày `d` khi `effective_date ≤ d < expiry_date` (`expiry_date = null` nghĩa là còn hiệu lực).
- Luồng dữ liệu: `.doc` → MinerU → `data/normalized/*.md` → `data/legal_structure_parser.py` → `data/structured/*.json` (đầu vào chuẩn) → `src/ingestion/legal_chunker.py` → `data/processed/chunks.jsonl` (Khoản), `chunks_article.jsonl` (Điều), `chunks_fixed.jsonl` (cố định).
- Đơn vị truy xuất của hệ thống: Khoản (Điểm nằm trong Khoản). `get_article` trả toàn văn Điều; mở rộng Khoản lên Điều cha là việc của bước sinh câu trả lời, không thuộc RQ2.
- Tập kiểm thử ~170–180 câu, trường `source` ∈ {zalo, synthetic, manual}, kết quả báo cáo tách theo nguồn:
  - zalo (~80): câu do người viết từ Zalo AI Legal Text Retrieval 2021 (MIT), chỉ BLDS + LDN, căn cứ cấp Điều. Bộ chính cho RQ1/RQ2.
  - synthetic (65): câu LLM sinh từ điều luật, có đáp án mẫu, phủ 4 luật. Bộ phụ; kiểm định tay mẫu 20 câu.
  - manual (~30–35): situational cho BLLĐ + LTM, temporal 10–15, direct ~5, out_of_scope ~5.
  - VLQA 2025 chưa công bố dữ liệu (kiểm tra 15/10/2026) nên không dùng.
- `gold_citations`: chunk_id cấp Khoản, hoặc khóa Điều `<LAW_ID>_Dieu<n>` khi chỉ biết căn cứ cấp Điều. Chỉ số cấp Khoản chỉ tính cho câu có toàn bộ căn cứ cấp Khoản.
- Định dạng file raw, `laws.json`, chunk, test case, API: xem Phụ lục A trong đề cương (nguồn chuẩn duy nhất).

## 4. Kiến trúc

```
src/ingestion/   legal_chunker.py, index.py          (đã có)
src/retrieval/   filters.py, bm25.py, dense.py, retriever.py   Retriever.search(query, k, date, mode), Retriever.get_article(law_id, number); load_retriever(variant)
src/generation/  llm.py, prompts.py, citations.py    client chuẩn OpenAI + cache đĩa + retry 429 + giãn cách RPM; tách/gỡ [chunk_id]
src/agent/       state.py, nodes.py, graph.py, run.py   LangGraph, Agent.run(question, config) -> dict (Phụ lục A.5)
src/api/         main.py                             FastAPI: /api/ask, /api/article, /health
src/ui/          app.py                              Streamlit: chat, panel nguyên văn, trace
eval/            cases.py, import_cases.py (gộp zalo + synthetic + manual, kiểm tra hợp lệ), metrics.py, evaluate.py, test_cases.json, results/
```

Ranh giới: agent chỉ gọi retrieval qua `Retriever.search` / `Retriever.get_article`, chỉ gọi LLM qua `llm.py`. UI chỉ nói chuyện với API. `evaluate.py` gọi thẳng `retrieval` (RQ1, RQ2) và `agent.run` (RQ3, RQ4), không đi qua API.

## 5. Tác tử

```
route ──┬─ out_of_scope ───────────────────────────→ từ chối
        ├─ direct ───→ lookup_article ─────────────┐
        └─ situational → retrieve → grade ─────────┤
                            ↑   thiếu, ≤2 lần      │
                            └── viết lại truy vấn ─┘
                                                   ↓
                               generate → verify ──→ trả lời
                                     ↑ câu mất hết căn cứ: sinh lại 1 lần
```

| Nút | LLM | Ghi chú |
|---|---|---|
| route | 1 | JSON `{type, event_date, law_id?, article?}` |
| lookup_article | 0 | |
| retrieve | 0 | `search(q, date=event_date)`. Không lọc theo lĩnh vực, để router đoán sai không kéo theo truy xuất sai |
| grade | 1 | `{sufficient, new_query}`. Hết 2 vòng vẫn thiếu thì trả "không đủ căn cứ" |
| generate | 1 | Mỗi khẳng định gắn `[chunk_id]` |
| verify | 1 | (a) regex: loại id không có trong context; (b) một lượt LLM kiểm từng cặp (câu, chunk) |

- Thông thường 4 lượt gọi LLM mỗi câu, tối đa khoảng 8.
- Cấu hình: `baseline` = retrieve (lọc còn hiệu lực) → generate → verify(a). Các cờ `use_router`, `use_grading`, `use_verify` tạo ra các cấu hình ablation.
- `trace` ghi mỗi bước: `{node, output, ms, llm_calls}`. Trace vừa hiển thị trên UI, vừa dùng cho phân tích lỗi.

## 6. Xử lý lỗi

- LLM: lỗi 429 thì chờ lũy tiến rồi thử lại. JSON hỏng thì thử lại 1 lần, sau đó dùng mặc định (route mặc định là `situational`, grade mặc định là `sufficient`).
- API: đầu vào sai trả 422. LLM lỗi hết số lần thử trả 503 kèm thông báo thân thiện, log chi tiết ở phía server. Chỉ mục thiếu hoặc lệch với file chunk: khi khởi động thì dừng và nêu lệnh nạp lại; khi đang phục vụ thì trả 500 JSON, log chi tiết.
- Không bao giờ trả về một câu trả lời có trích dẫn chưa qua bước verify(a).

## 7. Đánh giá

- Truy xuất, trích dẫn, phiên bản, từ chối: tính bằng code so với nhãn. Citation P/R tính ở cấp Điều.
- Faithfulness, Answer Correctness: LLM-judge, mỗi câu 1 lượt gọi, chạy trên nhà cung cấp khác với agent. Judge được kiểm định bằng 2 người chấm tay 20 câu.
- Latency đo trên 20 câu không dùng cache. Đầu ra thô lưu JSONL để chấm lại mà không phải chạy lại agent.
- Quota: khoảng 1.600 lượt gọi agent và 400 lượt judge, chia ra chạy trong 2–3 ngày, có cache.

## 8. Kiểm thử

- Unit test cho chunker, index, metrics, `llm.py` (client giả) và từng node (LLM giả).
- Graph test đi qua đủ các nhánh: out_of_scope, direct, vòng viết lại dừng sau 2 lần, verify gỡ trích dẫn sai.
- `validate_cases.py` kiểm tra tập test.

## 9. Rủi ro và phương án dự phòng

| Rủi ro | Phương án |
|---|---|
| Câu tổng hợp (LLM sinh) dễ hơn câu thật, thổi phồng chỉ số | Báo cáo tách theo nguồn; Zalo là bộ chính; kiểm định tay 20 câu |
| Văn bản gốc chưa hợp nhất sửa đổi | Ghi là giới hạn; Zalo cũng gán nhãn trên văn bản gốc nên nhãn vẫn khớp |
| Agent chưa ổn định vào 28/10 | Cắt grade và vòng viết lại, giữ router + verify |
| Hết quota | Chạy cấu hình phụ trên tập con 40 câu |
| Rerank trên CPU chậm (> 3s/câu) | Rerank top-10 thay vì top-20 |
| Model free tier gọi JSON kém | Few-shot, retry, giá trị mặc định an toàn. Đổi nhà cung cấp chỉ bằng `.env` |

## 10. Ngoài phạm vi

Nghị định/Thông tư, quan hệ dẫn chiếu và sửa đổi ở cấp Điều, hội thoại nhiều lượt, đăng nhập, khảo sát người dùng, fine-tune.
