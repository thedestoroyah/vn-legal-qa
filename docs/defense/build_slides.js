// Slide bảo vệ (H24): 17 slide, cùng thiết kế slide báo cáo tuần; mọi con số lấy từ Chương 5, 6 của báo cáo.
// Chạy từ gốc repo (cần pptxgenjs@3.12.0, ví dụ NODE_PATH=<thư mục>/node_modules):
//   node docs/defense/build_slides.js "docs/defense/Slide bảo vệ - ĐA127.pptx"
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const OUT = process.argv[2] || path.join(__dirname, "Slide bảo vệ - ĐA127.pptx");
const png = (rel) => "image/png;base64," + fs.readFileSync(path.join(ROOT, rel)).toString("base64");
const LOGO = png("docs/managements/tools/logo.png");

const COL = { blue: "2C5EAD", sky: "1591DC", card: "EAF4FC", line: "BFDBFE", circle: "C4E2F5", text: "1F2937",
  muted: "6B7280", warnBg: "FEF3C7", warn: "B45309", red: "DC2626", redBg: "FEE2E2", green: "16A34A", greenBg: "DCFCE7", white: "FFFFFF" };
const FONT = "Arial";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Phạm Huỳnh Quốc Đạt, Hoàng Sinh Hùng";
pres.title = "Bảo vệ Dự án CNTT — ĐA127";
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: COL.white },
  objects: [
    { image: { data: LOGO, x: 10.5, y: 0.18, w: 2.68, h: 1.08 } },
    { text: { text: "Hệ thống hỏi đáp pháp luật Việt Nam dựa trên Agentic-RAG — ĐA127", options: { x: 0.25, y: 7.05, w: 8.5, h: 0.3, fontFace: FONT, fontSize: 10.5, color: COL.sky, margin: 0 } } },
    { rect: { x: 12.45, y: 7.0, w: 0.6, h: 0.32, fill: { color: COL.circle } } },
  ],
  slideNumber: { x: 12.45, y: 7.0, w: 0.6, h: 0.32, fontFace: FONT, fontSize: 11, color: COL.blue, bold: true, align: "center", valign: "middle" },
});

const T = (s, text, o) => s.addText(text, { fontFace: FONT, color: COL.text, margin: 0, isTextBox: true, valign: "top", ...o });
const box = (s, x, y, w, h, o = {}) => s.addShape(pres.shapes.ROUNDED_RECTANGLE,
  { x, y, w, h, rectRadius: 0.1, fill: { color: o.fill || COL.card }, line: { color: o.line || COL.sky, width: 1, dashType: o.dash ? "dash" : "solid" } });
const num = (s, n, x, y, d = 0.48) => {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: COL.blue }, line: { color: COL.blue } });
  T(s, String(n), { x, y, w: d, h: d, fontSize: 16, bold: true, color: COL.white, align: "center", valign: "middle" });
};
const bullets = (items, gap = 6) => items.map((t, i) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: i < items.length - 1, paraSpaceAfter: gap } }));
const pill = (s, text, x, y, w, color, bg) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.36, rectRadius: 0.18, fill: { color: bg }, line: { color: bg } });
  T(s, text, { x, y, w, h: 0.36, fontSize: 11.5, bold: true, color, align: "center", valign: "middle" });
};
// ảnh có viền mảnh; w, h tính theo tỷ lệ ảnh gốc
const figure = (s, rel, x, y, w, ratio, caption) => {
  const h = w / ratio;
  s.addImage({ data: png(rel), x, y, w, h });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: COL.white, transparency: 100 }, line: { color: COL.line, width: 1 } });
  if (caption) T(s, caption, { x, y: y + h + 0.06, w, h: 0.3, fontSize: 11, italic: true, color: COL.muted, align: "center" });
  return h;
};
const sidePanel = (s, title, items, o = {}) => {
  const x = o.x ?? 8.5, y = o.y ?? 1.6, w = o.w ?? 4.25, h = o.h ?? 5.2;
  box(s, x, y, w, h, { fill: COL.white });
  T(s, title, { x: x + 0.25, y: y + 0.15, w: w - 0.45, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(items, o.gap ?? 9), { x: x + 0.25, y: y + 0.65, w: w - 0.45, h: h - 0.8, fontSize: o.size ?? 13.5 });
};
const NOTES = [];
function slide(title, sub, note) {
  const s = pres.addSlide({ masterName: "CONTENT" });
  T(s, title, { x: 0.6, y: 0.32, w: 9.7, h: 0.6, fontSize: 27, bold: true, color: COL.blue, valign: "middle" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.62, y: 0.98, w: 0.08, h: 0.36, rectRadius: 0.04, fill: { color: COL.blue }, line: { color: COL.blue } });
  T(s, sub, { x: 0.8, y: 0.98, w: 9.5, h: 0.36, fontSize: 14, color: COL.sky, valign: "middle" });
  s.addNotes(note);
  NOTES.push(note);
  return s;
}

// ---------- 1. Trang tiêu đề
{
  const s = pres.addSlide();
  s.background = { color: COL.white };
  s.addShape(pres.shapes.OVAL, { x: -1.0, y: 5.6, w: 3.0, h: 3.0, fill: { color: COL.circle }, line: { color: COL.circle } });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 0.55, w: 12.2, h: 6.3, rectRadius: 0.2, fill: { color: COL.white, transparency: 100 }, line: { color: COL.sky, width: 1.25 } });
  s.addImage({ data: LOGO, x: 10.13, y: 0.61, w: 2.68, h: 1.08 });
  T(s, "PHÁT TRIỂN HỆ THỐNG HỎI ĐÁP PHÁP LUẬT VIỆT NAM DỰA TRÊN AGENTIC-RAG VỚI TRUY XUẤT CĂN CỨ THEO HIỆU LỰC VÀ KIỂM CHỨNG TRÍCH DẪN",
    { x: 0.9, y: 0.75, w: 9.0, h: 1.75, fontSize: 21, bold: true, valign: "middle" });
  T(s, "Developing a Vietnamese Legal Question Answering System Based on Agentic-RAG with Temporally-Aware Legal Retrieval and Citation Verification",
    { x: 0.9, y: 2.55, w: 8.4, h: 0.62, fontSize: 12, italic: true, color: COL.sky });
  [["RAG", 0.8, false], ["LangGraph", 1.4, false], ["Hybrid Retrieval", 1.85, false], ["Temporal Validity", 1.95, true]]
    .reduce((x, [label, w, solid]) => {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.27, w, h: 0.34, rectRadius: 0.17, fill: { color: solid ? COL.blue : COL.card }, line: { color: solid ? COL.blue : COL.card } });
      T(s, label, { x, y: 3.27, w, h: 0.34, fontSize: 11, bold: true, color: solid ? COL.white : COL.blue, align: "center", valign: "middle" });
      return x + w + 0.1;
    }, 0.95);
  T(s, [
    { text: "Bảo vệ Dự án Công nghệ thông tin (504091)", options: { bold: true, breakLine: true } },
    { text: "Trường Đại học Tôn Đức Thắng | Khoa Công nghệ Thông tin", options: { breakLine: true } },
    { text: "Mã đề tài: ĐA127", options: { breakLine: true } },
    { text: "Sinh viên: Phạm Huỳnh Quốc Đạt (52300098) – Hoàng Sinh Hùng (52300106)", options: { breakLine: true } },
    { text: "Giảng viên hướng dẫn: PGS.TS. Lê Anh Cường" },
  ], { x: 0.95, y: 4.1, w: 7.6, h: 1.7, fontSize: 13, color: COL.blue, paraSpaceAfter: 3 });
  [["5 văn bản luật", "có Bộ luật Lao động 2012 đã hết hiệu lực", false], ["209 câu kiểm thử", "có tập giữ riêng 30 câu", false],
    ["4 câu hỏi nghiên cứu", "truy xuất · phân đoạn · tác tử · hiệu lực", true]].forEach(([h, d, solid], i) => {
    const x = 8.75 + 0.3 * i, y = 3.0 + 1.05 * i;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.35, h: 0.9, rectRadius: 0.1, fill: { color: solid ? COL.blue : COL.white }, line: { color: COL.sky, width: 1 } });
    T(s, h, { x: x + 0.15, y: y + 0.08, w: 3.1, h: 0.38, fontSize: 14, bold: true, color: solid ? COL.white : COL.blue, valign: "middle" });
    T(s, d, { x: x + 0.15, y: y + 0.45, w: 3.1, h: 0.35, fontSize: 11.5, color: solid ? COL.white : COL.muted, valign: "middle" });
  });
  const note = "Kính chào quý Thầy Cô. Chúng em là Phạm Huỳnh Quốc Đạt và Hoàng Sinh Hùng, dưới sự hướng dẫn của PGS.TS. Lê Anh Cường. "
    + "Đề tài của chúng em là hệ thống hỏi đáp pháp luật tiếng Việt theo hướng Agentic-RAG, với hai điểm chính: truy xuất căn cứ theo hiệu lực tại thời điểm xảy ra sự việc, và kiểm chứng trích dẫn trước khi trả lời. "
    + "";
  s.addNotes(note);
  NOTES.push(note);
}

// ---------- 2. Vấn đề: LLM và hiệu lực theo thời gian
{
  const s = slide("VẤN ĐỀ", "Mô hình ngôn ngữ trả lời trôi chảy nhưng dễ trích sai căn cứ, sai phiên bản luật",
    "Mô hình ngôn ngữ lớn trả lời câu hỏi pháp luật trôi chảy, nhưng có thể bịa căn cứ hoặc trích điều luật không liên quan. "
    + "Pháp luật còn có một đặc thù: hiệu lực theo thời gian. Bộ luật Lao động 2012 có hiệu lực tới hết năm 2020, sau đó bị thay thế bởi Bộ luật Lao động 2019. "
    + "Ví dụ, nếu năm 2019 một người lao động làm hợp đồng xác định thời hạn muốn nghỉ việc, thì phải áp dụng Điều 37 của luật 2012, tức là cần có lý do luật định; còn theo Điều 35 luật 2019, chỉ cần báo trước. "
    + "Hệ thống chỉ có văn bản hiện hành sẽ trả lời sai cho sự việc trong quá khứ.");
  box(s, 0.6, 1.6, 5.6, 5.2, { fill: COL.white });
  T(s, "Hỏi đáp pháp luật bằng LLM", { x: 0.85, y: 1.75, w: 5.1, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(["Nhu cầu tra cứu lớn; văn bản dài, nhiều thuật ngữ", "LLM có thể bịa căn cứ (ảo giác) hoặc trích điều luật không hỗ trợ nội dung trả lời",
    "Cùng một vấn đề, mỗi thời điểm có thể do một văn bản khác điều chỉnh", "Hệ thống chỉ có văn bản hiện hành sẽ trả lời sai cho sự việc trong quá khứ"], 12),
  { x: 0.85, y: 2.3, w: 5.15, h: 4.3, fontSize: 15 });
  // dòng thời gian hai phiên bản Bộ luật Lao động
  T(s, "Bộ luật Lao động: hai phiên bản", { x: 6.5, y: 1.65, w: 6.2, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.5, y: 2.2, w: 3.6, h: 0.75, rectRadius: 0.08, fill: { color: COL.card }, line: { color: COL.sky } });
  T(s, [{ text: "BLLĐ 2012", options: { bold: true, color: COL.blue, breakLine: true } }, { text: "01/05/2013 – 31/12/2020", options: { fontSize: 11.5, color: COL.muted } }],
    { x: 6.65, y: 2.25, w: 3.4, h: 0.65, fontSize: 14, valign: "middle" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 10.15, y: 2.2, w: 2.6, h: 0.75, rectRadius: 0.08, fill: { color: COL.blue }, line: { color: COL.blue } });
  T(s, [{ text: "BLLĐ 2019", options: { bold: true, breakLine: true } }, { text: "từ 01/01/2021", options: { fontSize: 11.5 } }],
    { x: 10.3, y: 2.25, w: 2.4, h: 0.65, fontSize: 14, color: COL.white, valign: "middle" });
  box(s, 6.5, 3.2, 6.25, 3.6, { fill: COL.white });
  T(s, [{ text: "“Năm 2019, tôi làm hợp đồng xác định thời hạn, muốn nghỉ việc chỉ báo trước 30 ngày có được không?”", options: { italic: true, breakLine: true, paraSpaceAfter: 10 } },
    { text: "Đúng: ", options: { bold: true, color: COL.green } }, { text: "BLLĐ 2012 Điều 37: phải có một trong các lý do luật định.", options: { breakLine: true, paraSpaceAfter: 8 } },
    { text: "Sai phiên bản: ", options: { bold: true, color: COL.red } }, { text: "BLLĐ 2019 Điều 35: chỉ cần báo trước. Văn bản này chưa có hiệu lực năm 2019." }],
  { x: 6.75, y: 3.4, w: 5.8, h: 3.25, fontSize: 14 });
}

// ---------- 3. Khoảng trống nghiên cứu
{
  const s = slide("CÁC NGHIÊN CỨU LIÊN QUAN CÒN THIẾU GÌ", "Khảo sát Chương 2: bốn vấn đề chưa được giải quyết đầy đủ",
    "Qua khảo sát ở Chương 2, chúng em thấy bốn vấn đề còn bỏ ngỏ. "
    + "Thứ nhất, các hệ thống tiếng Việt gần nhất không chọn phiên bản văn bản theo thời điểm sự việc. "
    + "Thứ hai, hệ thống Agentic-RAG được đánh giá ở mức tổng thể, không biết thành phần nào đóng góp bao nhiêu. "
    + "Thứ ba, trích dẫn chưa được kiểm xem có hỗ trợ nội dung trả lời không. Thứ tư, khi kho có hai phiên bản của một bộ luật, nhầm văn bản chính là trích sai phiên bản.");
  [["Chưa xét hiệu lực theo thời gian", "Hệ thống tiếng Việt không chọn phiên bản theo thời điểm sự việc; Pham và cộng sự (2025) loại bỏ văn bản đã bị thay thế."],
    ["Đánh giá tác tử ở mức tổng thể", "Không tách đóng góp và chi phí của định tuyến, đánh giá bằng chứng, kiểm chứng trích dẫn."],
    ["Trích dẫn chưa được kiểm chứng", "ALCE (Gao và cộng sự, 2023): LLM hay sinh trích dẫn không hỗ trợ; công trình trong nước chưa đo điều này."],
    ["Nhầm văn bản (DRM)", "Reuter và cộng sự (2025); nặng hơn khi kho có hai phiên bản của cùng một bộ luật."]].forEach(([h, d], i) => {
    const x = 0.6 + (i % 2) * 6.1, y = 1.6 + Math.floor(i / 2) * 2.65;
    box(s, x, y, 5.9, 2.45);
    num(s, i + 1, x + 0.25, y + 0.25);
    T(s, h, { x: x + 0.9, y: y + 0.25, w: 4.8, h: 0.48, fontSize: 17, bold: true, color: COL.blue, valign: "middle" });
    T(s, d, { x: x + 0.3, y: y + 0.95, w: 5.35, h: 1.35, fontSize: 14.5 });
  });
}

// ---------- 4. Mục tiêu và câu hỏi nghiên cứu
{
  const s = slide("MỤC TIÊU VÀ CÂU HỎI NGHIÊN CỨU", "Xây dựng hệ thống và đo riêng từng lựa chọn thiết kế",
    "Mục tiêu là xây dựng hệ thống hỏi đáp có trích dẫn tới từng Khoản, chọn đúng phiên bản luật theo thời điểm sự việc, và đo riêng từng lựa chọn thiết kế qua 4 câu hỏi nghiên cứu. "
    + "RQ1 so sánh bốn cách truy xuất. RQ2 so sánh bốn cách phân đoạn văn bản. RQ3 là nghiên cứu lược bỏ trên 5 cấu hình của tác tử. RQ4 so sánh ba chính sách lọc theo hiệu lực. "
    + "Ba chỉ tiêu định lượng được đặt trước như trên slide.");
  [["RQ1", "Truy xuất", "BM25 · Dense · Hybrid RRF · Hybrid + rerank"], ["RQ2", "Phân đoạn", "Cố định 200 từ · Điều · Khoản · Khoản + tiêu đề"],
    ["RQ3", "Tác tử", "baseline · full · no_router · no_grading · no_verify"], ["RQ4", "Hiệu lực", "event (ngày sự việc) · current · any"]].forEach(([k, h, d], i) => {
    const x = 0.6 + i * 3.05;
    box(s, x, 1.6, 2.85, 3.1, { fill: COL.white });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.6, w: 2.85, h: 1.0, rectRadius: 0.1, fill: { color: COL.blue }, line: { color: COL.blue } });
    T(s, [{ text: k, options: { fontSize: 13, color: COL.circle, breakLine: true } }, { text: h, options: { fontSize: 19, bold: true, color: COL.white } }],
      { x: x + 0.2, y: 1.66, w: 2.5, h: 0.88, valign: "middle" });
    T(s, d, { x: x + 0.2, y: 2.8, w: 2.5, h: 1.75, fontSize: 14 });
  });
  T(s, "Chỉ tiêu đặt trước", { x: 0.6, y: 4.95, w: 6, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  [["Hit@5", "≥ 0,80"], ["Recall@10", "≥ 0,75"], ["Citation Precision", "≥ 0,85"]].forEach(([k, v], i) => {
    const x = 0.6 + i * 4.1;
    box(s, x, 5.45, 3.85, 1.3);
    T(s, v, { x, y: 5.5, w: 3.85, h: 0.7, fontSize: 28, bold: true, color: COL.blue, align: "center", valign: "middle" });
    T(s, k, { x, y: 6.2, w: 3.85, h: 0.45, fontSize: 13.5, align: "center", valign: "middle" });
  });
}

// ---------- 5. Dữ liệu
{
  const s = slide("DỮ LIỆU: 5 VĂN BẢN LUẬT", "Bóc tách thành cây Chương → Mục → Điều → Khoản → Điểm; mỗi đoạn mang ngày hiệu lực",
    "Kho gồm 5 văn bản tải từ Cơ sở dữ liệu quốc gia về văn bản pháp luật, trong đó Bộ luật Lao động 2012 đã hết hiệu lực được giữ lại có chủ đích để kiểm tra việc chọn phiên bản. "
    + "Văn bản được phân tích thành cây Chương, Điều, Khoản, Điểm. "
    + "Mỗi đoạn mang ngày có hiệu lực và ngày hết hiệu lực; tổng cộng 1.693 Điều và 4.853 đoạn cấp Khoản.");
  const rows = [["BLDS 2015", "91/2015/QH13", "từ 01/01/2017", "689", "1.673"], ["BLLĐ 2012", "10/2012/QH13", "01/05/2013 – 31/12/2020", "242", "686"],
    ["BLLĐ 2019", "45/2019/QH14", "từ 01/01/2021", "220", "687"], ["LDN 2020", "59/2020/QH14", "từ 01/01/2021", "218", "923"],
    ["LTM 2005", "36/2005/QH11", "từ 01/01/2006", "324", "884"], ["Tổng", "", "", "1.693", "4.853"]];
  s.addTable([["Văn bản", "Số hiệu", "Hiệu lực", "Số Điều", "Đoạn cấp Khoản"].map((h) => ({ text: h, options: { bold: true, color: COL.white, fill: { color: COL.blue } } })),
    ...rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: i === 5, color: i === 1 && j === 2 ? COL.red : COL.text, align: j >= 3 ? "right" : "left" } })))],
  { x: 0.6, y: 1.65, w: 7.6, colW: [1.35, 1.65, 2.4, 0.95, 1.25], fontFace: FONT, fontSize: 13, border: { type: "solid", pt: 0.75, color: COL.line },
    fill: { color: COL.white }, rowH: 0.45, valign: "middle", margin: 0.06 });
  T(s, "Nguồn: vbpl.vn; văn bản gốc khi ban hành, chưa hợp nhất các lần sửa đổi.", { x: 0.6, y: 4.95, w: 7.6, h: 0.3, fontSize: 11.5, italic: true, color: COL.muted });
  sidePanel(s, "Tiền xử lý và phân đoạn", ["Văn bản .doc → Markdown (MinerU) → JSON theo cây Phần → Điểm", "Đối chiếu số Điều với mục lục; kiểm ngẫu nhiên 10 Điều mỗi văn bản",
    "Mỗi đoạn mang effective_date, expiry_date; có hiệu lực tại ngày d khi effective_date ≤ d < expiry_date",
    "4 chỉ mục: Khoản + tiêu đề (mặc định), Khoản, Điều, cố định 200 từ"]);
}

// ---------- 6. Tập kiểm thử
{
  const s = slide("TẬP KIỂM THỬ: 209 CÂU TỪ BA NGUỒN", "Kết quả luôn báo cáo tách theo nguồn; tập giữ riêng soạn sau khi đã cố định prompt",
    "Tập kiểm thử có 209 câu từ ba nguồn: 77 câu thực tế của bộ Zalo AI, 65 câu tổng hợp sinh từ văn bản và đã kiểm tay, 67 câu nhóm tự soạn gồm câu tình huống, câu có mốc thời gian, câu tra cứu trực tiếp và câu ngoài phạm vi. "
    + "Điểm quan trọng là tập giữ riêng 30 câu: chúng em soạn và chốt trước khi chạy hệ thống, sau khi prompt đã cố định, để giảm nguy cơ chỉnh prompt theo tập kiểm thử. "
    + "Chỉ số chính là Citation Precision, Citation Recall và tỷ lệ trích đúng phiên bản.");
  [["77", "Zalo AI 2021", "Câu hỏi thực tế của người dân, lọc theo 5 văn bản; căn cứ chuẩn cấp Điều"],
    ["65", "Tổng hợp", "Sinh bằng LLM từ văn bản; kiểm tay 20 câu, đạt 20/20"],
    ["67", "Tự soạn", "15 tình huống · 32 có mốc thời gian · 15 tra cứu trực tiếp · 5 ngoài phạm vi"]].forEach(([n, h, d], i) => {
    const x = 0.6 + i * 2.65;
    box(s, x, 1.6, 2.45, 3.2);
    T(s, n, { x, y: 1.7, w: 2.45, h: 0.8, fontSize: 34, bold: true, color: COL.blue, align: "center", valign: "middle" });
    T(s, h, { x: x + 0.15, y: 2.5, w: 2.15, h: 0.4, fontSize: 15, bold: true, align: "center" });
    T(s, d, { x: x + 0.15, y: 2.95, w: 2.15, h: 1.75, fontSize: 12.5, align: "center" });
  });
  box(s, 0.6, 5.0, 7.75, 1.8, { fill: COL.greenBg, line: COL.green });
  T(s, [{ text: "Tập giữ riêng 30 câu (M_038–M_067)", options: { bold: true, color: COL.green, breakLine: true } },
    { text: "20 câu có mốc thời gian theo 10 cặp quy định khác nhau giữa BLLĐ 2012 và 2019, 10 câu tra cứu trực tiếp. Soạn và chốt giả thuyết trước khi chạy, sau khi prompt đã cố định." }],
  { x: 0.85, y: 5.12, w: 7.3, h: 1.6, fontSize: 13.5, valign: "middle" });
  sidePanel(s, "Chỉ số", ["Truy xuất: Hit@5, Recall@10, MRR@10 (cấp Điều); DRM@5 cho nhầm văn bản",
    "Trích dẫn: Citation Precision, Citation Recall", "Đúng phiên bản (32 câu có mốc thời gian)",
    "Faithfulness, Correctness: bộ chấm gpt-oss-120b (khác nhà cung cấp với tác tử), chỉ số bổ trợ",
    "So sánh ghép cặp theo câu, bootstrap 95%"], { x: 8.6, w: 4.15, size: 13 });
}

// ---------- 7. Kiến trúc
{
  const s = slide("KIẾN TRÚC HỆ THỐNG", "Bốn tầng chạy trên CPU; chỉ các lượt gọi mô hình ngôn ngữ đi ra ngoài",
    "Hệ thống có bốn tầng. Tầng dữ liệu là các đoạn luật và chỉ mục vector ChromaDB. Tầng truy xuất kết hợp BM25 và BGE-M3, lọc theo hiệu lực, hợp nhất bằng RRF rồi xếp hạng lại bằng cross-encoder. "
    + "Tầng tác tử là đồ thị LangGraph. Tầng giao tiếp gồm API FastAPI và giao diện web NiceGUI. "
    + "Embedding và reranker chạy cục bộ trên CPU; mô hình ngôn ngữ là Gemini 3.1 Flash Lite qua gói miễn phí.");
  figure(s, "assets/diagrams/architecture.png", 0.6, 1.6, 7.7, 1.638, "Hình 4.1 trong báo cáo");
  sidePanel(s, "Thành phần", ["Truy xuất: BM25 + BGE-M3, lọc hiệu lực, RRF (k = 60), cross-encoder bge-reranker-v2-m3 → 5 đoạn",
    "Tác tử LangGraph 7 nút, ghi lại từng bước (trace)", "LLM: gemini-3.1-flash-lite, có bộ đệm trên đĩa",
    "API FastAPI, giao diện NiceGUI; Docker Compose 2 dịch vụ"]);
}

// ---------- 8. Tác tử
{
  const s = slide("TÁC TỬ AGENTIC-RAG", "Đồ thị LangGraph 7 nút; cùng một đồ thị phục vụ 5 cấu hình thí nghiệm",
    "Đây là đồ thị của tác tử. Nút route phân loại câu hỏi và trích ngày sự việc. Câu tra cứu trực tiếp đi tới lookup_article để lấy thẳng toàn văn Điều. Câu tình huống đi qua retrieve, rồi grade đánh giá bằng chứng đã đủ chưa; chưa đủ thì viết lại truy vấn, tối đa hai lần. "
    + "Generate sinh câu trả lời có gắn mã Khoản, verify kiểm chứng trích dẫn. Ngoài phạm vi hoặc không đủ căn cứ thì refuse từ chối kèm lý do. "
    + "Ba cờ bật tắt router, grade và verify tạo ra 5 cấu hình cho RQ3.");
  figure(s, "assets/diagrams/agent_graph.png", 0.6, 1.6, 7.7, 1.786, "Hình 4.2 trong báo cáo");
  sidePanel(s, "Các bước", ["route: loại câu, ngày sự việc, Điều được nêu", "lookup_article: lấy thẳng toàn văn Điều",
    "retrieve → grade: chưa đủ thì viết lại truy vấn (≤ 2 lần)", "generate: trả lời kèm mã [BLLD2019_Dieu20_Khoan1]",
    "verify: kiểm chứng trích dẫn hai lớp", "refuse: ngoài phạm vi, không đủ căn cứ", "Khoảng 4 lượt LLM mỗi câu tình huống"], { gap: 7, size: 13 });
}

// ---------- 9. Hai cơ chế chính
{
  const s = slide("HAI CƠ CHẾ CHÍNH", "Lọc văn bản theo ngày sự việc và kiểm chứng trích dẫn hai lớp",
    "Cơ chế thứ nhất là truy xuất theo hiệu lực: router trích ngày sự việc từ câu hỏi, và bộ truy xuất chỉ lấy văn bản có hiệu lực tại ngày đó. Để so sánh, RQ4 có hai chính sách đối chứng: chỉ lấy văn bản còn hiệu lực, và không lọc. "
    + "Cơ chế thứ hai là kiểm chứng trích dẫn hai lớp. Lớp a dùng biểu thức chính quy gỡ mọi mã không nằm trong ngữ cảnh, nên hệ thống không bao giờ trích tới đoạn mà mô hình chưa đọc. "
    + "Lớp b dùng một lượt mô hình ngôn ngữ kiểm từng cặp câu và đoạn được trích.");
  const col = (x, n, h, sub, rows) => {
    box(s, x, 1.6, 5.9, 5.2, { fill: COL.white });
    num(s, n, x + 0.25, 1.78);
    T(s, [{ text: h, options: { bold: true, color: COL.blue, fontSize: 17, breakLine: true } }, { text: sub, options: { color: COL.muted, fontSize: 12 } }],
      { x: x + 0.9, y: 1.7, w: 4.85, h: 0.7, valign: "middle" });
    rows.forEach(([label, text, last], j) => {
      const y = 2.6 + j * 1.38;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.25, y, w: 5.4, h: 1.25, rectRadius: 0.08, fill: { color: last ? COL.greenBg : COL.card }, line: { color: last ? COL.greenBg : COL.card } });
      T(s, [{ text: label, options: { bold: true, color: last ? COL.green : COL.blue, breakLine: true } }, { text }], { x: x + 0.4, y: y + 0.08, w: 5.1, h: 1.1, fontSize: 13.5, valign: "middle" });
    });
  };
  col(0.6, 1, "Truy xuất theo hiệu lực", "effective_date ≤ d_sự_việc < expiry_date", [
    ["event (đề tài)", "Router trích ngày sự việc; chỉ tìm trong văn bản có hiệu lực tại ngày đó."],
    ["Đối chứng (RQ4)", "current: chỉ văn bản còn hiệu lực · any: không lọc, mọi phiên bản."],
    ["Lợi ích", "Câu về sự việc trước 2021 được trả lời theo BLLĐ 2012, không theo luật mới.", true]]);
  col(6.7, 2, "Kiểm chứng trích dẫn hai lớp", "chạy sau bước sinh câu trả lời", [
    ["(a) Cú pháp, không gọi LLM", "Chuẩn hóa mã, gỡ mã không nằm trong ngữ cảnh; chạy ở mọi cấu hình."],
    ["(b) Ngữ nghĩa, 1 lượt LLM", "Kiểm từng cặp (câu, đoạn được trích); gỡ cặp không được hỗ trợ."],
    ["Câu mất hết trích dẫn", "Sinh lại một lần; vẫn thiếu thì gắn nhãn “(chưa có căn cứ)”.", true]]);
}

// ---------- 10. Demo
{
  const s = slide("DEMO", "Giao diện web: trích dẫn bấm được, thẻ hiệu lực văn bản, các bước của tác tử",
    "Mỗi câu trả lời có trích dẫn tới Khoản, bấm vào để xem toàn văn Điều, kèm thẻ hiệu lực và các bước của tác tử. "
    + "Chúng em demo bốn kịch bản: câu tình huống, câu có mốc năm 2020 để thấy căn cứ là Bộ luật Lao động 2012, câu ngoài phạm vi bị từ chối, và câu tra cứu trực tiếp một Điều. "
    + "Nếu API không ổn định, chúng em chiếu video quay sẵn.");
  figure(s, "assets/screenshots_nicegui/nicegui_02_answered_citations.png", 0.6, 1.6, 7.7, 1.6, "Câu trả lời kèm trích dẫn tới Khoản (Hình 4.3)");
  box(s, 8.5, 1.6, 4.25, 5.2, { fill: COL.white });
  T(s, "4 kịch bản", { x: 8.75, y: 1.75, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  [["Tình huống", "Bên mua trả tiền chậm có phải trả lãi không?"], ["Có mốc thời gian", "Năm 2020, nghỉ việc phải báo trước bao nhiêu ngày? → BLLĐ 2012"],
    ["Ngoài phạm vi", "Thủ tục ly hôn đơn phương? → từ chối"], ["Tra cứu trực tiếp", "Điều 104 BLLĐ 2012 quy định gì?"]].forEach(([h, d], i) => {
    const y = 2.25 + i * 1.12;
    num(s, i + 1, 8.75, y + 0.05, 0.4);
    T(s, [{ text: h, options: { bold: true, color: COL.blue, breakLine: true } }, { text: d, options: { fontSize: 12 } }], { x: 9.3, y, w: 3.3, h: 1.0, fontSize: 13.5 });
  });
}

// ---------- 11. RQ1
{
  const s = slide("RQ1: PHƯƠNG PHÁP TRUY XUẤT", "Hybrid + rerank đạt cả hai chỉ tiêu; rerank đưa Điều đúng lên vị trí cao hơn",
    "Trên 77 câu thực tế của bộ Zalo, tìm kiếm ngữ nghĩa vượt BM25 rõ rệt: Hit@5 0,844 so với 0,766, vì câu hỏi đời thường ít trùng từ với văn bản luật. "
    + "Hợp nhất RRF chưa làm tăng Hit@5 so với Dense, nhưng sau khi xếp hạng lại, MRR@10 tăng từ 0,748 lên 0,807, tức Điều đúng được đưa lên cao hơn. Điều này có ích vì tác tử chỉ đọc 5 đoạn đầu. "
    + "Cái giá là khoảng 6,8 giây mỗi câu cho bước rerank trên CPU.");
  figure(s, "docs/report/figures/rq1.png", 0.6, 1.6, 7.7, 1.875, "77 câu Zalo, biến thể Khoản + tiêu đề (Bảng 5.2, Hình 5.1)");
  sidePanel(s, "Kết quả", ["Hybrid + rerank: Hit@5 0,844 (≥ 0,80), Recall@10 0,872 (≥ 0,75)", "Dense > BM25: Hit@5 0,844 so với 0,766",
    "Rerank: MRR@10 0,748 → 0,807", "Cái giá: khoảng 6,8 giây mỗi câu trên CPU", "157 câu có căn cứ chuẩn: Hit@5 0,924, Recall@10 0,937"]);
}

// ---------- 12. RQ2
{
  const s = slide("RQ2: CÁCH PHÂN ĐOẠN", "Phân đoạn theo cấu trúc luật hơn hẳn cắt cố định",
    "Phân đoạn theo cấu trúc Điều, Khoản cao hơn cắt cố định 200 từ khoảng 0,25 đến 0,29 điểm Hit@5, vì cửa sổ cố định cắt ngang Điều và trộn nội dung nhiều Điều. "
    + "Trên câu Zalo, phân đoạn cấp Điều cao nhất, điều dễ hiểu vì căn cứ chuẩn của Zalo ở cấp Điều. Chúng em vẫn chọn cấp Khoản làm mặc định vì trích dẫn tới Khoản cụ thể hơn và đoạn ngắn hơn đưa vào ngữ cảnh. "
    + "");
  figure(s, "docs/report/figures/rq2.png", 0.6, 1.6, 7.7, 1.875, "77 câu Zalo, Hybrid + rerank (Bảng 5.3, Hình 5.2)");
  sidePanel(s, "Kết quả", ["Cấu trúc > cố định 200 từ: Hit@5 cao hơn 0,25–0,29", "Điều cao nhất trên câu Zalo: Hit@5 0,883 (căn cứ chuẩn cấp Điều)",
    "Chọn Khoản + tiêu đề làm mặc định: trích dẫn tới Khoản cụ thể hơn", "DRM@5 thấp ở mọi cách (0,075–0,101); chênh lệch nhỏ, chưa kiểm định"]);
}

// ---------- 13. RQ3
{
  const s = slide("RQ3: ĐÓNG GÓP CỦA CÁC THÀNH PHẦN TÁC TỬ", "209 câu, so ghép cặp với full, bootstrap 95% (* = khoảng tin cậy không chứa 0)",
    "Hình này là chênh lệch của từng cấu hình so với cấu hình đầy đủ, kèm khoảng tin cậy 95%. Cấu hình đầy đủ đạt Citation Precision 0,870, vượt chỉ tiêu 0,85. "
    + "Router có tác dụng rõ nhất: bỏ router làm tỷ lệ đúng phiên bản giảm 0,250, có ý nghĩa, vì không còn ngày sự việc để chọn văn bản. "
    + "Verify là lớp phòng vệ: bỏ verify thì recall tăng 0,034 nhưng precision giảm 0,016; trong phép thử tiêm trích dẫn sai, nó bắt được 96 trên 97 trích dẫn sai. "
    + "Bước grade chưa cho thấy lợi ích đo được. So với RAG một lượt, tác tử tốt hơn về precision và đúng phiên bản, đổi lại trung vị 15,9 giây mỗi câu.");
  figure(s, "docs/report/figures/rq3_diff.png", 0.6, 1.55, 12.15, 3.125);
  [["Router", "Bỏ router: đúng phiên bản −0,250*", COL.green, COL.greenBg],
    ["Verify (b)", "Bỏ: recall +0,034*, precision −0,016*; bắt 96/97 trích dẫn sai", COL.blue, COL.card],
    ["Grade", "Chưa có lợi ích đo được; thêm khoảng 1 lượt LLM", COL.warn, COL.warnBg],
    ["full so với baseline", "Precision +0,060*, phiên bản +0,250*; 15,9 s so với 6,9 s", COL.green, COL.greenBg]].forEach(([h, d, c, bg], i) => {
    const x = 0.6 + i * 3.05;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.6, w: 2.9, h: 1.25, rectRadius: 0.08, fill: { color: bg }, line: { color: bg } });
    T(s, [{ text: h, options: { bold: true, color: c, breakLine: true } }, { text: d, options: { fontSize: 11.5 } }], { x: x + 0.12, y: 5.65, w: 2.68, h: 1.15, fontSize: 13.5, valign: "middle" });
  });
}

// ---------- 14. RQ4
{
  const s = slide("RQ4: LỌC THEO HIỆU LỰC", "32 câu có mốc thời gian: event hơn current có ý nghĩa; hơn any nhưng chưa đủ mạnh",
    "Trên 32 câu có mốc thời gian, lọc theo ngày sự việc tốt hơn có ý nghĩa so với chỉ lấy văn bản còn hiệu lực: đúng phiên bản 0,750 so với 0,438, chênh 0,312; trên 20 câu giữ riêng cũng chênh 0,250. "
    + "So với không lọc, event cao hơn 0,188 nhưng chưa có ý nghĩa. "
    + "Ví dụ M_016: sự việc tháng 5 năm 2020, hợp đồng mùa vụ 6 tháng. Chính sách event trích đúng Điều 22 Bộ luật Lao động 2012. Chính sách current trích Bộ luật Lao động 2019, văn bản lúc đó chưa có hiệu lực.");
  figure(s, "docs/report/figures/rq4.png", 0.6, 1.6, 6.6, 1.875, "Bảng 5.9, 5.10, Hình 5.4");
  [["event", "0,750"], ["current", "0,438"], ["any", "0,562"]].forEach(([k, v], i) => {
    const x = 0.6 + i * 2.25;
    box(s, x, 5.55, 2.1, 1.25, { fill: i === 0 ? COL.greenBg : COL.card, line: i === 0 ? COL.green : COL.sky });
    T(s, v, { x, y: 5.6, w: 2.1, h: 0.65, fontSize: 24, bold: true, color: i === 0 ? COL.green : COL.blue, align: "center", valign: "middle" });
    T(s, `${k}: đúng phiên bản`, { x, y: 6.25, w: 2.1, h: 0.45, fontSize: 12, align: "center", valign: "middle" });
  });
  box(s, 7.45, 1.6, 5.3, 5.2, { fill: COL.white });
  T(s, "Ví dụ M_016 (sự việc 05/2020)", { x: 7.7, y: 1.75, w: 4.9, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, "“Tháng 5/2020, công ty ký hợp đồng mùa vụ 6 tháng để thu hoạch nông sản có đúng quy định không?”", { x: 7.7, y: 2.2, w: 4.85, h: 0.85, fontSize: 13, italic: true });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.7, y: 3.15, w: 4.8, h: 1.65, rectRadius: 0.08, fill: { color: COL.greenBg }, line: { color: COL.greenBg } });
  T(s, [{ text: "event: đúng phiên bản", options: { bold: true, color: COL.green, breakLine: true } },
    { text: "Hợp đồng mùa vụ dưới 12 tháng là loại hợp đồng được quy định [BLLD2012_Dieu22_Khoan1].", options: { fontSize: 12.5 } }],
  { x: 7.85, y: 3.22, w: 4.5, h: 1.5, fontSize: 14, valign: "middle" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.7, y: 4.95, w: 4.8, h: 1.7, rectRadius: 0.08, fill: { color: COL.redBg }, line: { color: COL.redBg } });
  T(s, [{ text: "current: sai phiên bản", options: { bold: true, color: COL.red, breakLine: true } },
    { text: "Trích [BLLD2019_Dieu20_Khoan1] (hợp đồng xác định thời hạn), văn bản chưa có hiệu lực năm 2020.", options: { fontSize: 12.5 } }],
  { x: 7.85, y: 5.02, w: 4.5, h: 1.55, fontSize: 14, valign: "middle" });
}

// ---------- 15. Phân tích lỗi và giới hạn
{
  const s = slide("PHÂN TÍCH LỖI VÀ GIỚI HẠN", "20 câu của cấu hình full: 12 lỗi thật của hệ thống, 8 do chỉ số báo nhầm",
    "Chúng em đọc tay 20 câu có dấu hiệu chưa tốt của cấu hình đầy đủ. 12 câu là lỗi thật của hệ thống, 8 câu là chỉ số báo nhầm, ví dụ hệ thống trích thêm một Điều liên quan hợp lý nhưng ngoài căn cứ chuẩn. "
    + "Lỗi thật nhiều nhất là trích dẫn có liên quan một phần lọt qua verify, và từ chối nhầm do router quá chặt với câu dân sự đời thường. "
    + "Giới hạn chính là prompt được chỉnh trên tập kiểm thử, bộ chấm kiểm định yếu và cỡ mẫu nhỏ, nên nhiều chênh lệch mới là xu hướng.");
  box(s, 0.6, 1.6, 5.9, 5.2, { fill: COL.white });
  T(s, "Loại lỗi (một câu có thể nhiều loại)", { x: 0.85, y: 1.75, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  const errs = [["Trích dẫn không hỗ trợ nội dung câu", 5], ["Từ chối nhầm", 3], ["Định tuyến sai (xếp nhầm ngoài phạm vi)", 2], ["Truy xuất sai Điều", 2],
    ["Trả lời thiếu điều kiện, con số", 2], ["Lấy nhầm văn bản", 1], ["Chỉ số báo nhầm (trích thêm Điều hợp lý…)", 8]];
  errs.forEach(([label, n], i) => {
    const y = 2.3 + i * 0.6, last = i === errs.length - 1;
    T(s, label, { x: 0.85, y, w: 3.5, h: 0.45, fontSize: 12.5, valign: "middle", color: last ? COL.muted : COL.text });
    s.addShape(pres.shapes.RECTANGLE, { x: 4.4, y: y + 0.08, w: 0.22 * n, h: 0.3, fill: { color: last ? COL.line : COL.sky }, line: { color: last ? COL.line : COL.sky } });
    T(s, String(n), { x: 4.45 + 0.22 * n, y, w: 0.4, h: 0.45, fontSize: 12.5, bold: true, color: COL.blue, valign: "middle" });
  });
  T(s, "Chỉ số báo nhầm tính theo câu (8/20).", { x: 0.85, y: 6.42, w: 5.4, h: 0.3, fontSize: 11, italic: true, color: COL.muted });
  sidePanel(s, "Giới hạn", ["Prompt chỉnh trên tập kiểm thử; tập giữ riêng 30 câu giảm nhưng không loại bỏ được",
    "Bộ chấm: một người chấm tay, cũng là người làm hệ thống; kappa = 0", "Cỡ mẫu nhỏ: router với Correctness, event so với any mới là xu hướng",
    "5 văn bản gốc, chưa hợp nhất sửa đổi; không có Nghị định, Thông tư", "Mô hình nhỏ, API miễn phí; reranker đọc tối đa 512 token"],
  { x: 6.7, w: 6.05, gap: 8 });
}

// ---------- 16. Kết luận
{
  const s = slide("KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "Đạt cả ba chỉ tiêu; đóng góp rõ nhất là truy xuất theo hiệu lực tại thời điểm sự việc",
    "Tóm lại, hệ thống đạt cả ba chỉ tiêu đặt ra. Đóng góp rõ nhất là truy xuất theo hiệu lực: cả RQ3 và RQ4 cho thấy trích ngày sự việc rồi lọc văn bản giúp trích đúng phiên bản tốt hơn rõ, 0,750 so với 0,500 của RAG một lượt và 0,438 của chính sách chỉ dùng văn bản còn hiệu lực. "
    + "Verify là lớp phòng vệ trước trích dẫn sai. Hệ thống phù hợp làm công cụ tra cứu tham khảo, nơi người dùng bấm vào trích dẫn để tự kiểm chứng. "
    + "Hướng phát triển chính là tách tập phát triển, mở rộng tập câu có mốc thời gian, và mở rộng kho sang Nghị định, Thông tư.");
  [["0,844", "Hit@5 (≥ 0,80)"], ["0,872", "Recall@10 (≥ 0,75)"], ["0,870", "Citation Precision (≥ 0,85)"]].forEach(([v, l], i) => {
    const x = 0.6 + i * 2.05;
    box(s, x, 1.6, 1.9, 1.35, { fill: COL.greenBg, line: COL.green });
    T(s, v, { x, y: 1.65, w: 1.9, h: 0.7, fontSize: 24, bold: true, color: COL.green, align: "center", valign: "middle" });
    T(s, l, { x: x + 0.05, y: 2.33, w: 1.8, h: 0.55, fontSize: 11, align: "center", valign: "middle" });
  });
  box(s, 0.6, 3.15, 5.95, 3.65, { fill: COL.white });
  T(s, "Kết luận", { x: 0.85, y: 3.3, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: COL.blue });
  T(s, bullets(["Truy xuất theo hiệu lực: đúng phiên bản 0,750 so với 0,500 (RAG một lượt) và 0,438 (chỉ văn bản còn hiệu lực)",
    "Verify (b) là lớp phòng vệ: bắt 96/97 trích dẫn sai tiêm vào", "Grade chưa cho thấy lợi ích đo được",
    "Phù hợp làm công cụ tra cứu tham khảo có trích dẫn để người dùng tự kiểm chứng"], 8), { x: 0.85, y: 3.8, w: 5.5, h: 2.9, fontSize: 13.5 });
  sidePanel(s, "Hướng phát triển", ["Tách tập phát triển và tập kiểm thử", "Kiểm định bộ chấm với nhiều người, có chuyên môn luật",
    "Mở rộng tập câu có mốc thời gian lên vài trăm câu", "Cải thiện router; dùng mô hình khác cho bước verify",
    "Văn bản hợp nhất, hiệu lực cấp Điều, Khoản; thêm Nghị định, Thông tư", "Thử mô hình lớn hơn; rerank Điều dài theo nhiều cửa sổ"],
  { x: 6.75, w: 6.0, gap: 8 });
}

// ---------- 17. Cảm ơn
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  T(s, "Chúng em xin chân thành cảm ơn quý Thầy Cô đã lắng nghe", { x: 0.6, y: 2.4, w: 12.1, h: 1.0, fontSize: 30, bold: true, color: COL.blue, align: "center", valign: "middle" });
  T(s, "Rất mong nhận được câu hỏi và góp ý của Hội đồng", { x: 0.6, y: 3.45, w: 12.1, h: 0.6, fontSize: 18, color: COL.sky, align: "center", valign: "middle" });
  T(s, "Phạm Huỳnh Quốc Đạt (52300098) – Hoàng Sinh Hùng (52300106) · GVHD: PGS.TS. Lê Anh Cường", { x: 0.6, y: 4.6, w: 12.1, h: 0.4, fontSize: 13, color: COL.muted, align: "center" });
  const note = "Phần trình bày của chúng em đến đây là hết. Chúng em xin cảm ơn quý Thầy Cô đã lắng nghe, và rất mong nhận được câu hỏi, góp ý của Hội đồng.";
  s.addNotes(note);
  NOTES.push(note);
}

// Lời thuyết trình: khoảng 130 từ/phút; thuyết trình tối đa 15 phút (sheet môn học)
const words = NOTES.join(" ").split(/\s+/).length;
console.log(`${NOTES.length} slide, lời nói ${words} từ ≈ ${(words / 130).toFixed(1)} phút`);
pres.writeFile({ fileName: OUT }).then(() => console.log("saved", OUT));
