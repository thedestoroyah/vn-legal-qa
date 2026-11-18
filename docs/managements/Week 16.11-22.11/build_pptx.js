// Slide báo cáo tuần 14: chép từ tuần 13 (cùng thiết kế), nội dung 16/11 – 22/11/2026 (tính tới 19/11).
// node build_pptx.js <out.pptx> <logo.png> <content.json> <ảnh Bảng 5.4 trong báo cáo.png>
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const [, , OUT, LOGO, CONTENT, TABLE_IMG] = process.argv;
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
  [["Báo cáo đúng quy định", "Đối chiếu với hướng dẫn của Khoa", false], ["Slide bảo vệ 17 slide", "Có lời thuyết trình, khoảng 12 phút", false],
    ["Sprint 6 đang làm", "Còn video, Turnitin, nộp", true]].forEach(([h, d, solid], i) => {
    const x = 8.75 + 0.3 * i, y = 3.0 + 1.05 * i;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.35, h: 0.9, rectRadius: 0.1, fill: { color: solid ? COL.blue : COL.white }, line: { color: COL.sky, width: 1 } });
    T(s, h, { x: x + 0.15, y: y + 0.08, w: 3.1, h: 0.38, fontSize: 14, bold: true, color: solid ? COL.white : COL.blue, valign: "middle" });
    T(s, d, { x: x + 0.15, y: y + 0.45, w: 3.1, h: 0.35, fontSize: 11.5, color: solid ? COL.white : COL.muted, valign: "middle" });
  });
}

// ---------- 2. Tổng quan tuần
{
  const s = content("TỔNG QUAN TUẦN 14", "Tuần đầu của Sprint 6; số liệu tính tới 19/11/2026");
  [["76", "trang báo cáo (nội dung 64)"], ["393", "test tự động đạt"], ["17", "slide bảo vệ có lời nói"], ["35", "hình và bảng trong danh mục"], ["75/79", "hạng mục kế hoạch xong"]]
    .forEach(([v, l], i) => {
      const x = 0.6 + i * 2.43;
      card(s, x, 1.65, 2.23, 1.25);
      T(s, v, { x, y: 1.72, w: 2.23, h: 0.65, fontSize: 30, bold: true, color: COL.blue, align: "center", valign: "middle" });
      T(s, l, { x: x + 0.1, y: 2.38, w: 2.03, h: 0.42, fontSize: 12, color: COL.text, align: "center", valign: "middle" });
    });
  const cols = [["Đã hoàn thành", COL.green, ["Đối chiếu báo cáo với quy định và rubric của Khoa", "Viết lại Chương 3; Hình 3.1–3.4, sơ đồ activity",
    "Bảng cỡ 13, bỏ in đậm, viết lại văn phong; danh mục hình, bảng", "Slide bảo vệ 17 slide; chạy thử Docker"]],
    ["Đang thực hiện", COL.warn, ["Quay video demo 4 kịch bản (Đạt)", "Kiểm tra Turnitin",
      "Cập nhật trường, ký, xuất PDF", "Tập nói theo slide; đóng gói nộp ELIT"]]];
  cols.forEach(([h, color, items], i) => {
    const x = 0.6 + i * 6.1;
    card(s, x, 3.2, 5.9, 3.55, { fill: COL.white });
    T(s, h, { x: x + 0.25, y: 3.35, w: 5.4, h: 0.4, fontSize: 16, bold: true, color });
    T(s, bullets(items, { gap: 8 }), { x: x + 0.25, y: 3.85, w: 5.45, h: 2.8, fontSize: 14 });
  });
}

// ---------- 3. Đối chiếu báo cáo với quy định (bảng 1.1: 7 mục kiểm)
{
  const s = content("KẾT QUẢ 1: ĐỐI CHIẾU BÁO CÁO VỚI QUY ĐỊNH", "16/11: hướng dẫn kèm QĐ 2284, slide lỗi thường gặp, sheet môn học và rubric");
  C.ch1.sections[0].table.rows.forEach(([item, req, status], i) => {
    const y = 1.6 + i * 0.75;
    const done = status.startsWith("Xong");
    card(s, 0.6, y, 8.2, 0.66, { fill: COL.white, line: COL.line });
    num(s, i + 1, 0.72, y + 0.09, 0.46);
    T(s, [{ text: item, options: { bold: true, color: COL.blue, fontSize: 13.5, breakLine: true } }, { text: req, options: { color: COL.muted, fontSize: 10.5 } }],
      { x: 1.3, y: y + 0.03, w: 5.0, h: 0.6, valign: "middle" });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.4, y: y + 0.15, w: 2.3, h: 0.36, rectRadius: 0.18,
      fill: { color: done ? COL.greenBg : COL.warnBg }, line: { color: done ? COL.greenBg : COL.warnBg } });
    T(s, status, { x: 6.4, y: y + 0.15, w: 2.3, h: 0.36, fontSize: 10.5, bold: true, color: done ? COL.green : COL.warn, align: "center", valign: "middle" });
  });
  card(s, 9.1, 1.6, 3.65, 5.2, { fill: COL.white });
  T(s, "Nhận xét", { x: 9.3, y: 1.75, w: 3.3, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(["Tài liệu tham khảo thêm phần A: 5 văn bản quy phạm pháp luật.",
    "Thêm 3 đoạn theo yêu cầu môn: quản lý dự án, ý nghĩa khoa học và thực tiễn, khả năng ứng dụng.",
    "Mọi hình, bảng được nhắc theo số trong bài.",
    "Hồ sơ nộp ELIT cần thư mục source và readme.txt: đã viết readme.txt."], { gap: 8 }),
  { x: 9.3, y: 2.25, w: 3.3, h: 4.45, fontSize: 12.5 });
}

// ---------- 4. Chương 3 và hình minh họa
{
  const s = content("KẾT QUẢ 2: CHƯƠNG 3 VÀ HÌNH MINH HỌA", "16/11: việc của Hùng do Đạt làm thay; đối chiếu từng tham số với mã nguồn");
  const items = [["Bỏ từ cường điệu", "Khoảng 30 từ như \"vượt trội\", \"hoàn hảo\" được thay bằng mô tả đo được."],
    ["Sửa 7 chỗ lệch mã", "IDF của BM25, 2.048 token của BGE-M3, cửa sổ 200/40 từ, định nghĩa ngoài phạm vi, bước sinh lại, reranker 512 token."],
    ["Thêm trích dẫn", "Từ 9 lên 14 trích dẫn, đều có trong danh mục tài liệu tham khảo."],
    ["Hình 3.1–3.4", "Vẽ bằng draw.io, cùng kiểu Hình 4.1–4.2; sinh bằng script nên sửa được."],
    ["Sơ đồ activity", "Sửa 7 điểm lệch so với mã nguồn; đưa vào Chương 4 thành Hình 4.8; bỏ Hình 3.5."],
    ["Chọn công cụ", "Thử công cụ vẽ khác để so với draw.io; giữ draw.io vì bộ hình đồng bộ."]];
  items.forEach(([h, d], i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.65 + Math.floor(i / 3) * 2.6;
    card(s, x, y, 3.85, 2.35);
    num(s, i + 1, x + 0.2, y + 0.18);
    T(s, h, { x: x + 0.8, y: y + 0.18, w: 2.95, h: 0.48, fontSize: 16, bold: true, color: COL.blue, valign: "middle" });
    T(s, d, { x: x + 0.2, y: y + 0.8, w: 3.45, h: 1.45, fontSize: 13 });
  });
}

// ---------- 5. Trình bày và văn phong (ảnh: Bảng 5.4 sau khi sửa)
{
  const s = content("KẾT QUẢ 3: TRÌNH BÀY VÀ VĂN PHONG BÁO CÁO", "18/11: bảng cỡ 13 như thân bài; chỉ tiêu mục được in đậm; viết lại văn phong 6 chương");
  // ảnh 948×381: giữ tỷ lệ
  s.addImage({ data: png(TABLE_IMG), x: 0.6, y: 1.65, w: 7.6, h: 3.05 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.65, w: 7.6, h: 3.05, fill: { color: COL.white, transparency: 100 }, line: { color: COL.line, width: 1 } });
  T(s, "Bảng 5.4 trong báo cáo sau khi sửa: chữ cỡ 13, số liệu không bị bẻ dòng.", { x: 0.6, y: 4.75, w: 7.6, h: 0.3, fontSize: 11.5, italic: true, color: COL.muted, align: "center" });
  [["13 pt", "cỡ chữ trong bảng (trước 11)"], ["0", "chỗ in đậm trong thân bài (trước hơn 200)"], ["0", "đường kẻ ngang chia cắt (trước 9)"]].forEach(([v, l], i) => {
    const x = 0.6 + i * 2.6;
    card(s, x, 5.3, 2.4, 1.5);
    T(s, v, { x, y: 5.35, w: 2.4, h: 0.65, fontSize: 26, bold: true, color: COL.blue, align: "center", valign: "middle" });
    T(s, l, { x: x + 0.1, y: 6.0, w: 2.2, h: 0.7, fontSize: 11.5, align: "center", valign: "middle" });
  });
  card(s, 8.5, 1.6, 4.25, 5.2, { fill: COL.white });
  T(s, "Đã làm", { x: 8.75, y: 1.75, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(["Chia lại bề rộng cột: số liệu và tên hàm như lookup_article không bị bẻ",
    "Bỏ in đậm trong thân bài và trong bảng, chỉ giữ ở tiêu mục có số",
    "Viết lại văn phong cả 6 chương: bỏ nhãn in đậm, mũi tên, câu dịch sát tiếng Anh",
    "Đối chiếu từng chương với bản cũ: số liệu giữ nguyên",
    "Báo cáo 76 trang, build không cảnh báo; bản cũ được lưu lại"], { gap: 9 }),
  { x: 8.75, y: 2.25, w: 3.85, h: 4.45, fontSize: 13 });
}

// ---------- 6. Công cụ ghép báo cáo
{
  const s = content("KẾT QUẢ 4: SỬA CÔNG CỤ GHÉP BÁO CÁO", "16/11 – 19/11: danh mục hình, bảng không còn phụ thuộc vào việc OnlyOffice cập nhật trường");
  const items = [["Mất tiêu đề mục 5.6", "Lỗi cũ: chú thích cuối dòng bị xóa kèm dấu xuống dòng; đã sửa, có test."],
    ["Danh mục bảng trống", "Mẫu của Khoa ghi \"Bảng\" ở dạng Unicode tổ hợp nên không khớp."],
    ["Trường số sai", "OnlyOffice tính sai trường số của chú thích; chú thích nay là chữ ghi sẵn."],
    ["Danh mục tĩnh", "19/11: 16 hình, 19 bảng; mỗi dòng có số trang và trường PAGEREF."],
    ["Số trang đúng", "Số trang lấy từ bản render, build lại tới khi ổn định."],
    ["Kiểm thử", "393 test đạt, thêm 12 test cho script ghép báo cáo."]];
  items.forEach(([h, d], i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.65 + Math.floor(i / 3) * 2.6;
    card(s, x, y, 3.85, 2.35);
    num(s, i + 1, x + 0.2, y + 0.18);
    T(s, h, { x: x + 0.8, y: y + 0.18, w: 2.95, h: 0.48, fontSize: 16, bold: true, color: COL.blue, valign: "middle" });
    T(s, d, { x: x + 0.2, y: y + 0.8, w: 3.45, h: 1.45, fontSize: 14 });
  });
}

// ---------- 7. Slide bảo vệ và Docker
{
  const s = content("KẾT QUẢ 5: SLIDE BẢO VỆ VÀ DOCKER", "Slide bảo vệ đã xong; Docker chạy được trên máy Đạt");
  twoColumns(s, [["1", "Slide bảo vệ",
    ["17 slide dựng bằng script", "Theo dàn ý thẻ H24, cùng thiết kế slide báo cáo tuần."],
    ["Lời thuyết trình", "Mỗi slide có lời nói; khoảng 12 phút, giới hạn 15 phút gồm demo; số lấy từ Chương 5, 6."],
    ["Kết luận", "Đạt duyệt; video demo là phương án dự phòng khi demo trực tiếp lỗi."]],
  ["2", "Docker và giao diện",
    ["Chạy thử Docker", "docker compose up --build trên máy Đạt; giao diện kết nối API."],
    ["Sửa giao diện", "Lỗi 500 do chỉ mục không còn gợi ý \"Thử lại\" vô ích."],
    ["Kết luận", "Chưa kiểm trên máy sạch, Windows; readme.txt ghi lần đầu tải khoảng 7 GB mô hình."]]]);
}

// ---------- 8. Tiến độ so với kế hoạch Khoa
{
  const s = content("ĐÁNH GIÁ TIẾN ĐỘ SO VỚI KẾ HOẠCH CỦA KHOA", "Đã qua 86% thời gian (96/112 ngày); 75/79 hạng mục xong (95%); sớm khoảng 1 tuần");
  const X0 = 0.9, X1 = 12.4, Y = 2.3;
  const pos = (week) => X0 + (X1 - X0) * (week - 1) / 16;  // 16 tuần: 15/08 – 04/12
  s.addShape(pres.shapes.LINE, { x: X0, y: Y, w: X1 - X0, h: 0, line: { color: COL.line, width: 6 } });
  s.addShape(pres.shapes.LINE, { x: X0, y: Y, w: pos(14.43) - X0, h: 0, line: { color: COL.sky, width: 6 } });
  // vị trí tuần = 1 + (số ngày kể từ 15/08 − 2)/7, cùng thang với báo cáo tuần 13
  [[1, "15/08", "Bắt đầu", COL.blue], [10.43, "22/10", "Giữa kỳ", COL.blue], [14.43, "19/11", "Hôm nay", COL.red],
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
  { x: 0.6, y: 3.2, w: 8.0, colW: [0.95, 3.75, 3.3], fontFace: FONT, fontSize: 10.5, color: COL.text, border: { type: "solid", pt: 0.75, color: COL.line },
    fill: { color: COL.white }, rowH: 0.33, valign: "middle", margin: 0.04 });
  card(s, 8.85, 3.2, 3.9, 3.6, { fill: COL.white });
  T(s, "Tự đánh giá", { x: 9.05, y: 3.33, w: 3.55, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, C.ch2.verdict.map(([l, t], i) => [{ text: l + ": ", options: { bold: true, color: [COL.blue, COL.green, COL.warn][i] } },
    { text: t, options: { breakLine: i < 2, paraSpaceAfter: 8 } }]).flat(), { x: 9.05, y: 3.8, w: 3.55, h: 2.9, fontSize: 12 });
}

// ---------- 9. Kế hoạch
{
  const s = content("KẾ HOẠCH TỪ NAY ĐẾN 04/12/2026", "Chốt báo cáo và video → hoàn thiện báo cáo → đóng gói và nộp");
  C.ch3.weeks.forEach((w, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.6, 3.85, 5.2, { fill: COL.white });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.6, w: 3.85, h: 1.05, rectRadius: 0.1, fill: { color: COL.blue }, line: { color: COL.blue } });
    T(s, [{ text: `${w.name} · ${w.dates}`, options: { fontSize: 12, color: COL.circle, breakLine: true } }, { text: w.goal, options: { fontSize: 17, bold: true, color: COL.white } }],
      { x: x + 0.2, y: 1.68, w: 3.5, h: 0.9, valign: "middle" });
    T(s, bullets(w.items, { gap: 9 }), { x: x + 0.2, y: 2.85, w: 3.5, h: 3.85, fontSize: 13.5 });
  });
}

// ---------- 10. Rủi ro (6 khó khăn tiêu biểu: ch4.rows[0..5]; lời giải rút gọn cho vừa ô)
{
  const s = content("KHÓ KHĂN, RỦI RO VÀ GIẢI PHÁP", "Ba vấn đề của tuần đã xử lý; còn theo dõi Docker, Word và Gemini");
  const short = ["Danh mục hình, bảng trống", "Chưa đúng quy định trình bày", "Chương 3 lệch mã nguồn", "Không có Microsoft Word", "Docker chưa kiểm máy sạch", "Gemini quá tải (503)"];
  const detail = ["OnlyOffice tính sai trường, F9 không dựng", "Bảng cỡ 11, in đậm nhiều, văn dịch sát", "Văn cường điệu, 7 chỗ lệch tham số",
    "Khó kiểm trang trắng, ngắt trang", "Chưa kiểm trên Windows", "Ảnh hưởng quay video demo"];
  // [tình trạng, giải pháp]: tách "đã xử lý" khỏi "giảm thiểu" và "chấp nhận là giới hạn" để người đọc không hiểu là đã hết
  const fix = [["Đã xử lý", "Danh mục tĩnh có số trang và trường PAGEREF; có test."],
    ["Đã xử lý", "Bảng cỡ 13, chỉ tiêu mục in đậm, viết lại văn phong; số liệu giữ nguyên."],
    ["Đã xử lý", "Viết lại, đối chiếu từng tham số với mã nguồn, thêm trích dẫn."],
    ["Giảm thiểu", "Kiểm cấu trúc bằng test, xem trước bằng OnlyOffice; kiểm trang trắng trên bản PDF cuối."],
    ["Đang theo dõi", "Chạy tốt trên máy Đạt; readme.txt ghi dung lượng và thời gian tải."],
    ["Giảm thiểu", "Lỗi phía Google; quay video khi mô hình ổn định, kiểm /health trước."]];
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
  const s = content("TỔNG KẾT", "Báo cáo và slide đã xong về nội dung; tuần tới quay video, kiểm Turnitin và nộp");
  [["Báo cáo đúng quy định", "Đã đối chiếu với hướng dẫn, rubric của Khoa; bảng cỡ 13, văn phong viết lại."],
    ["Chương 3 và hình", "Viết lại theo mã nguồn; Hình 3.1–3.4, sơ đồ activity xong trước hạn 20/11."],
    ["Số liệu không đổi", "Tác tử, prompt, tập kiểm thử giữ nguyên; kết quả RQ1–RQ4 như tuần 12."],
    ["Việc tuần tới", "Video demo, Turnitin, ký, xuất PDF, đóng gói nộp ELIT."]]
    .forEach(([h, d], i) => {
      const x = 0.6 + (i % 2) * 6.1, y = 1.6 + Math.floor(i / 2) * 1.55;
      card(s, x, y, 5.9, 1.35);
      num(s, i + 1, x + 0.2, y + 0.43);
      T(s, [{ text: h, options: { bold: true, color: COL.blue, fontSize: 15, breakLine: true } }, { text: d, options: { fontSize: 13 } }],
        { x: x + 0.85, y: y + 0.12, w: 4.85, h: 1.1, valign: "middle" });
    });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 4.85, w: 12.0, h: 1.2, rectRadius: 0.1, fill: { color: COL.white }, line: { color: COL.sky, width: 1, dashType: "dash" } });
  T(s, "Từ 16/11, Đạt nhận hết việc còn lại của Hùng (Hùng không phản hồi từ 07/11): slide bảo vệ và Hình 3.x đã xong, video demo Đạt tự quay.",
    { x: 0.85, y: 4.95, w: 11.5, h: 1.0, fontSize: 13, italic: true, valign: "middle" });
  T(s, "Em xin trân trọng cảm ơn Thầy đã lắng nghe.", { x: 0.6, y: 6.25, w: 12.0, h: 0.55, fontSize: 22, bold: true, color: COL.sky, align: "center", valign: "middle" });
}

if (C.notes && C.notes.length !== SLIDES.length) throw new Error(`notes ${C.notes.length} ≠ slides ${SLIDES.length}`);
SLIDES.forEach((s, i) => C.notes && C.notes[i] && s.addNotes(C.notes[i]));
pres.writeFile({ fileName: OUT }).then(() => console.log("saved", OUT));
