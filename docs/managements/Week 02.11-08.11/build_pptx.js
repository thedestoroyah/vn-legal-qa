// Slide báo cáo tuần 12: cùng thiết kế tuần 11 (tools/build_pptx.js), nội dung tuần 02/11 – 08/11/2026.
// node build_pptx.js <out.pptx> <logo.png> <content.json> <ảnh giao diện.png>
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const [, , OUT, LOGO, CONTENT, SCREENSHOT] = process.argv;
const C = JSON.parse(fs.readFileSync(CONTENT, "utf8"));
const M = C.meta;
const png = (path) => "image/png;base64," + fs.readFileSync(path).toString("base64");
const LOGO_DATA = png(LOGO);

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
const val = (r, i) => parseFloat(r[i].replace(",", "."));
const CHART = { barDir: "col", showValue: true, dataLabelColor: COL.text, dataLabelPosition: "outEnd", showLegend: true, legendPos: "b",
  legendFontSize: 12, legendFontFace: "+mn-lt", catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, catAxisLabelColor: COL.text,
  valAxisLabelColor: COL.muted, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt",
  valGridLine: { color: "E5E7EB", size: 0.5 }, catGridLine: { style: "none" }, showTitle: true, titleFontSize: 13,
  titleColor: COL.blue, titleFontFace: "+mn-lt" };

function content(title, sub) {
  const s = pres.addSlide({ masterName: "CONTENT" });
  T(s, title, { x: 0.6, y: 0.32, w: 9.7, h: 0.6, fontSize: 27, bold: true, color: COL.blue, valign: "middle" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.62, y: 0.98, w: 0.08, h: 0.36, rectRadius: 0.04, fill: { color: COL.blue }, line: { color: COL.blue } });
  T(s, sub, { x: 0.8, y: 0.98, w: 9.5, h: 0.36, fontSize: 14, color: COL.sky, valign: "middle" });
  return s;
}

// hai cột, mỗi cột 3 ô; ô cuối nền xanh lá (kết quả / kết luận)
function twoColumns(s, cols) {
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
    { text: `${M.report} (${M.dates}) — ${M.course}`, options: { bold: true, breakLine: true } },
    { text: "Trường Đại học Tôn Đức Thắng | Khoa Công nghệ Thông tin", options: { breakLine: true } },
    { text: `Mã đề tài: ${M.code}`, options: { breakLine: true } },
    { text: "Sinh viên: Phạm Huỳnh Quốc Đạt (52300098) – Hoàng Sinh Hùng (52300106)", options: { breakLine: true } },
    { text: `Giảng viên hướng dẫn: ${M.supervisor}` },
  ], { x: 0.95, y: 4.1, w: 7.6, h: 1.7, fontSize: 13, color: COL.blue, paraSpaceAfter: 3 });
  [["RQ1–RQ4 hoàn tất", "209 câu · kiểm định bootstrap 95%", false], ["Tập giữ riêng 30 câu", "Chốt trước khi chạy hệ thống", false],
    ["Hạn nộp 04/12/2026", "Kế hoạch đã điều chỉnh", true]].forEach(([h, d, solid], i) => {
    const x = 8.75 + 0.3 * i, y = 3.0 + 1.05 * i;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.35, h: 0.9, rectRadius: 0.1, fill: { color: solid ? COL.blue : COL.white }, line: { color: COL.sky, width: 1 } });
    T(s, h, { x: x + 0.15, y: y + 0.08, w: 3.1, h: 0.38, fontSize: 14, bold: true, color: solid ? COL.white : COL.blue, valign: "middle" });
    T(s, d, { x: x + 0.15, y: y + 0.45, w: 3.1, h: 0.35, fontSize: 11.5, color: solid ? COL.white : COL.muted, valign: "middle" });
  });
}

// ---------- 2. Tổng quan tuần
{
  const s = content("TỔNG QUAN TUẦN 12", "Thực nghiệm RQ1–RQ4 hoàn tất; phần kỹ thuật Sprint 5 xong trước khi sprint bắt đầu");
  [["209", "câu kiểm thử (+30 giữ riêng)"], ["319", "test tự động đạt"], ["96/97", "trích dẫn sai bị phát hiện"], ["15,9 s", "độ trễ trung vị (full)"], ["62/74", "hạng mục kế hoạch xong"]]
    .forEach(([v, l], i) => {
      const x = 0.6 + i * 2.43;
      card(s, x, 1.65, 2.23, 1.25);
      T(s, v, { x, y: 1.72, w: 2.23, h: 0.65, fontSize: 30, bold: true, color: COL.blue, align: "center", valign: "middle" });
      T(s, l, { x: x + 0.1, y: 2.38, w: 2.03, h: 0.42, fontSize: 12, color: COL.text, align: "center", valign: "middle" });
    });
  const cols = [["Đã hoàn thành", COL.green, ["Chạy lại RQ1–RQ4 với bước kiểm chứng đã sửa", "Tập giữ riêng 30 câu: chốt trước, chạy và chấm",
    "Phép thử kiểm chứng, chấm tay, độ trễ, phân tích lỗi", "Giao diện NiceGUI kết nối API; bản nháp Chương 1, 3, 4"]],
    ["Đang thực hiện", COL.warn, ["Chương 2 và Chương 5 (Hùng)", "Cập nhật số liệu Chương 1 (Hùng)",
      "Sơ đồ use case và sequence (Hùng)", "Chuẩn bị Sprint 6: Docker, README, ghép báo cáo"]]];
  cols.forEach(([h, color, items], i) => {
    const x = 0.6 + i * 6.1;
    card(s, x, 3.2, 5.9, 3.55, { fill: COL.white });
    T(s, h, { x: x + 0.25, y: 3.35, w: 5.4, h: 0.4, fontSize: 16, bold: true, color });
    T(s, bullets(items, { gap: 8 }), { x: x + 0.25, y: 3.85, w: 5.45, h: 2.8, fontSize: 14 });
  });
}

// ---------- 3. Thực nghiệm lại và tập giữ riêng
{
  const s = content("KẾT QUẢ 1: THỰC NGHIỆM LẠI VÀ TẬP GIỮ RIÊNG", "Sửa bước kiểm chứng, chạy lại RQ1–RQ4, mở rộng tập kiểm thử bằng 30 câu chốt trước");
  const items = [["Kiểm chứng phiên bản 2", "179 câu, full: Recall 0,784 → 0,830; căn cứ đúng bị gỡ nhầm 47 → 21."],
    ["RQ1, RQ2 (77 câu Zalo)", "Hybrid + rerank: Hit@5 0,844, Recall@10 0,872, đạt chỉ tiêu; phân đoạn theo cấu trúc ≫ cắt cố định."],
    ["Tập giữ riêng 30 câu", "20 câu mốc thời gian (10 cặp BLLĐ 2012/2019), 10 câu tra cứu; câu hỏi và giả thuyết chốt trước khi chạy."],
    ["Tập kiểm thử 209 câu", "77 Zalo · 65 tổng hợp · 67 tự soạn; câu có mốc thời gian tăng 12 → 32."],
    ["Kiểm định thống kê", "So sánh ghép cặp theo câu, khoảng tin cậy bootstrap 95%."],
    ["Rà soát M_017", "Hùng viết lại câu hỏi mơ hồ; chạy lại 5 cấu hình RQ3 và 3 chính sách RQ4."]];
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
  const s = content("KẾT QUẢ 2: THỰC NGHIỆM RQ3", "5 cấu hình tác tử trên cùng 209 câu, so sánh ghép cặp với full");
  const rows = C.ch1.sections[2].table.rows;
  s.addChart(pres.charts.BAR, [
    { name: "Citation P", labels: rows.map((r) => r[0]), values: rows.map((r) => val(r, 2)) },
    { name: "Citation R", labels: rows.map((r) => r[0]), values: rows.map((r) => val(r, 3)) },
    { name: "Đúng phiên bản (32 câu)", labels: rows.map((r) => r[0]), values: rows.map((r) => val(r, 4)) },
  ], { ...CHART, x: 0.6, y: 1.55, w: 7.4, h: 5.25, barGapWidthPct: 60, chartColors: [COL.circle, COL.sky, COL.blue],
    valAxisMinVal: 0.4, valAxisMaxVal: 1.0, valAxisLabelFormatCode: "0.0", dataLabelFormatCode: "0.00", dataLabelFontSize: 9,
    title: "Chỉ số trích dẫn và đúng phiên bản (209 câu)" });
  card(s, 8.3, 1.6, 4.45, 5.2, { fill: COL.white });
  T(s, "Nhận xét (* = có ý nghĩa 95%)", { x: 8.55, y: 1.75, w: 4, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(["Bỏ router: đúng phiên bản −0,250*, vì không trích được ngày sự việc.",
    "Baseline kém nhất về Citation P (−0,060*) và đúng phiên bản (−0,250*).",
    "Bỏ kiểm chứng: Recall +0,034* nhưng Precision −0,016*: kiểm chứng đổi recall lấy độ chính xác.",
    "30 câu giữ riêng: Precision của full 0,978 so với 0,740 khi bỏ router."], { gap: 9 }),
  { x: 8.55, y: 2.25, w: 4.0, h: 4.45, fontSize: 13.5 });
}

// ---------- 5. RQ4
{
  const s = content("KẾT QUẢ 3: THỰC NGHIỆM RQ4", "Lọc theo ngày sự việc trích đúng phiên bản luật nhiều nhất (32 câu có mốc thời gian)");
  const rows = C.ch1.sections[3].table.rows;
  s.addChart(pres.charts.BAR, [
    { name: "Đúng phiên bản", labels: rows.map((r) => r[0]), values: rows.map((r) => val(r, 2)) },
    { name: "Trả lời", labels: rows.map((r) => r[0]), values: rows.map((r) => val(r, 1)) },
  ], { ...CHART, x: 0.6, y: 1.55, w: 7.4, h: 5.25, barGapWidthPct: 70, chartColors: [COL.blue, COL.circle],
    valAxisMinVal: 0, valAxisMaxVal: 1.0, valAxisLabelFormatCode: "0.0", dataLabelFormatCode: "0.000", dataLabelFontSize: 10,
    title: "Tỷ lệ theo chính sách lọc hiệu lực (cấu hình full)" });
  rows.forEach(([l, , v], i) => {
    const y = 1.6 + i * 1.2;
    card(s, 8.3, y, 4.45, 1.05);
    T(s, v, { x: 8.45, y, w: 1.7, h: 1.05, fontSize: 30, bold: true, color: [COL.blue, COL.sky, COL.warn][i], align: "center", valign: "middle" });
    T(s, [{ text: l, options: { bold: true, breakLine: true } }, { text: "tỷ lệ trích đúng phiên bản", options: { color: COL.muted } }],
      { x: 10.2, y, w: 2.45, h: 1.05, fontSize: 13, valign: "middle" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.3, y: 5.3, w: 4.45, h: 1.5, rectRadius: 0.1, fill: { color: COL.warnBg }, line: { color: COL.warnBg } });
  T(s, [{ text: "Giả thuyết H2", options: { bold: true, color: COL.warn, breakLine: true } },
    { text: "Hơn \"chỉ còn hiệu lực\": có ý nghĩa (−0,312*). Hơn \"không lọc\": cùng chiều (−0,188) nhưng chưa có ý nghĩa." }],
  { x: 8.5, y: 5.4, w: 4.1, h: 1.3, fontSize: 13 });
}

// ---------- 6. Kiểm chứng, bộ chấm, độ trễ, lỗi
{
  const s = content("KẾT QUẢ 4: ĐỘ TIN CẬY, ĐỘ TRỄ VÀ PHÂN TÍCH LỖI", "Kiểm chứng bắt gần hết trích dẫn sai; bộ chấm LLM chỉ dùng làm chỉ số phụ");
  twoColumns(s, [["1", "Độ tin cậy của đánh giá",
    ["Tiêm trích dẫn sai", "Bước kiểm chứng phát hiện 96/97 trích dẫn sai, không gỡ nhầm mã đúng nào."],
    ["Chấm tay 20 câu", "Khớp bộ chấm 0,950 / 0,917, nhưng bộ chấm cho điểm tối đa ở mọi câu (kappa = 0)."],
    ["Kết luận", "Dựa chính vào chỉ số tính bằng code; điểm của bộ chấm là chỉ số phụ."]],
  ["2", "Độ trễ và phân tích lỗi",
    ["Độ trễ (19 câu, không cache)", "Trung vị full 15,9 s · baseline 6,9 s; truy xuất + rerank trên CPU ≈ 5,5 s."],
    ["20 câu sai của full", "12 lỗi thật: 5 trích dẫn không hỗ trợ, 3 từ chối nhầm, 2 truy xuất sai Điều, 2 thiếu ý."],
    ["Kết luận", "8/20 do chỉ số báo nhầm (trích thêm Điều liên quan): Citation Precision là cận dưới."]]]);
}

// ---------- 7. Giao diện và báo cáo
{
  const s = content("KẾT QUẢ 5: GIAO DIỆN WEB VÀ BÁO CÁO", "Giao diện NiceGUI kết nối API (Hùng); bản nháp Chương 1, 3, 4");
  // ảnh 1440×900: giữ tỷ lệ 16:10
  s.addImage({ data: png(SCREENSHOT), x: 0.6, y: 1.65, w: 7.6, h: 4.75 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.65, w: 7.6, h: 4.75, fill: { color: COL.white, transparency: 100 }, line: { color: COL.line, width: 1 } });
  T(s, "Câu trả lời kèm trích dẫn; bấm trích dẫn mở toàn văn Điều (bên phải).", { x: 0.6, y: 6.45, w: 7.6, h: 0.35, fontSize: 11.5, italic: true, color: COL.muted, align: "center" });
  card(s, 8.5, 1.6, 4.25, 5.2, { fill: COL.white });
  T(s, "Đã có", { x: 8.75, y: 1.75, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(["Thẻ trích dẫn, thẻ hiệu lực văn bản, các bước của tác tử",
    "Hiển thị trên laptop, máy tính bảng, điện thoại; 4 kịch bản demo chạy đúng",
    "API báo lỗi nhanh khi mô hình quá tải (20–50 s thay vì ~3 phút)",
    "Bản nháp Chương 1, 3, 4; 4 biểu đồ RQ1–RQ4; sơ đồ kiến trúc, activity",
    "Tài liệu tham khảo đã đối chiếu với nguồn gốc"], { gap: 9 }),
  { x: 8.75, y: 2.25, w: 3.85, h: 4.45, fontSize: 13 });
}

// ---------- 8. Tiến độ so với kế hoạch Khoa
{
  const s = content("ĐÁNH GIÁ TIẾN ĐỘ SO VỚI KẾ HOẠCH CỦA KHOA", "Đã qua 12/16 tuần (75%); 62/74 hạng mục xong (84%); phần kỹ thuật sớm khoảng 1,5 tuần");
  const X0 = 0.9, X1 = 12.4, Y = 2.3;
  const pos = (week) => X0 + (X1 - X0) * (week - 1) / 16;  // 16 tuần: 15/08 – 04/12
  s.addShape(pres.shapes.LINE, { x: X0, y: Y, w: X1 - X0, h: 0, line: { color: COL.line, width: 6 } });
  s.addShape(pres.shapes.LINE, { x: X0, y: Y, w: pos(12.86) - X0, h: 0, line: { color: COL.sky, width: 6 } });
  [[1, "15/08", "Bắt đầu", COL.blue], [10.43, "22/10", "Giữa kỳ", COL.blue], [12.86, "08/11", "Hôm nay", COL.red], [13.43, "12/11", "Đóng băng", COL.white],
    [15.57, "27/11", "Hoàn chỉnh", COL.white], [16.57, "04/12", "Hạn nộp", COL.white]].forEach(([w, date, label, fill], i) => {
    const x = pos(w);
    s.addShape(pres.shapes.OVAL, { x: x - 0.13, y: Y - 0.13, w: 0.26, h: 0.26, fill: { color: fill }, line: { color: fill === COL.white ? COL.blue : fill, width: 2 } });
    T(s, [{ text: date, options: { bold: true, color: fill === COL.red ? COL.red : COL.blue, breakLine: true } }, { text: label, options: { color: COL.muted } }],
      { x: x - 0.75, y: i % 2 ? Y + 0.22 : Y - 0.78, w: 1.5, h: 0.55, fontSize: 11, align: "center", valign: i % 2 ? "top" : "bottom" });
  });
  const tb = C.ch2.table;
  const status = (t) => t.startsWith("Hoàn thành") ? { color: COL.green, bold: true } : t.startsWith("Chưa") ? { color: COL.muted } : { color: COL.warn, bold: true };
  s.addTable([tb.head.map((h) => ({ text: h, options: { bold: true, color: COL.white, fill: { color: COL.blue } } })),
    ...tb.rows.map((r) => [{ text: r[0] }, { text: r[1] }, { text: r[2], options: status(r[2]) }])],
  { x: 0.6, y: 3.2, w: 8.0, colW: [0.95, 4.15, 2.9], fontFace: FONT, fontSize: 10.5, color: COL.text, border: { type: "solid", pt: 0.75, color: COL.line },
    fill: { color: COL.white }, rowH: 0.33, valign: "middle", margin: 0.04 });
  card(s, 8.85, 3.2, 3.9, 3.6, { fill: COL.white });
  T(s, "Tự đánh giá", { x: 9.05, y: 3.33, w: 3.55, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, C.ch2.verdict.map(([l, t], i) => [{ text: l + ": ", options: { bold: true, color: [COL.blue, COL.green, COL.warn][i] } },
    { text: t, options: { breakLine: i < 2, paraSpaceAfter: 8 } }]).flat(), { x: 9.05, y: 3.8, w: 3.55, h: 2.9, fontSize: 12 });
}

// ---------- 9. Kế hoạch
{
  const s = content("KẾ HOẠCH TỪ NAY ĐẾN 04/12/2026", "Hoàn thiện bản nháp → đóng gói, hoàn thiện báo cáo → dự phòng và nộp");
  C.ch3.weeks.forEach((w, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.6, 3.85, 5.2, { fill: COL.white });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.6, w: 3.85, h: 1.05, rectRadius: 0.1, fill: { color: COL.blue }, line: { color: COL.blue } });
    T(s, [{ text: `${w.name} · ${w.dates}`, options: { fontSize: 12, color: COL.circle, breakLine: true } }, { text: w.goal, options: { fontSize: 17, bold: true, color: COL.white } }],
      { x: x + 0.2, y: 1.68, w: 3.5, h: 0.9, valign: "middle" });
    T(s, bullets(w.items, { gap: 9 }), { x: x + 0.2, y: 2.85, w: 3.5, h: 3.85, fontSize: 13.5 });
  });
}

// ---------- 10. Rủi ro (6 mục đầu của ch4; lời giải rút gọn cho vừa ô)
{
  const s = content("KHÓ KHĂN, RỦI RO VÀ GIẢI PHÁP", "Rủi ro về hạn mức API đã giảm; còn lại chủ yếu là độ tin cậy của đánh giá và tiến độ viết báo cáo");
  const short = ["Gemini quá tải (503)", "Hạn mức API miễn phí", "Bộ chấm LLM dễ dãi", "Cỡ mẫu", "Chỉnh prompt trên tập kiểm thử", "Báo cáo dồn vào tuần 13"];
  const detail = ["Kéo dài nhiều giờ, ví dụ chiều 03/11", "Gemini 500 lượt/ngày/key; Groq ≈ 100 lượt chấm", "Điểm tối đa ở mọi câu chấm tay (kappa = 0)",
    "Vài chênh lệch chưa có ý nghĩa thống kê", "Chưa có tập dev riêng", "4 thẻ của Hùng, hạn 15/11"];
  const fix = ["Lỗi phía máy chủ (đã thử 2 mạng). API báo lỗi nhanh; thực nghiệm đã xong; quay demo khi ổn định, ghi sẵn bản dự phòng.",
    "Các lượt chạy chính đã xong; cache đĩa; pipeline tự dừng khi hết hạn mức và chạy tiếp đúng chỗ.",
    "Kết luận chính dựa vào chỉ số tính bằng code; điểm bộ chấm là chỉ số phụ, ghi rõ giới hạn.",
    "Báo cáo kèm khoảng tin cậy, số câu; nêu cả giả thuyết chưa được ủng hộ.",
    "Tập giữ riêng 30 câu chốt sau khi cố định prompt; kết quả cùng chiều.",
    "Thẻ việc chi tiết; Chương 3–4 đã có làm khung số liệu; còn 2 tuần đệm trước 27/11."];
  short.forEach((h, i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.6 + Math.floor(i / 3) * 2.65;
    card(s, x, y, 3.85, 2.45, { fill: COL.white });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: y + 0.15, w: 3.55, h: 1.0, rectRadius: 0.08, fill: { color: COL.warnBg }, line: { color: COL.warnBg } });
    T(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: detail[i], options: { fontSize: 11.5 } }],
      { x: x + 0.3, y: y + 0.18, w: 3.3, h: 0.95, fontSize: 14, color: COL.warn, valign: "middle" });
    T(s, fix[i], { x: x + 0.3, y: y + 1.25, w: 3.3, h: 1.15, fontSize: 12.5 });
  });
}

// ---------- 11. Tổng kết
{
  const s = content("TỔNG KẾT", "Thực nghiệm đã đủ; tuần 13 tập trung hoàn thiện bản nháp Chương 1–5");
  [["RQ1–RQ4 hoàn tất", "Kèm khoảng tin cậy 95%; router giúp đúng phiên bản; lọc theo ngày sự việc > chỉ còn hiệu lực."],
    ["Tập giữ riêng 30 câu", "Chốt trước khi chạy; kết quả cùng chiều với tập cũ."],
    ["Hệ thống hoàn chỉnh", "Giao diện web NiceGUI + API; 319 test; 4 kịch bản demo chạy đúng."],
    ["Việc tuần 13", "Chương 2, 5; sơ đồ use case, sequence; đóng băng 12/11; nghiệm thu 15/11."]]
    .forEach(([h, d], i) => {
      const x = 0.6 + (i % 2) * 6.1, y = 1.6 + Math.floor(i / 2) * 1.55;
      card(s, x, y, 5.9, 1.35);
      num(s, i + 1, x + 0.2, y + 0.43);
      T(s, [{ text: h, options: { bold: true, color: COL.blue, fontSize: 15, breakLine: true } }, { text: d, options: { fontSize: 13 } }],
        { x: x + 0.85, y: y + 0.12, w: 4.85, h: 1.1, valign: "middle" });
    });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 4.85, w: 12.0, h: 1.2, rectRadius: 0.1, fill: { color: COL.white }, line: { color: COL.sky, width: 1, dashType: "dash" } });
  T(s, "Sau báo cáo tuần 11, nhóm đã chốt: (1) trình bày bước kiểm chứng như một đánh đổi của RQ3 (tăng độ chính xác trích dẫn, giảm recall), kèm phép thử tiêm trích dẫn sai; (2) mở rộng mẫu bằng tập giữ riêng 30 câu thay vì chỉ dùng mẫu 60/12 câu.",
    { x: 0.85, y: 4.95, w: 11.5, h: 1.0, fontSize: 13, italic: true, valign: "middle" });
  T(s, "Em xin trân trọng cảm ơn Thầy đã lắng nghe.", { x: 0.6, y: 6.25, w: 12.0, h: 0.55, fontSize: 22, bold: true, color: COL.sky, align: "center", valign: "middle" });
}

if (C.notes && C.notes.length !== SLIDES.length) throw new Error(`notes ${C.notes.length} ≠ slides ${SLIDES.length}`);
SLIDES.forEach((s, i) => C.notes && C.notes[i] && s.addNotes(C.notes[i]));
pres.writeFile({ fileName: OUT }).then(() => console.log("saved", OUT));
