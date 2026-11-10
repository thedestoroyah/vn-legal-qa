// Slide báo cáo tuần 13: chép từ tuần 12 (cùng thiết kế), nội dung tuần 09/11 – 15/11/2026.
// node build_pptx.js <out.pptx> <logo.png> <content.json> <ảnh 3 trang báo cáo.png> <sơ đồ kiến trúc.png>
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const [, , OUT, LOGO, CONTENT, REPORT_PAGES, ARCH] = process.argv;
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
  [["Báo cáo đủ 6 chương", "Ghép tự động theo mẫu của Khoa", false], ["Docker và tái lập", "Chạy hệ thống bằng một lệnh", false],
    ["Sprint 5 hoàn thành", "Sprint 6 làm sớm", true]].forEach(([h, d, solid], i) => {
    const x = 8.75 + 0.3 * i, y = 3.0 + 1.05 * i;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.35, h: 0.9, rectRadius: 0.1, fill: { color: solid ? COL.blue : COL.white }, line: { color: COL.sky, width: 1 } });
    T(s, h, { x: x + 0.15, y: y + 0.08, w: 3.1, h: 0.38, fontSize: 14, bold: true, color: solid ? COL.white : COL.blue, valign: "middle" });
    T(s, d, { x: x + 0.15, y: y + 0.45, w: 3.1, h: 0.35, fontSize: 11.5, color: solid ? COL.white : COL.muted, valign: "middle" });
  });
}

// ---------- 2. Tổng quan tuần
{
  const s = content("TỔNG QUAN TUẦN 13", "Sprint 5 hoàn thành; đóng gói và ghép báo cáo của Sprint 6 làm sớm");
  [["6", "chương báo cáo cuối kỳ"], ["381", "test tự động đạt"], ["73 MB", "bộ chỉ mục nộp kèm"], ["4", "sơ đồ vẽ theo mã nguồn"], ["72/79", "hạng mục kế hoạch xong"]]
    .forEach(([v, l], i) => {
      const x = 0.6 + i * 2.43;
      card(s, x, 1.65, 2.23, 1.25);
      T(s, v, { x, y: 1.72, w: 2.23, h: 0.65, fontSize: 30, bold: true, color: COL.blue, align: "center", valign: "middle" });
      T(s, l, { x: x + 0.1, y: 2.38, w: 2.03, h: 0.42, fontSize: 12, color: COL.text, align: "center", valign: "middle" });
    });
  const cols = [["Đã hoàn thành", COL.green, ["Docker, bộ chỉ mục nộp kèm, README tái lập", "Báo cáo đủ 6 chương; rà soát độc lập, sửa hết",
    "Ghép báo cáo theo mẫu môn Dự án của Khoa", "Sơ đồ use case, sequence; vẽ lại Hình 4.1–4.2"]],
    ["Đang thực hiện", COL.warn, ["Hình 3.1–3.4 và sơ đồ activity (Hùng, hạn 20/11)", "Đối chiếu quy định trình bày và rubric của môn",
      "Rà soát toàn bộ báo cáo; kiểm tra Turnitin", "Slide bảo vệ và video demo (Hùng)"]]];
  cols.forEach(([h, color, items], i) => {
    const x = 0.6 + i * 6.1;
    card(s, x, 3.2, 5.9, 3.55, { fill: COL.white });
    T(s, h, { x: x + 0.25, y: 3.35, w: 5.4, h: 0.4, fontSize: 16, bold: true, color });
    T(s, bullets(items, { gap: 8 }), { x: x + 0.25, y: 3.85, w: 5.45, h: 2.8, fontSize: 14 });
  });
}

// ---------- 3. Đóng gói và tái lập
{
  const s = content("KẾT QUẢ 1: ĐÓNG GÓI VÀ TÁI LẬP (06/11)", "Làm sớm Sprint 6: người chấm chạy hệ thống và tái lập kết quả bằng vài lệnh");
  const items = [["Sửa lỗi tái lập", "Chạy lại không lỗi khi lần trước dừng giữa chừng; điểm chấm hỏng được chấm lại."],
    ["Báo lỗi rõ ràng", "Tra cứu Điều không phân biệt hoa thường; chỉ mục thiếu thì báo lệnh nạp lại."],
    ["Docker", "2 dịch vụ API và giao diện; lên trong khoảng 1 phút; API dùng khoảng 1,5 GB RAM."],
    ["Bộ chỉ mục nộp kèm", "73 MB, đủ 4 chỉ mục, đã kiểm giải nén; khỏi nạp lại khoảng 2 giờ CPU."],
    ["README tái lập", "Bảng kết quả ↔ lệnh ↔ file; 7 bảng, 4 hình sinh lại khớp từng byte."],
    ["Thử trên bản sao sạch", "Chạy như người chấm vừa tải về; 339 test đạt sau ngày 06/11."]];
  items.forEach(([h, d], i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.65 + Math.floor(i / 3) * 2.6;
    card(s, x, y, 3.85, 2.35);
    num(s, i + 1, x + 0.2, y + 0.18);
    T(s, h, { x: x + 0.8, y: y + 0.18, w: 2.95, h: 0.48, fontSize: 16, bold: true, color: COL.blue, valign: "middle" });
    T(s, d, { x: x + 0.2, y: y + 0.8, w: 3.45, h: 1.45, fontSize: 14 });
  });
}

// ---------- 4. Báo cáo 6 chương (danh sách chương thay cho biểu đồ của tuần 12)
{
  const s = content("KẾT QUẢ 2: BÁO CÁO ĐỦ 6 CHƯƠNG", "Thêm Tổng quan tài liệu theo đề cương; Chương 3 còn chờ 4 hình minh họa");
  C.ch1.sections[1].table.rows.forEach(([chap, who, status], i) => {
    const y = 1.6 + i * 0.87;
    const done = status.startsWith("Xong");
    card(s, 0.6, y, 7.4, 0.77, { fill: COL.white, line: COL.line });
    const [n, name] = chap.split(". ");
    num(s, n, 0.75, y + 0.15);
    T(s, [{ text: name, options: { bold: true, color: COL.blue, fontSize: 15, breakLine: true } }, { text: who, options: { color: COL.muted, fontSize: 11.5 } }],
      { x: 1.4, y: y + 0.06, w: 4.4, h: 0.65, valign: "middle" });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 5.85, y: y + 0.2, w: 2.0, h: 0.37, rectRadius: 0.18,
      fill: { color: done ? COL.greenBg : COL.warnBg }, line: { color: done ? COL.greenBg : COL.warnBg } });
    T(s, status, { x: 5.85, y: y + 0.2, w: 2.0, h: 0.37, fontSize: 11.5, bold: true, color: done ? COL.green : COL.warn, align: "center", valign: "middle" });
  });
  card(s, 8.3, 1.6, 4.45, 5.2, { fill: COL.white });
  T(s, "Nhận xét", { x: 8.55, y: 1.75, w: 4, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(["Thêm Tổng quan tài liệu theo đề cương; mọi tham chiếu chương, bảng, hình đã dời số và kiểm bằng script.",
    "Đọc lại toàn văn 2 công trình trong nước; sửa mô tả sai trong đề cương.",
    "Chương 6: đối chiếu từng chỉ tiêu; 7 hạn chế ↔ 7 hướng phát triển.",
    "Rà soát độc lập: 4 lỗi nghiêm trọng, 8 lỗi quan trọng (câu chữ chưa khớp số liệu), đã sửa hết."], { gap: 9 }),
  { x: 8.55, y: 2.25, w: 4.0, h: 4.45, fontSize: 13.5 });
}

// ---------- 5. Ghép báo cáo (ảnh: bìa, Tóm tắt, Mục lục của bản hiện tại)
{
  const s = content("KẾT QUẢ 3: GHÉP BÁO CÁO THEO MẪU CỦA KHOA", "Sinh tự động từ Markdown trong vài giây; đã chuyển sang mẫu báo cáo môn Dự án");
  // ảnh 2922×1351: giữ tỷ lệ
  s.addImage({ data: png(REPORT_PAGES), x: 0.6, y: 1.65, w: 7.6, h: 3.51 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.65, w: 7.6, h: 3.51, fill: { color: COL.white, transparency: 100 }, line: { color: COL.line, width: 1 } });
  T(s, "Bìa, Tóm tắt và Mục lục của bản hiện tại.", { x: 0.6, y: 5.2, w: 7.6, h: 0.3, fontSize: 11.5, italic: true, color: COL.muted, align: "center" });
  [["vài giây", "mỗi lần build lại"], ["39", "test cấu trúc file"], ["15", "tài liệu APA 7"]].forEach(([v, l], i) => {
    const x = 0.6 + i * 2.6;
    card(s, x, 5.6, 2.4, 1.2);
    T(s, v, { x, y: 5.65, w: 2.4, h: 0.6, fontSize: 24, bold: true, color: COL.blue, align: "center", valign: "middle" });
    T(s, l, { x, y: 6.25, w: 2.4, h: 0.45, fontSize: 12, align: "center", valign: "middle" });
  });
  card(s, 8.5, 1.6, 4.25, 5.2, { fill: COL.white });
  T(s, "Đã làm", { x: 8.75, y: 1.75, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(["Script sinh file Word từ 6 chương Markdown; chú thích, mục lục, danh mục tự cập nhật",
    "Đổi sang mẫu môn Dự án: bìa mới, bỏ trang xác nhận GV, lề 3,5 / 2 / 3 / 3,5 cm",
    "Sửa lỗi ẩn của khung cũ: danh mục hình rỗng, trích dẫn kiểu IEEE lệch",
    "Tóm tắt, Abstract, 23 từ viết tắt; kiểm tự động trích dẫn ↔ danh mục tài liệu",
    "Rà soát độc lập: không có lỗi nghiêm trọng; lỗi còn lại đã sửa có test"], { gap: 9 }),
  { x: 8.75, y: 2.25, w: 3.85, h: 4.45, fontSize: 13 });
}

// ---------- 6. Sơ đồ và giao diện
{
  const s = content("KẾT QUẢ 4: SƠ ĐỒ VÀ GIAO DIỆN", "Sơ đồ khớp với mã nguồn; giữ giao diện cũ, chỉ vá lỗi hiển thị sai sự thật");
  twoColumns(s, [["1", "Sơ đồ theo mã nguồn",
    ["Use case và sequence", "Vẽ bằng draw.io theo mã nguồn (Hình 4.6, 4.7)."],
    ["Hình 4.1, 4.2 cũ sai", "Ghi giao diện Streamlit, thiếu bước kiểm chứng, có nhánh không tồn tại: đã vẽ lại."],
    ["Kết luận", "Sơ đồ trong báo cáo khớp hệ thống; activity và Hình 3.1–3.4 giao Hùng (hạn 20/11)."]],
  ["2", "Giao diện",
    ["Đánh giá theo Nielsen", "20/40 điểm; 2 lỗi sai sự thật: báo \"Đã kết nối\" khi chạy dự phòng, số Điều ghi cứng sai."],
    ["Làm thử giao diện mới", "Chạy 7 bước cải thiện, có rà soát độc lập; hiệu quả nhìn thấy chưa nhiều."],
    ["Kết luận", "Giữ giao diện cũ, vá 2 lỗi sai sự thật; dành thời gian cho phần nghiên cứu."]]]);
}

// ---------- 7. Sơ đồ kiến trúc vẽ lại
{
  const s = content("KẾT QUẢ 5: SƠ ĐỒ KIẾN TRÚC (HÌNH 4.1)", "Vẽ lại theo mã nguồn; cùng cách vẽ cho đồ thị tác tử, use case, sequence");
  // ảnh 3279×2002: giữ tỷ lệ
  s.addImage({ data: png(ARCH), x: 0.6, y: 1.65, w: 7.6, h: 4.64 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.65, w: 7.6, h: 4.64, fill: { color: COL.white, transparency: 100 }, line: { color: COL.line, width: 1 } });
  T(s, "Hình 4.1 trong báo cáo: 6 khối, nét đứt là dịch vụ bên ngoài hoặc luồng chỉ dùng khi đánh giá.", { x: 0.6, y: 6.37, w: 7.6, h: 0.35, fontSize: 11.5, italic: true, color: COL.muted, align: "center" });
  card(s, 8.5, 1.6, 4.25, 5.2, { fill: COL.white });
  T(s, "Điểm chính", { x: 8.75, y: 1.75, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(["Giao diện NiceGUI gọi API FastAPI; Docker 2 dịch vụ",
    "Tác tử LangGraph 7 nút, ghi số lượt gọi LLM của từng nút",
    "Truy xuất: BM25 + BGE-M3 → lọc hiệu lực → RRF → cross-encoder",
    "Dữ liệu: văn bản gốc → phân tích cấu trúc → tách đoạn → 4 chỉ mục",
    "Khối đánh giá: RQ1–RQ4 sinh bảng số liệu cho báo cáo"], { gap: 9 }),
  { x: 8.75, y: 2.25, w: 3.85, h: 4.45, fontSize: 13 });
}

// ---------- 8. Tiến độ so với kế hoạch Khoa
{
  const s = content("ĐÁNH GIÁ TIẾN ĐỘ SO VỚI KẾ HOẠCH CỦA KHOA", "Đã qua 13/16 tuần (81%); 72/79 hạng mục xong (91%); sớm khoảng 1,5 tuần");
  const X0 = 0.9, X1 = 12.4, Y = 2.3;
  const pos = (week) => X0 + (X1 - X0) * (week - 1) / 16;  // 16 tuần: 15/08 – 04/12
  s.addShape(pres.shapes.LINE, { x: X0, y: Y, w: X1 - X0, h: 0, line: { color: COL.line, width: 6 } });
  s.addShape(pres.shapes.LINE, { x: X0, y: Y, w: pos(13.57) - X0, h: 0, line: { color: COL.sky, width: 6 } });
  // mốc đóng băng 12/11 sát ngày báo cáo 13/11 nên không vẽ riêng (hai chấm chồng nhau)
  [[1, "15/08", "Bắt đầu", COL.blue], [10.43, "22/10", "Giữa kỳ", COL.blue], [13.57, "13/11", "Hôm nay", COL.red],
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
  const s = content("KẾ HOẠCH TỪ NAY ĐẾN 04/12/2026", "Chốt bản nháp → hoàn thiện báo cáo và demo → dự phòng và nộp");
  C.ch3.weeks.forEach((w, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.6, 3.85, 5.2, { fill: COL.white });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.6, w: 3.85, h: 1.05, rectRadius: 0.1, fill: { color: COL.blue }, line: { color: COL.blue } });
    T(s, [{ text: `${w.name} · ${w.dates}`, options: { fontSize: 12, color: COL.circle, breakLine: true } }, { text: w.goal, options: { fontSize: 17, bold: true, color: COL.white } }],
      { x: x + 0.2, y: 1.68, w: 3.5, h: 0.9, valign: "middle" });
    T(s, bullets(w.items, { gap: 9 }), { x: x + 0.2, y: 2.85, w: 3.5, h: 3.85, fontSize: 13.5 });
  });
}

// ---------- 10. Rủi ro (6 khó khăn mới của tuần, ch4.rows[0..5]; lời giải rút gọn cho vừa ô)
{
  const s = content("KHÓ KHĂN, RỦI RO VÀ GIẢI PHÁP", "Rủi ro chính là nhân lực; các vấn đề về mẫu báo cáo đã xử lý xong");
  const short = ["Hùng chưa cập nhật từ 07/11", "Sơ đồ do AI vẽ sai", "Dùng nhầm mẫu báo cáo cũ", "Lỗi ẩn của khung cũ", "Không có Microsoft Word", "Làm lại giao diện"];
  const detail = ["Các thẻ của Hùng chặn việc ghép báo cáo", "Hình 4.1–4.2, activity lệch mã nguồn", "Khác bìa, lề trang, có trang xác nhận GV",
    "Danh mục hình rỗng; trích dẫn IEEE lệch", "Khó kiểm file Word trước khi nộp", "Tốn công, hiệu quả ít, sát mốc đóng băng"];
  // [tình trạng, giải pháp]: tách "đã xử lý" khỏi "giảm thiểu" và "chấp nhận là giới hạn" để người đọc không hiểu là đã hết
  const fix = [["Đang theo dõi", "Đạt làm thay phần đang chặn; việc còn lại có thẻ và hạn rõ (20/11); ~20/11 chưa có thì Đạt làm slide."],
    ["Giảm thiểu", "Vẽ lại Hình 4.1–4.2 theo mã nguồn; activity, Hình 3.x giao Hùng theo danh sách điểm cần sửa."],
    ["Đã xử lý", "Chuyển sang mẫu môn Dự án của Khoa; báo cáo sinh tự động nên chỉ cần build lại."],
    ["Đã xử lý", "Ghép bằng script có test; danh mục tự cập nhật, tài liệu tham khảo theo APA 7."],
    ["Giảm thiểu", "Kiểm cấu trúc file bằng test, xem trước bằng OnlyOffice; bản cuối mở bằng Word."],
    ["Chấp nhận, ghi vào giới hạn", "Hủy làm lại, chỉ vá 2 lỗi sai sự thật; bản làm thử được lưu lại."]];
  const STATUS_COLOR = { "Đã xử lý": COL.green, "Giảm thiểu": COL.sky };
  short.forEach((h, i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.6 + Math.floor(i / 3) * 2.65;
    card(s, x, y, 3.85, 2.45, { fill: COL.white });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: y + 0.15, w: 3.55, h: 1.0, rectRadius: 0.08, fill: { color: COL.warnBg }, line: { color: COL.warnBg } });
    T(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: detail[i], options: { fontSize: 11.5 } }],
      { x: x + 0.3, y: y + 0.18, w: 3.3, h: 0.95, fontSize: 14, color: COL.warn, valign: "middle" });
    const [st, text] = fix[i];
    T(s, [{ text: st, options: { bold: true, color: STATUS_COLOR[st] || COL.warn, breakLine: true } }, { text }],
      { x: x + 0.3, y: y + 1.22, w: 3.3, h: 1.18, fontSize: 12, paraSpaceAfter: 2 });
  });
}

// ---------- 11. Tổng kết
{
  const s = content("TỔNG KẾT", "Sản phẩm và báo cáo đã đủ; tuần tới tập trung rà soát và hoàn thiện");
  [["Đóng gói và tái lập", "Docker 2 dịch vụ; bộ chỉ mục 73 MB; README nối kết quả ↔ lệnh ↔ file."],
    ["Báo cáo 6 chương", "Ghép tự động theo mẫu môn Dự án của Khoa; rà soát độc lập, sửa hết."],
    ["Số liệu không đổi", "Tác tử, prompt, tập kiểm thử giữ nguyên; kết quả RQ1–RQ4 như tuần 12."],
    ["Việc tuần tới", "Đối chiếu quy định trình bày, rubric; rà soát; Hình 3.1–3.4; slide, video."]]
    .forEach(([h, d], i) => {
      const x = 0.6 + (i % 2) * 6.1, y = 1.6 + Math.floor(i / 2) * 1.55;
      card(s, x, y, 5.9, 1.35);
      num(s, i + 1, x + 0.2, y + 0.43);
      T(s, [{ text: h, options: { bold: true, color: COL.blue, fontSize: 15, breakLine: true } }, { text: d, options: { fontSize: 13 } }],
        { x: x + 0.85, y: y + 0.12, w: 4.85, h: 1.1, valign: "middle" });
    });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 4.85, w: 12.0, h: 1.2, rectRadius: 0.1, fill: { color: COL.white }, line: { color: COL.sky, width: 1, dashType: "dash" } });
  T(s, "Từ báo cáo tuần 12, nhóm đã chốt: (1) báo cáo cuối kỳ có 6 chương, thêm Tổng quan tài liệu theo đề cương; (2) giữ giao diện hiện tại, dành thời gian còn lại cho rà soát nội dung và đúng thể thức trình bày của Khoa.",
    { x: 0.85, y: 4.95, w: 11.5, h: 1.0, fontSize: 13, italic: true, valign: "middle" });
  T(s, "Em xin trân trọng cảm ơn Thầy đã lắng nghe.", { x: 0.6, y: 6.25, w: 12.0, h: 0.55, fontSize: 22, bold: true, color: COL.sky, align: "center", valign: "middle" });
}

if (C.notes && C.notes.length !== SLIDES.length) throw new Error(`notes ${C.notes.length} ≠ slides ${SLIDES.length}`);
SLIDES.forEach((s, i) => C.notes && C.notes[i] && s.addNotes(C.notes[i]));
pres.writeFile({ fileName: OUT }).then(() => console.log("saved", OUT));
