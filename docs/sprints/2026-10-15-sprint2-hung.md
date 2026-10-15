# Sprint 2 — Việc của Hùng (15/10 – 21/10/2026)

Tài liệu này gồm 7 **thẻ việc**. Mỗi thẻ tự đủ thông tin: mục tiêu, file vào/ra, các bước, lệnh kiểm tra "xong chưa". Có thể dán nguyên một thẻ cho agent CLI hoặc web chat để được hỗ trợ.

Thiết kế tổng thể: `docs/superpowers/specs/2026-10-09-agentic-legal-qa-design.md`. Định dạng dữ liệu: **Phụ lục A** trong `Đề cương DACNTT.txt` (đã cập nhật 15/10). Phần việc của Đạt chạy song song: `docs/superpowers/plans/2026-10-15-sprint2-dat.md`.

## Thay đổi so với kế hoạch cũ (đọc trước)

- **Không dùng VLQA** vì dữ liệu chưa được công bố. Nguồn câu hỏi mới có 3 loại, ghi trong trường `source`:
  - `zalo`: khoảng 81 câu do người viết, lấy từ Zalo AI 2021, chỉ có BLDS và LDN. Đạt nhập bằng script, Hùng duyệt.
  - `synthetic`: 65 câu trong `data/test_cases.json` mà Hùng đã sinh bằng AI. Giữ nguyên, kiểm định một mẫu 20 câu.
  - `manual`: câu do người viết, gồm câu tình huống cho BLLĐ và LTM, câu có mốc thời gian, câu tra cứu trực tiếp, câu ngoài phạm vi.
- **Dữ liệu luật:** pipeline của Hùng (`.doc` → MinerU → `normalized/*.md` → `legal_structure_parser.py` → `structured/*.json`) trở thành chuẩn. Đạt đọc `data/structured/*.json` để phân đoạn. Không cần làm file `data/raw/<LAW_ID>.md` nữa.
- `eval/test_cases.json` là file **sinh tự động** bằng lệnh `python -m eval.import_cases`, **không sửa tay**. Hùng chỉ sửa 3 file nguồn: `eval/manual_cases.json`, `eval/zalo_exclude.txt` và `data/test_cases.json`.

## Thứ tự và hạn

| Thẻ | Việc | Hạn | Phụ thuộc |
|---|---|---|---|
| H1 | Thêm BLLĐ 2012 vào kho | 17/10 | — |
| H2 | Hoàn thiện `laws.json` | 17/10 | — |
| H3 | Kiểm tra chất lượng dữ liệu luật | 18/10 | — |
| H4 | Duyệt khoảng 81 câu Zalo | 20/10 | Đạt nhập xong Zalo (Task 2 của Đạt, dự kiến 17/10) |
| H5 | Kiểm định 20 câu synthetic | 18/10 | Đạt nhập xong (như H4) |
| H6 | Soạn khoảng 35 câu manual | 20/10 | H1, H2 (câu temporal cần BLLĐ 2012) |
| H7 | Khung giao diện Streamlit | 21/10 | — |

Nghiệm thu Sprint 2 (21/10): `python -m eval.import_cases` chạy không lỗi, có đủ 3 nguồn; giao diện mẫu chạy được.

## Quy trình chung

**Môi trường (Windows PowerShell, chạy từ thư mục gốc repo `vn-legal-qa`):**

```powershell
git pull
python --version          # cần Python 3.10 trở lên
```

Các lệnh `python -m src.ingestion.legal_chunker`, `python -m eval.import_cases` và `python -m eval.show_article` **chỉ dùng thư viện chuẩn**, không cần cài gì. Riêng H7 cần cài Streamlit.

**Git:**
- Luôn chạy `git pull` trước khi làm.
- Commit nhỏ theo từng thẻ, message dạng `data: add BLLD2012 structured json`, `eval: add manual cases`, `feat: streamlit skeleton`, rồi `git push`.
- **Không sửa** các file code của Đạt: `src/ingestion/*.py`, `src/retrieval/`, `eval/*.py`. Thấy lỗi thì báo Đạt.
- File của Hùng: `data/raw/*.doc`, `data/normalized/`, `data/structured/`, `data/legal_*.py`, `data/test_cases.json`, mục BLLD2012 trong `data/raw/laws.json`, `docs/data_check.md`, `docs/synthetic_check.md`, `eval/manual_cases.json`, `eval/zalo_exclude.txt`, `src/ui/`.

**Xem toàn văn một Điều kèm `chunk_id`** (dùng ở H3–H6):

```powershell
python -m eval.show_article BLLD2019 35
```

Kết quả gồm một dòng tiêu đề, sau đó mỗi dòng là `[BLLD2019_Dieu35_Khoan1] nội dung...`. Chuỗi trong ngoặc vuông chính là mã căn cứ dùng cho `gold_citations`. Lệnh này cần file `data/processed/chunks.jsonl` (Đạt tạo ở Task 1, nhớ `git pull` để có). Nếu Hùng vừa thêm luật mới thì tự tạo lại bằng `python -m src.ingestion.legal_chunker`.

---

## H1 — Thêm Bộ luật Lao động 2012 vào kho

**Mục tiêu:** có `data/structured/10_2012_QH13_Bo_luat_Lao_dong.json`, đủ 242 Điều. Đây là văn bản đã hết hiệu lực, chỉ dùng cho RQ4 (hỏi đúng phiên bản luật theo thời điểm).

**Đầu vào:** toàn văn Bộ luật Lao động số 10/2012/QH13 (bản gốc) trên vbpl.vn hoặc thuvienphapluat.vn.
**Đầu ra:** `data/raw/10_2012_QH13_Bo_luat_Lao_dong.doc`, `data/normalized/10_2012_QH13_Bo_luat_Lao_dong.md`, `data/structured/10_2012_QH13_Bo_luat_Lao_dong.json`.

**Các bước** (giống cách đã làm với 4 luật trước, xem `data/normalized/note.txt`):
1. Tải file `.doc` và lưu đúng tên ở trên vào `data/raw/`.
2. Chạy:
   ```powershell
   mineru parse "data\raw\10_2012_QH13_Bo_luat_Lao_dong.doc" -o "data\normalized\10_2012_QH13_Bo_luat_Lao_dong.md"
   cd data
   python legal_structure_parser.py normalized -o structured
   cd ..
   ```
3. Mở file `.md` và kiểm tra nhanh:
   - Không còn header trang hay số trang.
   - Mỗi `**Điều N. ...**` nằm riêng một dòng.
4. Làm H2 (thêm BLLD2012 vào `laws.json`) rồi chạy `python -m src.ingestion.legal_chunker`.

**Xong khi:** lệnh `python -m src.ingestion.legal_chunker` in ra dòng `BLLD2012: 242 điều, ... chunk`, và **không** còn dòng `bỏ qua 10_2012_QH13...`. Nếu số Điều lệch khỏi 242 thì sửa ở file `.md` hoặc parser, rồi chạy lại bước 2. Commit cả 3 file cùng `data/processed/*.jsonl` mới sinh.

---

## H2 — Hoàn thiện `data/raw/laws.json`

**Mục tiêu:** cả 5 văn bản có metadata đúng và đã đối chiếu với nguồn chính thức. Hệ thống dùng các ngày trong file này để lọc luật theo hiệu lực, nên ghi sai ngày là trích sai phiên bản.

**Các bước:**
1. Chạy `git pull` trước, vì Đạt sẽ thêm trường `domain` cho 4 luật.
2. Với **từng** luật, mở trang văn bản trên vbpl.vn và đối chiếu `number`, `issued_date`, `effective_date`. Thêm trường `"source": "<URL trang văn bản>"`. Nếu ngày nào sai thì sửa và ghi chú lại để báo Đạt.
3. Thêm mục BLLD2012 theo mẫu dưới. Các ngày này là dự kiến, **phải đối chiếu lại**:
   ```json
   "BLLD2012": {
     "document": "Bộ luật Lao động 2012",
     "number": "10/2012/QH13",
     "issued_date": "2012-06-18",
     "effective_date": "2013-05-01",
     "expiry_date": "2021-01-01",
     "status": "Hết hiệu lực",
     "domain": "lao_dong",
     "source": "<URL>"
   }
   ```
   `expiry_date` của BLLD2012 phải đúng bằng `effective_date` của BLLD2019, tức là luật mới thay luật cũ ngay ngày đó.
4. `number` phải **trùng** với `law_number` trong file JSON cấu trúc (`"10/2012/QH13"`).

**Xong khi:**
```powershell
python -c "import json; d=json.load(open('data/raw/laws.json', encoding='utf-8')); print(sorted(d)); print({k: (v['effective_date'], v['expiry_date'], v.get('domain'), bool(v.get('source'))) for k, v in d.items()})"
```
in ra đủ 5 mã (`BLDS2015, BLLD2012, BLLD2019, LDN2020, LTM2005`), mỗi mã có `domain` và `source` là `True`.

---

## H3 — Kiểm tra chất lượng dữ liệu luật → `docs/data_check.md`

**Mục tiêu:** có bằng chứng rằng bước chuyển `.doc` → JSON không làm mất hay sai nội dung. Bảng kết quả này sẽ đưa vào báo cáo, chương Dữ liệu.

**Các bước:**
1. Chọn ngẫu nhiên 10 Điều cho mỗi luật (cố định seed để người khác làm lại được):
   ```powershell
   python -c "import random; random.seed(15); limits={'BLDS2015':689,'BLLD2019':220,'LDN2020':218,'LTM2005':324,'BLLD2012':242}; print({k: sorted(random.sample(range(1, n+1), 10)) for k, n in limits.items()})"
   ```
2. Với mỗi Điều, chạy `python -m eval.show_article <MÃ> <số>` rồi so với file `.doc` gốc. Kiểm tra 3 điều: nội dung có khớp không, số Khoản có đúng không, các Điểm a), b)... có nằm đủ trong Khoản không.
3. Ghi vào `docs/data_check.md` theo mẫu:
   ```markdown
   # Kiểm tra chất lượng dữ liệu luật (seed 15, 10 Điều/văn bản)

   | Văn bản | Điều | Nội dung khớp | Số khoản đúng | Điểm đủ | Ghi chú |
   |---|---|---|---|---|---|
   | BLDS2015 | 12 | ✅ | ✅ | ✅ | |

   **Tổng kết:** 50/50 Điều khớp hoàn toàn; lỗi phát hiện: ...
   ```

**Xong khi:** có đủ 50 dòng và đoạn tổng kết. Lỗi nào sửa được thì sửa ngay trong `.md` hoặc parser, rồi chạy lại H1 bước 2 cho luật đó.

---

## H4 — Duyệt khoảng 81 câu Zalo → `eval/zalo_exclude.txt`

**Mục tiêu:** loại những câu Zalo mà căn cứ không còn trả lời được câu hỏi trong văn bản của kho. Câu Zalo do người viết, gán nhãn ở cấp Điều, và là **bộ chính** cho RQ1.

**Đầu vào:** `eval/test_cases.json`, mở bằng VS Code, tìm các mục có `"source": "zalo"`. Đạt tạo file này ở Task 2, nhớ `git pull`.
**Đầu ra:** `eval/zalo_exclude.txt`, mỗi câu bị loại một dòng.

**Các bước:** với từng câu Zalo:
1. Đọc câu hỏi và `gold_citations`, ví dụ `BLDS2015_Dieu321` thì chạy `python -m eval.show_article BLDS2015 321`.
2. **Giữ** câu nếu đọc nội dung Điều đó là trả lời được câu hỏi, dù chỉ một phần.
3. **Loại** câu nếu rơi vào một trong các trường hợp:
   - Điều đó không liên quan đến câu hỏi.
   - Câu hỏi cần thêm văn bản khác ngoài kho (Nghị định, Thông tư) mới trả lời được.
   - Câu hỏi quá mơ hồ.

   Ghi vào `eval/zalo_exclude.txt` như sau:
   ```
   Z_0637bf82  # căn cứ chỉ đúng khi có Nghị định 100/2019
   ```

**Gợi ý dùng AI:** có thể dán câu hỏi và toàn văn Điều vào chat với prompt:
> "Đây là một câu hỏi pháp luật và một điều luật. Chỉ dựa vào điều luật này, có trả lời được câu hỏi không? Trả lời: CÓ / MỘT PHẦN / KHÔNG, kèm 1 câu lý do."

AI chỉ để gợi ý. **Người quyết định** giữ hay loại.

**Xong khi:** đã xem hết các câu Zalo, `python -m eval.import_cases` chạy không lỗi, và dòng `source:` cho thấy số câu zalo đã giảm đúng bằng số dòng trong file exclude.

---

## H5 — Kiểm định 20 câu synthetic → `docs/synthetic_check.md`

**Mục tiêu:** 65 câu trong `data/test_cases.json` do AI sinh nên phải kiểm định. Cách làm là đọc kỹ một mẫu 20 câu và báo cáo tỷ lệ đạt. Thiếu bước này thì hội đồng có thể không chấp nhận số liệu.

**Các bước:**
1. Chọn mẫu (seed cố định):
   ```powershell
   python -c "import json, random; random.seed(20); ids=[t['id'] for t in json.load(open('data/test_cases.json', encoding='utf-8'))['test_cases']]; print(sorted(random.sample(ids, 20)))"
   ```
2. Với mỗi câu, xem `ground_truth` (ví dụ `"clauses": ["35.2"]` nghĩa là Điều 35 Khoản 2), mở điều luật bằng `show_article`, rồi chấm 3 tiêu chí:
   - **Căn cứ đúng:** Khoản hoặc Điều được ghi có thực sự trả lời câu hỏi không.
   - **Căn cứ đủ:** có cần thêm Khoản hoặc Điều khác mới trả lời đủ không.
   - **Đáp án đúng:** `expected_answer` có đúng với văn bản không, có bịa thêm gì không.
3. Ghi vào `docs/synthetic_check.md`:
   ```markdown
   # Kiểm định câu tổng hợp (seed 20, 20/65 câu)

   | Mã | Căn cứ đúng | Căn cứ đủ | Đáp án đúng | Ghi chú / đã sửa |
   |---|---|---|---|---|

   **Tỷ lệ đạt cả 3 tiêu chí:** x/20. **Lỗi đã sửa trong data/test_cases.json:** ...
   ```
4. Câu nào sai thì **sửa trực tiếp trong `data/test_cases.json`** rồi chạy lại `python -m eval.import_cases`.

**Xong khi:** đủ 20 dòng, có tỷ lệ đạt, và `import_cases` chạy không lỗi.

---

## H6 — Soạn khoảng 35 câu manual → `eval/manual_cases.json`

**Mục tiêu:** bổ sung những loại câu mà Zalo và synthetic không có. Đây là các câu **do người viết**: có thể dùng AI để gợi ý ý tưởng, nhưng câu hỏi phải viết lại bằng lời của mình, và căn cứ phải tự tra.

| Loại (`type`) | Số câu | Nội dung |
|---|---|---|
| `situational` | ~15 | Tình huống đời thường: khoảng 8 câu BLLĐ 2019, 7 câu LTM 2005 (Zalo không có 2 luật này) |
| `temporal` | 10–15 | Tình huống có thời điểm, trong đó luật cũ và luật mới quy định **khác nhau** |
| `direct` | ~5 | "Điều X Luật Y quy định gì?" |
| `out_of_scope` | ~5 | Hình sự, giao thông, đất đai, thuế, hôn nhân gia đình (ngoài 5 văn bản) |

**Định dạng file:** `eval/manual_cases.json` là **một danh sách JSON**. Mã câu là `M_001`, `M_002`, ... Mẫu cho từng loại:

```json
[
  {"id": "M_001", "question": "Tôi làm ở công ty được 3 năm, hợp đồng không xác định thời hạn. Tôi muốn nghỉ việc thì phải báo trước bao lâu?",
   "type": "situational", "domain": "lao_dong", "event_date": null,
   "gold_citations": ["BLLD2019_Dieu35_Khoan1"], "reference_answer": "Phải báo trước ít nhất 45 ngày.",
   "source": "manual", "checked_by": null},
  {"id": "M_016", "question": "Tháng 3/2020 tôi ký hợp đồng lao động theo mùa vụ 6 tháng. Loại hợp đồng này có hợp lệ không?",
   "type": "temporal", "domain": "lao_dong", "event_date": "2020-03-01",
   "gold_citations": ["BLLD2012_Dieu22_Khoan1"], "reference_answer": "...",
   "source": "manual", "checked_by": null},
  {"id": "M_031", "question": "Điều 357 Bộ luật Dân sự 2015 quy định gì?",
   "type": "direct", "domain": "dan_su", "event_date": null,
   "gold_citations": ["BLDS2015_Dieu357"], "reference_answer": "Trách nhiệm trả lãi khi chậm thực hiện nghĩa vụ trả tiền.",
   "source": "manual", "checked_by": null},
  {"id": "M_036", "question": "Vượt đèn đỏ bằng xe máy bị phạt bao nhiêu tiền?",
   "type": "out_of_scope", "domain": "ngoai_pham_vi", "event_date": null,
   "gold_citations": [], "reference_answer": "Ngoài phạm vi kho dữ liệu.",
   "source": "manual", "checked_by": null}
]
```

Các số Điều và Khoản trong mẫu **phải tra lại** bằng `show_article` trước khi dùng.

**Quy tắc:**
- `gold_citations` dùng mã cấp Khoản (`..._Khoan1`) khi biết chính xác Khoản. Nếu không thì dùng mã cấp Điều (`BLLD2019_Dieu35`). Liệt kê **đủ** mọi căn cứ cần để trả lời.
- **Câu temporal:**
  - `event_date` ghi dạng `YYYY-MM-DD`.
  - Tình huống trước 01/01/2021 thì căn cứ là **BLLD2012**, từ 01/01/2021 trở đi là **BLLD2019**.
  - Nên soạn **thành cặp**: cùng một vấn đề, một câu năm 2020 và một câu năm 2022. Mỗi cặp thử được cả hai chiều.
  - Một số vấn đề thường khác nhau giữa hai bộ luật (gợi ý, **phải đọc cả hai bản để xác nhận**): hợp đồng lao động theo mùa vụ; người lao động đơn phương chấm dứt hợp đồng có cần lý do không; thời hạn báo trước; tuổi nghỉ hưu; giới hạn giờ làm thêm; thời gian thử việc cho người quản lý doanh nghiệp; số ngày nghỉ lễ Quốc khánh.
- Câu `out_of_scope` thì `gold_citations` là `[]` và `domain` là `"ngoai_pham_vi"`.
- Câu do Hùng soạn thì để `checked_by: null`. Khi Đạt kiểm chéo xong, Đạt đổi thành `"Dat"`.

**Gợi ý dùng AI để lấy ý tưởng câu tình huống:** dán toàn văn một Điều kèm prompt:
> "Dưới đây là một điều luật Việt Nam. Hãy gợi ý 3 tình huống đời thường mà một người lao động hoặc chủ doanh nghiệp có thể gặp và cần tới điều luật này. Chỉ mô tả tình huống, không trích lại câu chữ của điều luật, không nhắc số Điều."

Sau đó **tự viết** câu hỏi theo tình huống mình chọn, như cách người dân thật hay hỏi, rồi tự tra căn cứ.

**Xong khi:**
```powershell
python -m eval.import_cases
```
in ra `đã ghi ... câu`, dòng `source:` có `'manual': 35` (khoảng), và dòng `type:` có đủ 4 loại. Nếu báo lỗi thì đọc thông báo: mỗi dòng có dạng `M_0xx: <lỗi>`. Sửa đúng câu đó rồi chạy lại.

---

## H7 — Khung giao diện Streamlit (dữ liệu mẫu)

**Mục tiêu:** dựng bố cục giao diện, chưa nối API (Sprint 4 mới nối). Gồm khung chat bên trái; bên phải là panel hiện nguyên văn điều luật khi bấm vào trích dẫn; mục "Các bước tác tử" hiện trace.

**Cài đặt:** `pip install streamlit==1.65.0`

**Đầu ra:** `src/ui/sample_response.json`, `src/ui/app.py`. Xóa file thừa `src/ui/t.txt`.

1. Tạo `src/ui/sample_response.json`. File này đúng định dạng Phụ lục A.5, với nội dung Điều 357 BLDS lấy từ kho:
```json
{
  "answer": "Có. Bên chậm trả tiền phải trả lãi trên số tiền chậm trả, tương ứng với thời gian chậm trả [BLDS2015_Dieu357_Khoan1]. Lãi suất do các bên thỏa thuận nhưng không vượt mức tại khoản 1 Điều 468; nếu không thỏa thuận thì áp dụng khoản 2 Điều 468 [BLDS2015_Dieu357_Khoan2].",
  "refused": false,
  "citations": [
    {"chunk_id": "BLDS2015_Dieu357_Khoan1", "document": "Bộ luật Dân sự 2015", "article": "Điều 357", "clause": "Khoản 1",
     "content": "Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi đối với số tiền chậm trả tương ứng với thời gian chậm trả."},
    {"chunk_id": "BLDS2015_Dieu357_Khoan2", "document": "Bộ luật Dân sự 2015", "article": "Điều 357", "clause": "Khoản 2",
     "content": "Lãi suất phát sinh do chậm trả tiền được xác định theo thỏa thuận của các bên nhưng không được vượt quá mức lãi suất được quy định tại khoản 1 Điều 468 của Bộ luật này; nếu không có thỏa thuận thì thực hiện theo quy định tại khoản 2 Điều 468 của Bộ luật này."}
  ],
  "retrieved_chunks": [
    {"chunk_id": "BLDS2015_Dieu357_Khoan1", "score": 0.91},
    {"chunk_id": "BLDS2015_Dieu357_Khoan2", "score": 0.87},
    {"chunk_id": "BLDS2015_Dieu468_Khoan1", "score": 0.62}
  ],
  "trace": [
    {"node": "route", "output": {"type": "situational", "event_date": null}, "ms": 820, "llm_calls": 1},
    {"node": "retrieve", "output": {"query": "chậm trả tiền phải trả lãi", "top": ["BLDS2015_Dieu357_Khoan1", "BLDS2015_Dieu357_Khoan2"]}, "ms": 1450, "llm_calls": 0},
    {"node": "grade", "output": {"sufficient": true}, "ms": 760, "llm_calls": 1},
    {"node": "generate", "output": {"citations": 2}, "ms": 2100, "llm_calls": 1},
    {"node": "verify", "output": {"removed": []}, "ms": 900, "llm_calls": 1}
  ]
}
```

2. Tạo `src/ui/app.py`:
```python
"""Khung giao diện (Sprint 2): dùng phản hồi mẫu theo Phụ lục A.5, chưa gọi API."""
import json
from pathlib import Path

import streamlit as st

SAMPLE = Path(__file__).with_name("sample_response.json")
DISCLAIMER = "Thông tin chỉ mang tính tham khảo, không thay thế tư vấn pháp lý."


def ask(question):
    # shortcut: trả phản hồi mẫu cố định; Sprint 4 thay bằng gọi POST /api/ask
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def citation_label(c):
    return f"{c['document']} – {c['article']}" + (f", {c['clause']}" if c.get("clause") else "")


st.set_page_config(page_title="Hỏi đáp pháp luật", layout="wide")
st.session_state.setdefault("history", [])
st.session_state.setdefault("selected", None)
chat_col, panel_col = st.columns([2, 1])

with chat_col:
    st.title("Hỏi đáp pháp luật Việt Nam")
    st.caption(DISCLAIMER)
    for turn, (question, resp) in enumerate(st.session_state["history"]):
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            (st.warning if resp["refused"] else st.markdown)(resp["answer"])
            for c in resp["citations"]:
                if st.button(citation_label(c), key=f"{turn}-{c['chunk_id']}"):
                    st.session_state["selected"] = c
            with st.expander("Các bước tác tử"):
                for step in resp["trace"]:
                    st.write(f"**{step['node']}** · {step['ms']} ms · {step['llm_calls']} lượt gọi LLM")
                    st.json(step["output"], expanded=False)
    question = st.chat_input("Nhập câu hỏi pháp luật...")
    if question:
        st.session_state["history"].append((question, ask(question)))
        st.rerun()

with panel_col:
    st.subheader("Nguyên văn điều luật")
    selected = st.session_state["selected"]
    if selected is None:
        st.info("Bấm vào một trích dẫn để xem nguyên văn.")
    else:
        st.markdown(f"**{citation_label(selected)}**")
        st.write(selected["content"])
```

3. Chạy:
```powershell
streamlit run src/ui/app.py
```

**Xong khi:**
- Gõ một câu hỏi bất kỳ thì hiện câu trả lời mẫu cùng 2 nút trích dẫn.
- Bấm nút thì panel bên phải hiện nguyên văn Khoản tương ứng.
- Mở mục "Các bước tác tử" thấy 5 bước.
- Chụp ảnh màn hình lưu vào `docs/img/ui-sprint2.png` để dùng cho báo cáo.

**Mở rộng nếu còn thời gian** (không bắt buộc ở Sprint 2): vẽ wireframe cho bản cuối, trong đó panel phải hiện **toàn văn Điều** và tô sáng Khoản được trích. Sprint 3 sẽ làm phần này với API `/api/article`.
