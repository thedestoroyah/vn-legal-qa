// Slide báo cáo tuần 11: tái hiện thiết kế "Slide báo cáo giữa kỳ - KLTN.pptx" (Arial, xanh 2C5EAD/1591DC, thẻ EAF4FC).
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const [, , OUT, LOGO, CONTENT] = process.argv;
const C = JSON.parse(fs.readFileSync(CONTENT, "utf8"));
const M = C.meta;
const LOGO_DATA = "image/png;base64," + fs.readFileSync(LOGO).toString("base64");

const COL = { blue: "2C5EAD", sky: "1591DC", card: "EAF4FC", line: "BFDBFE", circle: "C4E2F5", text: "1F2937",
  muted: "6B7280", warnBg: "FEF3C7", warn: "B45309", red: "DC2626", green: "16A34A", greenBg: "DCFCE7", white: "FFFFFF" };
const FONT = "Arial";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Phạm Huỳnh Quốc Đạt, Hoàng Sinh Hùng";
pres.title = `${M.report} — ${M.code}`;
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
// ghi lại thứ tự slide để gắn lời thuyết trình (C.notes[i]) sau khi dựng xong
const SLIDES = [];
const addSlide = pres.addSlide.bind(pres);
pres.addSlide = (o) => { const s = addSlide(o); SLIDES.push(s); return s; };

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: COL.white },
  objects: [
    { image: { data: LOGO_DATA, x: 10.5, y: 0.18, w: 2.68, h: 1.08 } },
    { text: { text: M.footer, options: { x: 0.25, y: 7.05, w: 8.5, h: 0.3, fontFace: FONT, fontSize: 10.5, color: COL.sky, margin: 0 } } },
    { rect: { x: 12.45, y: 7.0, w: 0.6, h: 0.32, fill: { color: COL.circle } } },
  ],
  slideNumber: { x: 12.45, y: 7.0, w: 0.6, h: 0.32, fontFace: FONT, fontSize: 11, color: COL.blue, bold: true, align: "center", valign: "middle" },
});

const T = (slide, text, o) => slide.addText(text, { fontFace: FONT, color: COL.text, margin: 0, isTextBox: true, valign: "top", ...o });
const card = (slide, x, y, w, h, o = {}) => slide.addShape(pres.shapes.ROUNDED_RECTANGLE,
  { x, y, w, h, rectRadius: 0.1, fill: { color: o.fill || COL.card }, line: { color: o.line || COL.sky, width: 1 } });
const num = (slide, n, x, y, d = 0.48) => {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: COL.blue }, line: { color: COL.blue } });
  T(slide, String(n), { x, y, w: d, h: d, fontSize: 16, bold: true, color: COL.white, align: "center", valign: "middle" });
};
const bullets = (items, o = {}) => items.map((t, i) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: i < items.length - 1, paraSpaceAfter: o.gap ?? 5 } }));

function content(title, sub) {
  const s = pres.addSlide({ masterName: "CONTENT" });
  T(s, title, { x: 0.6, y: 0.32, w: 9.7, h: 0.6, fontSize: 27, bold: true, color: COL.blue, valign: "middle" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.62, y: 0.98, w: 0.08, h: 0.36, rectRadius: 0.04, fill: { color: COL.blue }, line: { color: COL.blue } });
  T(s, sub, { x: 0.8, y: 0.98, w: 9.5, h: 0.36, fontSize: 14, color: COL.sky, valign: "middle" });
  return s;
}

// ---------- 1. Trang tiêu đề
{
  const s = pres.addSlide();
  s.background = { color: COL.white };
  s.addShape(pres.shapes.OVAL, { x: -1.0, y: 5.6, w: 3.0, h: 3.0, fill: { color: COL.circle }, line: { color: COL.circle } });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 0.55, w: 12.2, h: 6.3, rectRadius: 0.2, fill: { color: COL.white, transparency: 100 }, line: { color: COL.sky, width: 1.25 } });
  s.addImage({ data: LOGO_DATA, x: 10.13, y: 0.61, w: 2.68, h: 1.08 });
  T(s, M.title, { x: 0.9, y: 0.75, w: 9.0, h: 1.75, fontSize: 21, bold: true, valign: "middle" });
  T(s, M.title_en, { x: 0.9, y: 2.55, w: 8.4, h: 0.62, fontSize: 12, italic: true, color: COL.sky });
  [["RAG", 0.8, false], ["LangGraph", 1.4, false], ["Hybrid Retrieval", 1.85, false], ["Temporal Validity", 1.95, true]]
    .reduce((x, [label, w, solid]) => {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.27, w, h: 0.34, rectRadius: 0.17, fill: { color: solid ? COL.blue : COL.card }, line: { color: solid ? COL.blue : COL.card } });
      T(s, label, { x, y: 3.27, w, h: 0.34, fontSize: 11, bold: true, color: solid ? COL.white : COL.blue, align: "center", valign: "middle" });
      return x + w + 0.1;
    }, 0.95);
  T(s, [
    { text: `${M.report} (26/10 – 01/11/2026) — ${M.course}`, options: { bold: true, breakLine: true } },
    { text: "Trường Đại học Tôn Đức Thắng | Khoa Công nghệ Thông tin", options: { breakLine: true } },
    { text: `Mã đề tài: ${M.code}`, options: { breakLine: true } },
    { text: "Sinh viên: Phạm Huỳnh Quốc Đạt (52300098) – Hoàng Sinh Hùng (52300106)", options: { breakLine: true } },
    { text: `Giảng viên hướng dẫn: ${M.supervisor}` },
  ], { x: 0.95, y: 4.1, w: 7.6, h: 1.7, fontSize: 13, color: COL.blue, paraSpaceAfter: 3 });
  [["Sprint 4 hoàn thành", "API · đánh giá · bộ chấm LLM", false], ["RQ3 + RQ4 đã chạy", "5 cấu hình · 3 chính sách hiệu lực", false],
    ["2 lỗi tác tử đã sửa", "Router · bước kiểm chứng", true]].forEach(([h, d, solid], i) => {
    const x = 8.75 + 0.3 * i, y = 3.0 + 1.05 * i;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.35, h: 0.9, rectRadius: 0.1, fill: { color: solid ? COL.blue : COL.white }, line: { color: COL.sky, width: 1 } });
    T(s, h, { x: x + 0.15, y: y + 0.08, w: 3.1, h: 0.38, fontSize: 14, bold: true, color: solid ? COL.white : COL.blue, valign: "middle" });
    T(s, d, { x: x + 0.15, y: y + 0.45, w: 3.1, h: 0.35, fontSize: 11.5, color: solid ? COL.white : COL.muted, valign: "middle" });
  });
}

// ---------- 2. Tổng quan tuần
{
  const s = content("TỔNG QUAN TUẦN 11", "Sprint 4 xong sớm 1 tuần; thực nghiệm RQ3, RQ4 đã chạy và chấm lần 1");
  [["6/6", "task Sprint 4 (Đạt)"], ["274", "test tự động đạt"], ["179", "câu kiểm thử (3 nguồn)"], ["4.853", "đoạn Khoản · 5 văn bản luật"], ["5 + 3", "cấu hình RQ3 + chính sách RQ4"]]
    .forEach(([v, l], i) => {
      const x = 0.6 + i * 2.43;
      card(s, x, 1.65, 2.23, 1.25);
      T(s, v, { x, y: 1.72, w: 2.23, h: 0.65, fontSize: 30, bold: true, color: COL.blue, align: "center", valign: "middle" });
      T(s, l, { x: x + 0.1, y: 2.38, w: 2.03, h: 0.42, fontSize: 12, color: COL.text, align: "center", valign: "middle" });
    });
  const cols = [["Đã hoàn thành", COL.green, ["Nạp BLLĐ 2012 vào 4 chỉ mục; kiểm chéo 37 câu tự soạn", "API FastAPI, lọc hiệu lực RQ4, pipeline thực nghiệm, bộ chấm Groq",
    "Chạy và chấm RQ3 (5 cấu hình) và RQ4 (12 câu × 3 chính sách)", "Sửa router từ chối nhầm và bước kiểm chứng gỡ nhầm trích dẫn"]],
    ["Đang thực hiện", COL.warn, ["Chạy lại RQ3, RQ4 với bước kiểm chứng đã sửa (chờ hạn mức API)", "Ghép giao diện Streamlit với API (Hùng)",
      "Chấm tay 20 câu để kiểm định bộ chấm LLM (Hùng, Đạt)", "Bản nháp Chương 1–2 của báo cáo"]]];
  cols.forEach(([h, color, items], i) => {
    const x = 0.6 + i * 6.1;
    card(s, x, 3.2, 5.9, 3.55, { fill: COL.white });
    T(s, h, { x: x + 0.25, y: 3.35, w: 5.4, h: 0.4, fontSize: 16, bold: true, color });
    T(s, bullets(items, { gap: 8 }), { x: x + 0.25, y: 3.85, w: 5.45, h: 2.8, fontSize: 14 });
  });
}

// ---------- 3. Dữ liệu và Sprint 4
{
  const s = content("KẾT QUẢ 1: DỮ LIỆU VÀ SPRINT 4", "Kho 5 văn bản luật, tập kiểm thử 179 câu, hạ tầng API và đánh giá câu trả lời");
  const items = [["BLLĐ 2012 vào kho", "242 Điều (hết hiệu lực 01/01/2021) nạp vào cả 4 chỉ mục, phục vụ RQ4."],
    ["Tập kiểm thử 179 câu", "77 Zalo · 65 tổng hợp · 37 tự soạn (15 tình huống, 12 mốc thời gian, 5 tra cứu, 5 ngoài phạm vi)."],
    ["API FastAPI", "/api/ask, /api/article, /health; đầu vào sai trả 422, mô hình lỗi trả 503."],
    ["Lọc hiệu lực RQ4", "3 chính sách: theo ngày sự việc, chỉ văn bản còn hiệu lực, không lọc."],
    ["Pipeline theo hạn mức", "Chạy dần qua nhiều ngày, tự dừng khi hết quota, chạy tiếp đúng chỗ dừng."],
    ["Bộ chấm LLM", "Groq gpt-oss-120b, khác nhà cung cấp với tác tử; chấm 0 / 0,5 / 1, kèm phiếu chấm tay."]];
  items.forEach(([h, d], i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.65 + Math.floor(i / 3) * 2.6;
    card(s, x, y, 3.85, 2.35);
    num(s, i + 1, x + 0.2, y + 0.18);
    T(s, h, { x: x + 0.8, y: y + 0.18, w: 2.95, h: 0.48, fontSize: 16, bold: true, color: COL.blue, valign: "middle" });
    T(s, d, { x: x + 0.2, y: y + 0.8, w: 3.45, h: 1.45, fontSize: 14 });
  });
}

// ---------- 4. RQ3
{
  const s = content("KẾT QUẢ 2: THỰC NGHIỆM RQ3", "5 cấu hình tác tử trên cùng mẫu phân tầng 60 câu (lần chạy 1)");
  const rows = C.ch1.sections[2].table.rows;
  const val = (r, i) => parseFloat(r[i].replace(",", "."));
  s.addChart(pres.charts.BAR, [
    { name: "Citation P", labels: rows.map((r) => r[0]), values: rows.map((r) => val(r, 2)) },
    { name: "Citation R", labels: rows.map((r) => r[0]), values: rows.map((r) => val(r, 3)) },
    { name: "Correctness", labels: rows.map((r) => r[0]), values: rows.map((r) => val(r, 5)) },
  ], { x: 0.6, y: 1.55, w: 7.4, h: 5.25, barDir: "col", barGapWidthPct: 60, chartColors: [COL.circle, COL.sky, COL.blue],
    valAxisMinVal: 0.6, valAxisMaxVal: 1.0, valAxisLabelFormatCode: "0.00", showValue: true, dataLabelFormatCode: "0.00", dataLabelFontSize: 9,
    dataLabelColor: COL.text, dataLabelPosition: "outEnd", showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt",
    catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, catAxisLabelColor: COL.text, valAxisLabelColor: COL.muted, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    dataLabelFontFace: "+mn-lt", valGridLine: { color: "E5E7EB", size: 0.5 }, catGridLine: { style: "none" },
    showTitle: true, title: "Chỉ số trích dẫn và độ đúng (mẫu 60 câu)", titleFontSize: 13, titleColor: COL.blue, titleFontFace: "+mn-lt" });
  card(s, 8.3, 1.6, 4.45, 5.2, { fill: COL.white });
  T(s, "Nhận xét", { x: 8.55, y: 1.75, w: 4, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(["Router và grading tăng tỷ lệ trả lời (0,850 → 0,917) và Correctness (0,868 → 0,985) so với baseline.",
    "no_verify có Citation R cao nhất (0,897): bước kiểm chứng đang gỡ nhầm trích dẫn đúng, xem slide 6.",
    "Toàn bộ 179 câu: full đạt P 0,840 / R 0,784 / Correctness 0,897; baseline 0,820 / 0,835 / 0,863.",
    "Faithfulness ≈ 1 ở mọi cấu hình: chờ chấm tay 20 câu để kiểm định bộ chấm."], { gap: 9 }),
  { x: 8.55, y: 2.25, w: 4.0, h: 4.45, fontSize: 13.5 });
}

// ---------- 5. RQ4
{
  const s = content("KẾT QUẢ 3: THỰC NGHIỆM RQ4", "Lọc theo ngày sự việc trích đúng phiên bản luật nhiều nhất (12 câu có mốc thời gian)");
  const rows = C.ch1.sections[3].table.rows;
  const val = (r, i) => parseFloat(r[i].replace(",", "."));
  s.addChart(pres.charts.BAR, [
    { name: "Đúng phiên bản", labels: rows.map((r) => r[0]), values: rows.map((r) => val(r, 2)) },
    { name: "Trả lời", labels: rows.map((r) => r[0]), values: rows.map((r) => val(r, 1)) },
  ], { x: 0.6, y: 1.55, w: 7.4, h: 5.25, barDir: "col", barGapWidthPct: 70, chartColors: [COL.blue, COL.circle],
    valAxisMinVal: 0, valAxisMaxVal: 1.0, valAxisLabelFormatCode: "0.0", showValue: true, dataLabelFormatCode: "0.000", dataLabelFontSize: 10,
    dataLabelColor: COL.text, dataLabelPosition: "outEnd", showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt",
    catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, catAxisLabelColor: COL.text, valAxisLabelColor: COL.muted, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    dataLabelFontFace: "+mn-lt", valGridLine: { color: "E5E7EB", size: 0.5 }, catGridLine: { style: "none" },
    showTitle: true, title: "Tỷ lệ theo chính sách lọc hiệu lực (cấu hình full)", titleFontSize: 13, titleColor: COL.blue, titleFontFace: "+mn-lt" });
  [["0,667", "Theo ngày sự việc", COL.blue], ["0,500", "Không lọc", COL.sky], ["0,417", "Chỉ còn hiệu lực", COL.warn]].forEach(([v, l, color], i) => {
    const y = 1.6 + i * 1.2;
    card(s, 8.3, y, 4.45, 1.05);
    T(s, v, { x: 8.45, y, w: 1.7, h: 1.05, fontSize: 30, bold: true, color, align: "center", valign: "middle" });
    T(s, [{ text: l, options: { bold: true, breakLine: true } }, { text: "tỷ lệ trích đúng phiên bản", options: { color: COL.muted } }],
      { x: 10.2, y, w: 2.45, h: 1.05, fontSize: 13, valign: "middle" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.3, y: 5.3, w: 4.45, h: 1.5, rectRadius: 0.1, fill: { color: COL.warnBg }, line: { color: COL.warnBg } });
  T(s, [{ text: "Lưu ý", options: { bold: true, color: COL.warn, breakLine: true } },
    { text: "Lọc \"còn hiệu lực\" bỏ mất BLLĐ 2012 nên từ chối 4/12 câu. Chỉ có 12 câu: kết quả thể hiện xu hướng, chưa đủ kết luận thống kê." }],
  { x: 8.5, y: 5.4, w: 4.1, h: 1.3, fontSize: 13 });
}

// ---------- 6. Hai lỗi
{
  const s = content("KẾT QUẢ 4: HAI LỖI PHÁT HIỆN VÀ KHẮC PHỤC", "Thực nghiệm chỉ ra điểm yếu của tác tử; đã sửa và đang chạy lại để so sánh");
  const cols = [["1", "Router từ chối nhầm câu dân sự",
    ["Vấn đề", "Prompt liệt kê lĩnh vực ngoài phạm vi theo từ khóa: câu về bồi thường tai nạn giao thông, thừa kế, hợp đồng dịch vụ bị từ chối."],
    ["Khắc phục", "Phân loại theo vấn đề pháp lý; liệt kê phạm vi Bộ luật Dân sự; ngoài phạm vi chỉ còn hình sự, xử phạt, thủ tục hành chính, thuế."],
    ["Kết quả", "26 câu kiểm tra trên LLM thật: 0 câu định tuyến sai."]],
  ["2", "Bước kiểm chứng gỡ nhầm trích dẫn đúng",
    ["Vấn đề", "47/63 mã bị gỡ (cấu hình full) là căn cứ đúng: bước kiểm chứng chỉ thấy nội dung Khoản, không thấy tên Điều."],
    ["Khắc phục", "Đưa tên văn bản, tên Điều vào ngữ cảnh; chỉ gỡ khi chắc chắn sai; giữ kết quả cũ để so sánh."],
    ["Sơ bộ (74 câu)", "Recall 0,734 → 0,761 · Precision 0,761 → 0,780 · mã đúng bị gỡ 17 → 8."]]];
  cols.forEach(([n, h, ...rows], i) => {
    const x = 0.6 + i * 6.1;
    card(s, x, 1.6, 5.9, 5.2, { fill: COL.white });
    num(s, n, x + 0.25, 1.78);
    T(s, h, { x: x + 0.9, y: 1.78, w: 4.9, h: 0.48, fontSize: 16, bold: true, color: COL.blue, valign: "middle" });
    rows.forEach(([label, text], j) => {
      const y = 2.5 + j * 1.42;
      const last = j === rows.length - 1;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.25, y, w: 5.4, h: 1.27, rectRadius: 0.08,
        fill: { color: last ? COL.greenBg : COL.card }, line: { color: last ? COL.greenBg : COL.card } });
      T(s, [{ text: label, options: { bold: true, color: last ? COL.green : COL.blue, breakLine: true } }, { text }],
        { x: x + 0.4, y: y + 0.08, w: 5.1, h: 1.12, fontSize: 13, valign: "middle" });
    });
  });
}

// ---------- 7. Tiến độ so với kế hoạch Khoa
{
  const s = content("ĐÁNH GIÁ TIẾN ĐỘ SO VỚI KẾ HOẠCH CỦA KHOA", "Đã qua 11/14 tuần (79%); 46/75 hạng mục xong (61%); phần kỹ thuật sớm khoảng 1 tuần");
  const X0 = 0.9, X1 = 12.4, Y = 2.3;
  const pos = (week) => X0 + (X1 - X0) * (week - 1) / 14;
  s.addShape(pres.shapes.LINE, { x: X0, y: Y, w: X1 - X0, h: 0, line: { color: COL.line, width: 6 } });
  s.addShape(pres.shapes.LINE, { x: X0, y: Y, w: pos(11) - X0, h: 0, line: { color: COL.sky, width: 6 } });
  [[1, "15/08", "Bắt đầu", COL.blue], [10, "22/10", "Giữa kỳ", COL.blue], [11.9, "01/11", "Hôm nay", COL.red], [13, "08/11", "Đóng băng", COL.white],
    [14.6, "21/11", "Nộp báo cáo", COL.white]].forEach(([w, date, label, fill], i) => {
    const x = pos(w);
    s.addShape(pres.shapes.OVAL, { x: x - 0.13, y: Y - 0.13, w: 0.26, h: 0.26, fill: { color: fill }, line: { color: fill === COL.white ? COL.blue : fill, width: 2 } });
    T(s, [{ text: date, options: { bold: true, color: fill === COL.red ? COL.red : COL.blue, breakLine: true } }, { text: label, options: { color: COL.muted } }],
      { x: x - 0.75, y: i % 2 ? Y + 0.22 : Y - 0.78, w: 1.5, h: 0.55, fontSize: 11, align: "center", valign: i % 2 ? "top" : "bottom" });
  });
  const tb = C.ch2.table;
  const status = (t) => t.startsWith("Hoàn thành") ? { color: COL.green, bold: true } : t.startsWith("Chưa") ? { color: COL.muted } : { color: COL.warn, bold: true };
  s.addTable([tb.head.map((h) => ({ text: h, options: { bold: true, color: COL.white, fill: { color: COL.blue } } })),
    ...tb.rows.map((r) => [{ text: r[0] }, { text: r[1] }, { text: r[2], options: status(r[2]) }])],
  { x: 0.6, y: 3.3, w: 7.9, colW: [0.9, 4.2, 2.8], fontFace: FONT, fontSize: 11.5, color: COL.text, border: { type: "solid", pt: 0.75, color: COL.line },
    fill: { color: COL.white }, rowH: 0.36, valign: "middle", margin: 0.05 });
  card(s, 8.8, 3.3, 3.95, 3.5, { fill: COL.white });
  T(s, "Tự đánh giá", { x: 9.0, y: 3.43, w: 3.6, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, C.ch2.verdict.map(([l, t], i) => [{ text: l + ": ", options: { bold: true, color: [COL.blue, COL.green, COL.warn][i] } },
    { text: t, options: { breakLine: i < 2, paraSpaceAfter: 8 } }]).flat(), { x: 9.0, y: 3.9, w: 3.6, h: 2.8, fontSize: 12.5 });
}

// ---------- 8. Kế hoạch
{
  const s = content("KẾ HOẠCH TỪ NAY ĐẾN 21/11/2026", "Ba tuần: hoàn tất thực nghiệm → phân tích, viết báo cáo → hoàn thiện và nộp");
  C.ch3.weeks.forEach((w, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.6, 3.85, 5.2, { fill: COL.white });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.6, w: 3.85, h: 1.05, rectRadius: 0.1, fill: { color: COL.blue }, line: { color: COL.blue } });
    T(s, [{ text: `${w.name} · ${w.dates}`, options: { fontSize: 12, color: COL.circle, breakLine: true } }, { text: w.goal, options: { fontSize: 17, bold: true, color: COL.white } }],
      { x: x + 0.2, y: 1.68, w: 3.5, h: 0.9, valign: "middle" });
    T(s, bullets(w.items, { gap: 9 }), { x: x + 0.2, y: 2.85, w: 3.5, h: 3.85, fontSize: 13.5 });
  });
}

// ---------- 9. Rủi ro
{
  const s = content("KHÓ KHĂN, RỦI RO VÀ GIẢI PHÁP", "Rủi ro lớn nhất là hạn mức API miễn phí và độ tin cậy của bộ chấm LLM");
  const short = ["Hạn mức API miễn phí", "Gemini quá tải (lỗi 503)", "Kiểm chứng gỡ nhầm", "Chỉnh prompt trên tập kiểm thử", "Bộ chấm LLM chấm dễ", "Mẫu nhỏ"];
  const detail = ["Gemini 500 lượt/ngày; Groq 200.000 token/ngày", "Khi chạy dài, kể cả sau khi SDK đã thử lại", "47/63 mã bị gỡ ở lần chạy 1 là căn cứ đúng", "Chưa có tập dev riêng để chỉnh prompt", "Faithfulness gần như luôn bằng 1", "RQ4 12 câu; ablation 60 câu"];
  C.ch4.rows.slice(0, 6).forEach(([risk, fix], i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.6 + Math.floor(i / 3) * 2.65;
    card(s, x, y, 3.85, 2.45, { fill: COL.white });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: y + 0.15, w: 3.55, h: 1.0, rectRadius: 0.08, fill: { color: COL.warnBg }, line: { color: COL.warnBg } });
    T(s, [{ text: short[i], options: { bold: true, breakLine: true } }, { text: detail[i], options: { fontSize: 11.5 } }],
      { x: x + 0.3, y: y + 0.18, w: 3.3, h: 0.95, fontSize: 14, color: COL.warn, valign: "middle" });
    T(s, fix, { x: x + 0.3, y: y + 1.25, w: 3.3, h: 1.15, fontSize: 12.5 });
  });
}

// ---------- 10. Tổng kết
{
  const s = content("TỔNG KẾT VÀ ĐỀ XUẤT", "Hạ tầng đánh giá đã sẵn sàng; tuần 12 hoàn tất thực nghiệm và đóng băng tính năng");
  [["Sprint 4 xong sớm", "API, pipeline thực nghiệm, bộ chấm LLM; 274 test tự động."], ["RQ3, RQ4 chạy lần 1", "Router và grading cải thiện câu trả lời; lọc theo ngày sự việc đúng phiên bản nhiều nhất."],
    ["Lỗi được phát hiện và sửa", "Router từ chối nhầm, bước kiểm chứng gỡ nhầm; đang chạy lại để so sánh."], ["Việc tuần 12", "Chạy lại RQ1–RQ4, chấm tay 20 câu, ghép giao diện với API, đóng băng 08/11."]]
    .forEach(([h, d], i) => {
      const x = 0.6 + (i % 2) * 6.1, y = 1.6 + Math.floor(i / 2) * 1.55;
      card(s, x, y, 5.9, 1.35);
      num(s, i + 1, x + 0.2, y + 0.43);
      T(s, [{ text: h, options: { bold: true, color: COL.blue, fontSize: 15, breakLine: true } }, { text: d, options: { fontSize: 13 } }],
        { x: x + 0.85, y: y + 0.12, w: 4.85, h: 1.1, valign: "middle" });
    });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 4.85, w: 12.0, h: 1.2, rectRadius: 0.1, fill: { color: COL.white }, line: { color: COL.sky, width: 1, dashType: "dash" } });
  T(s, "Em xin ý kiến Thầy: (1) có nên trình bày việc bước kiểm chứng bằng LLM nhỏ gỡ nhầm trích dẫn đúng như một phát hiện của RQ3, kèm số liệu trước/sau khi sửa? (2) mẫu 60 câu cho ablation và 12 câu cho RQ4 đã đủ cho báo cáo chưa?",
    { x: 0.85, y: 4.95, w: 11.5, h: 1.0, fontSize: 13, italic: true, valign: "middle" });
  T(s, "Em xin trân trọng cảm ơn Thầy đã lắng nghe.", { x: 0.6, y: 6.25, w: 12.0, h: 0.55, fontSize: 22, bold: true, color: COL.sky, align: "center", valign: "middle" });
}

SLIDES.forEach((s, i) => C.notes && C.notes[i] && s.addNotes(C.notes[i]));
pres.writeFile({ fileName: OUT }).then(() => console.log("saved", OUT));
