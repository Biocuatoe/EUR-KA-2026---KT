// EURÉKA 2026 — 5-minute defense deck (Adaptive LQR, battery aging, NSGA-II).
// Native, editable shapes only. Run: node build.js <out.pptx>
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/e05e24fd-69da-40c6-a255-41cc1e68a3c6_761b7d0c-f88b-41fd-9303-7e8e34dd6903/pptx/scripts/apply_theme.js");

const OUT = process.argv[2] || "EUREKA_2026_Adaptive_LQR_Defense_5min.pptx";

const THEME = {
  name: "EUREKA 2026 Engineering",
  headFontFace: "Inter",
  bodyFontFace: "Inter",
  colors: {
    dk1: "18324B", // navy: titles, main text, principal control path
    lt1: "FFFFFF",
    dk2: "667085", // secondary text
    lt2: "F4F6F8", // light structural background
    accent1: "477F7A", // muted teal: SoH / adaptive pathway
    accent2: "9A7549", // warm grey: offline optimisation / aging
    accent3: "E4E7EC", // fine dividers
    accent4: "98A2B3", // structural outlines, secondary connections
    accent5: "18324B",
    accent6: "D0D5DD",
    hlink: "477F7A",
    folHlink: "667085",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "LQR thích nghi với bù suy giảm pin cho Micro-EV";
pres.subject = "EURÉKA 2026 — báo cáo bảo vệ 5 phút";
pres.author = "EURÉKA 2026";

const C = pres.SchemeColor;
const NAVY = C.text1, GREY = C.text2, WHITE = C.background1, PANEL = C.background2;
const TEAL = C.accent1, WARM = C.accent2, DIVIDER = C.accent3, OUTLINE = C.accent4, SOFT = C.accent6;

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "COVER",
  background: { color: "FFFFFF" },
  objects: [],
});

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: "FFFFFF" },
  margin: [0.4, 0.6, 0.5, 0.6],
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.4, w: 9, h: 0.3, fontSize: 13, bold: true, color: TEAL, margin: 0, valign: "middle", align: "left", charSpacing: 0.5 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.72, w: 12.1, h: 0.66, fontSize: 32, bold: true, color: NAVY, margin: 0, valign: "middle", align: "left" }, text: "" } },
    { text: { text: "EURÉKA 2026 · LQR thích nghi với bù suy giảm pin cho Micro-EV", options: { x: 0.6, y: 7.02, w: 8, h: 0.25, fontSize: 10, color: GREY, margin: 0, valign: "middle" } } },
  ],
  slideNumber: { x: 12.13, y: 7.02, w: 0.6, h: 0.25, fontSize: 10, color: GREY, align: "right", margin: 0 },
});

// ---------------------------------------------------------------- helpers
let nameSeq = 0;
const nm = (n) => `${n || "obj"}-${++nameSeq}`;

// "R_{0}" -> subscript, "x^{T}" -> superscript.
function runs(str, opts) {
  return str.split(/(_\{[^}]*\}|\^\{[^}]*\})/).filter((p) => p !== "").map((p) => {
    if (p.startsWith("_{")) return { text: p.slice(2, -1), options: { ...opts, subscript: true } };
    if (p.startsWith("^{")) return { text: p.slice(2, -1), options: { ...opts, superscript: true } };
    return { text: p, options: { ...opts } };
  });
}

// lines: [[string, opts], ...] -> text-run array with breaks between lines.
function rich(lines) {
  const out = [];
  lines.forEach(([s, o], i) => {
    const r = runs(s, o);
    if (i < lines.length - 1) r[r.length - 1].options.breakLine = true;
    out.push(...r);
  });
  return out;
}

function text(slide, content, x, y, w, h, o = {}) {
  const body = typeof content === "string" ? runs(content, {}) : content;
  slide.addText(body, {
    x, y, w, h, margin: 0, isTextBox: true, valign: "top", color: NAVY, fontSize: 16,
    objectName: nm(o.name || "text"), ...o,
  });
}

// Straight line between two points; arrowhead at (x2, y2) when o.arrow.
function seg(slide, x1, y1, x2, y2, o = {}) {
  const line = { color: o.color || NAVY, width: o.width || 1.5 };
  if (o.dash) line.dashType = o.dash;
  if (o.arrow) line.endArrowType = "triangle";
  slide.addShape(pres.shapes.LINE, {
    x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    flipH: x2 < x1, flipV: y2 < y1, line, objectName: nm(o.name || "line"),
  });
}

// Orthogonal polyline through points; arrowhead on the final segment only.
function path(slide, pts, o = {}) {
  for (let i = 0; i < pts.length - 1; i++) {
    const last = i === pts.length - 2;
    seg(slide, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], { ...o, arrow: last && o.arrow !== false });
  }
}

// Diagram block: rectangle with an editable title / subtitle inside it.
function block(slide, x, y, w, h, title, sub, o = {}) {
  const lines = [[title, { fontSize: o.titleSize || 15, bold: true, color: o.titleColor || NAVY }]];
  for (const l of [].concat(sub || [])) lines.push([l, { fontSize: o.subSize || 13, color: o.subColor || GREY }]);
  slide.addText(rich(lines), {
    shape: pres.shapes.RECTANGLE, x, y, w, h,
    fill: { color: o.fill || WHITE }, line: { color: o.line || NAVY, width: o.lineWidth || 1.25, ...(o.dash ? { dashType: o.dash } : {}) },
    align: o.align || "center", valign: "middle", margin: o.align === "left" ? [2, 12, 2, 12] : [2, 8, 2, 8], paraSpaceAfter: 0,
    objectName: nm(o.name || "block"),
  });
}

function dot(slide, cx, cy, r, color, name) {
  slide.addShape(pres.shapes.OVAL, { x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, fill: { color }, line: { color, width: 0.5 }, objectName: nm(name || "dot") });
}

function content(sectionTitle, kicker, title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle });
  s.addText(kicker, { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  return s;
}

// ================================================================= SLIDE 1 — title
pres.addSection({ title: "Mở đầu" });
{
  const s = pres.addSlide({ masterName: "COVER", sectionTitle: "Mở đầu" });

  text(s, "BÁO CÁO BẢO VỆ ĐỀ TÀI", 0.75, 1.75, 6.8, 0.3, { fontSize: 13, bold: true, color: TEAL, charSpacing: 1, name: "cover-kicker" });
  text(s, "Thiết kế và tối ưu hóa bộ điều khiển LQR thích nghi với bù suy giảm pin cho Micro-EV",
    0.75, 2.17, 6.9, 2.0, { fontSize: 34, bold: true, color: NAVY, lineSpacingMultiple: 1.05, name: "cover-title" });
  text(s, "Adaptive LQR · Battery Aging · Multi-objective Optimization", 0.75, 4.4, 7.2, 0.4,
    { fontSize: 17, color: TEAL, name: "cover-subtitle" });
  seg(s, 0.75, 5.25, 7.55, 5.25, { color: DIVIDER, width: 1, name: "cover-divider" });
  text(s, "Giải thưởng Sinh viên Nghiên cứu Khoa học EURÉKA 2026", 0.75, 5.42, 6.8, 0.3,
    { fontSize: 12, color: GREY, name: "cover-competition" });

  // Micro-EV powertrain motif (line art, all native shapes)
  const ox = 8.35, top = 2.45;
  s.addShape(pres.shapes.CUSTOM_GEOMETRY, {
    x: ox, y: top, w: 4.3, h: 2.3, fill: { color: WHITE }, line: { color: NAVY, width: 2 }, objectName: nm("ev-body"),
    points: [{ x: 0.05, y: 2.3 }, { x: 0, y: 0.55 }, { x: 0.25, y: 0.05 }, { x: 3.05, y: 0.05 }, { x: 3.75, y: 1.05 },
      { x: 4.25, y: 1.3 }, { x: 4.3, y: 2.3 }, { close: true }],
  });
  s.addShape(pres.shapes.CUSTOM_GEOMETRY, {
    x: ox + 0.3, y: top + 0.3, w: 3.3, h: 0.75, fill: { color: PANEL }, line: { color: NAVY, width: 1.25 }, objectName: nm("ev-window"),
    points: [{ x: 0, y: 0 }, { x: 2.77, y: 0 }, { x: 3.3, y: 0.75 }, { x: 0, y: 0.75 }, { close: true }],
  });
  seg(s, ox + 1.6, top + 0.3, ox + 1.6, top + 1.05, { color: NAVY, width: 1.25, name: "ev-pillar" });
  s.addShape(pres.shapes.RECTANGLE, { x: ox + 4.08, y: top + 1.45, w: 0.17, h: 0.12, fill: { color: NAVY }, line: { color: NAVY, width: 0.5 }, objectName: nm("ev-lamp") });

  const gy = 5.25, wr = 0.42, wy = gy - wr;
  for (const [cx, label] of [[9.2, "rear"], [11.8, "front"]]) {
    s.addShape(pres.shapes.OVAL, { x: cx - 0.55, y: wy - 0.55, w: 1.1, h: 1.1, fill: { color: WHITE }, line: { color: WHITE, width: 0.5 }, objectName: nm(`ev-arch-${label}`) });
    s.addShape(pres.shapes.OVAL, { x: cx - wr, y: wy - wr, w: 2 * wr, h: 2 * wr, fill: { color: WHITE }, line: { color: NAVY, width: 2 }, objectName: nm(`ev-wheel-${label}`) });
    s.addShape(pres.shapes.OVAL, { x: cx - 0.14, y: wy - 0.14, w: 0.28, h: 0.28, fill: { color: PANEL }, line: { color: NAVY, width: 1 }, objectName: nm(`ev-hub-${label}`) });
  }
  // battery pack under the floor
  const bx = 10.1, bw = 1.15, by = 4.33, bh = 0.26;
  s.addShape(pres.shapes.RECTANGLE, { x: bx, y: by, w: bw, h: bh, fill: { color: TEAL }, line: { color: TEAL, width: 0.5 }, objectName: nm("ev-battery") });
  for (let i = 1; i < 4; i++) seg(s, bx + (bw * i) / 4, by + 0.04, bx + (bw * i) / 4, by + bh - 0.04, { color: WHITE, width: 1, name: "ev-cell" });
  // motor near the rear axle
  s.addShape(pres.shapes.OVAL, { x: 9.68, y: 4.33, w: 0.28, h: 0.28, fill: { color: WHITE }, line: { color: NAVY, width: 1.5 }, objectName: nm("ev-motor") });
  // controller with torque command and SoH feedback
  s.addText("LQR", { shape: pres.shapes.RECTANGLE, x: 10.25, y: 3.62, w: 0.75, h: 0.36, fill: { color: WHITE }, line: { color: NAVY, width: 1.25 },
    fontSize: 11, bold: true, color: NAVY, align: "center", valign: "middle", margin: 0, objectName: nm("ev-controller") });
  path(s, [[10.25, 3.8], [9.82, 3.8], [9.82, 4.33]], { color: NAVY, width: 1.25, name: "ev-torque" });
  seg(s, 10.8, by, 10.8, 3.98, { color: TEAL, width: 1.25, dash: "dash", arrow: true, name: "ev-soh" });
  text(s, "SoH", 10.88, 4.0, 0.5, 0.25, { fontSize: 10, bold: true, color: TEAL, name: "ev-soh-label" });

  seg(s, 8.05, gy, 12.95, gy, { color: DIVIDER, width: 1, name: "ev-ground" });
  text(s, "Hệ truyền động: pin · động cơ · bộ điều khiển", 8.35, 5.42, 4.3, 0.3, { fontSize: 11, color: GREY, name: "ev-caption" });

  s.addNotes(
    "Kính chào Hội đồng. Em xin trình bày đề tài “Thiết kế và tối ưu hóa bộ điều khiển LQR thích nghi với bộ bù suy giảm tuổi thọ pin cho hệ truyền động xe điện cỡ nhỏ (Micro-EV)”.\n\nCâu hỏi trung tâm là: khi pin già đi, bộ điều khiển nên thay đổi như thế nào, và làm sao đánh giá sự thay đổi đó một cách công bằng."
  );
}

// ================================================================= SLIDE 2 — problem and contributions
pres.addSection({ title: "Bài toán" });
{
  const s = content("Bài toán", "Vấn đề nghiên cứu", "Điều khiển thích nghi trước sự suy giảm của pin");

  // Left: the engineering problem as a causal chain
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.75, w: 4.95, h: 4.9, fill: { color: PANEL }, line: { color: PANEL, width: 0.5 }, objectName: nm("problem-panel") });
  text(s, "BÀI TOÁN", 0.95, 2.0, 3, 0.3, { fontSize: 12, bold: true, color: TEAL, charSpacing: 1, name: "problem-label" });

  const chain = [
    ["Pin suy giảm theo thời gian sử dụng", "SoH (trạng thái sức khỏe pin) giảm dần"],
    ["Nội trở tăng, dung lượng giảm", "R_{0}, R_{1} của mô hình pin phụ thuộc SoH"],
    ["LQR hệ số cố định", "thiết kế một lần cho pin mới"],
  ];
  chain.forEach(([t, sub], i) => {
    const y = 2.42 + i * 1.07;
    text(s, rich([[t, { fontSize: 17, bold: true, color: NAVY }], [sub, { fontSize: 14, color: GREY }]]), 0.95, y, 4.35, 0.8, { name: "problem-step" });
    if (i < chain.length - 1) seg(s, 1.1, y + 0.78, 1.1, y + 1.06, { color: TEAL, width: 1.5, arrow: true, name: "problem-arrow" });
  });
  seg(s, 0.95, 5.5, 5.2, 5.5, { color: SOFT, width: 1, name: "problem-divider" });
  text(s, "Luật điều khiển nên thích nghi với SoH thế nào để cân bằng năng lượng và lão hóa pin?",
    0.95, 5.65, 4.35, 0.8, { fontSize: 15, bold: true, color: NAVY, name: "problem-question" });

  // Right: three contributions
  text(s, "HƯỚNG TIẾP CẬN ĐỀ XUẤT", 6.1, 2.0, 6, 0.3, { fontSize: 12, bold: true, color: TEAL, charSpacing: 1, name: "approach-label" });
  const rows = [
    ["01", "Điều khiển thích nghi", [
      ["LQR lập lịch hệ số theo SoH ước lượng", { fontSize: 16, color: GREY }],
      ["J = Σ ( x^{T}Q(SoH) x + u^{T}R(SoH) u )", { fontSize: 15, color: NAVY }],
    ]],
    ["02", "Năng lượng và lão hóa pin", [
      ["Đánh giá đồng thời Wh/km và suy giảm dung lượng,", { fontSize: 16, color: GREY }],
      ["như hai chỉ số tách biệt", { fontSize: 16, color: GREY }],
    ]],
    ["03", "Thiết kế đa mục tiêu", [
      ["NSGA-II khám phá đánh đổi giữa các bộ trọng số Q, R", { fontSize: 16, color: GREY }],
      ["dưới ràng buộc ổn định và bám tốc độ", { fontSize: 16, color: GREY }],
    ]],
  ];
  rows.forEach(([num, title, lines], i) => {
    const y = 2.45 + i * 1.42;
    if (i > 0) seg(s, 6.1, y - 0.2, 12.73, y - 0.2, { color: DIVIDER, width: 1, name: "approach-divider" });
    text(s, num, 6.1, y, 0.75, 0.4, { fontSize: 22, bold: true, color: TEAL, name: "approach-num" });
    text(s, rich([[title, { fontSize: 20, bold: true, color: NAVY }], ...lines]), 6.95, y, 5.78, 1.15,
      { paraSpaceAfter: 3, name: "approach-row" });
  });

  s.addNotes(
    "Pin xe điện suy giảm theo thời gian sử dụng; mức suy giảm được mô tả bằng SoH, trạng thái sức khỏe của pin. Khi SoH giảm, nội trở tăng và dung lượng giảm, trong khi bộ LQR hệ số cố định chỉ được thiết kế một lần cho pin mới.\n\nĐề tài đề xuất ba hướng. Một: LQR thích nghi, với trọng số Q và R được lập lịch theo SoH ước lượng. Hai: đánh giá đồng thời năng lượng tiêu thụ và suy giảm dung lượng, như hai chỉ số riêng, không lấy chỉ số này thay cho chỉ số kia. Ba: dùng NSGA-II để khám phá các bộ trọng số khả thi dưới ràng buộc ổn định và bám tốc độ, thay vì chọn theo kinh nghiệm."
  );
}

// ================================================================= SLIDE 3 — architecture
pres.addSection({ title: "Kiến trúc" });
{
  const s = content("Kiến trúc", "Kiến trúc hệ thống", "Kiến trúc điều khiển và tối ưu hóa tích hợp");

  // geometry
  const rowTop = 2.05, rowH = 2.1;               // controller and plant containers
  const ctrl = { x: 2.91, w: 2.7 }, plant = { x: 6.26, w: 2.75 };
  const sigma = { cx: 2.4, cy: 3.15, r: 0.19 };
  const jx = 9.45;                                 // speed-output junction
  const met = { x: 9.91, w: 2.82 };
  const fbY = 1.72;                                // speed feedback route (above the loop)
  const lowY = 4.6, lowH = 0.66;                   // estimator / scheduling row
  const optY = 6.12;                               // NSGA-II loop route
  const inC = { x: ctrl.x + 0.15, w: ctrl.w - 0.3 }, inP = { x: plant.x + 0.15, w: plant.w - 0.3, h: 0.46 };

  // containers first, so every connector is drawn on top of them
  s.addShape(pres.shapes.RECTANGLE, { x: ctrl.x, y: rowTop, w: ctrl.w, h: rowH, fill: { color: PANEL }, line: { color: OUTLINE, width: 1 }, objectName: nm("ctrl-container") });
  text(s, "BỘ ĐIỀU KHIỂN · A/B", ctrl.x + 0.15, rowTop + 0.1, ctrl.w - 0.3, 0.25, { fontSize: 11, bold: true, color: GREY, charSpacing: 0.5, name: "ctrl-label" });
  s.addShape(pres.shapes.RECTANGLE, { x: plant.x, y: rowTop, w: plant.w, h: rowH, fill: { color: PANEL }, line: { color: OUTLINE, width: 1 }, objectName: nm("plant-container") });
  text(s, "HỆ TRUYỀN ĐỘNG MICRO-EV", plant.x + 0.15, rowTop + 0.1, plant.w - 0.3, 0.25, { fontSize: 11, bold: true, color: GREY, charSpacing: 0.5, name: "plant-label" });
  text(s, "CHỈ SỐ ĐẦU RA", met.x, rowTop + 0.1, met.w, 0.25, { fontSize: 11, bold: true, color: GREY, charSpacing: 0.5, name: "metrics-label" });

  // blocks
  block(s, 0.6, 2.7, 1.32, 0.9, "Chu trình lái", "v_{ref}(t)", { name: "drive-cycle", titleSize: 14 });
  block(s, inC.x, 2.45, inC.w, 0.68, "LQR hệ số cố định", "đối chứng · K_{0} không đổi", { line: OUTLINE, name: "fixed-lqr" });
  block(s, inC.x, 3.28, inC.w, 0.68, "LQR thích nghi", "K(SoH) cập nhật theo SoH", { line: TEAL, lineWidth: 1.75, titleColor: TEAL, name: "adaptive-lqr" });
  block(s, inP.x, 2.45, inP.w, inP.h, "Động cơ – truyền động", null, { name: "motor", titleSize: 14 });
  block(s, inP.x, 2.99, inP.w, inP.h, "Động lực học dọc xe", null, { name: "vehicle", titleSize: 14 });
  block(s, inP.x, 3.53, inP.w, inP.h, "Pin – mạch tương đương", null, { name: "battery", titleSize: 14 });
  block(s, inP.x, lowY, inP.w, lowH, "Ước lượng SoH", "EKF từ điện áp, dòng pin", { line: TEAL, lineWidth: 1.5, titleColor: TEAL, name: "soh-estimator" });
  block(s, inC.x, lowY, inC.w, lowH, "Lập lịch hệ số", "Q, R(SoH) → DARE → K", { line: TEAL, lineWidth: 1.5, titleColor: TEAL, name: "gain-scheduling" });
  block(s, met.x, 2.45, met.w, 0.98, "Hiệu năng xe – điều khiển", "RMSE bám tốc độ · Wh/km · ràng buộc vận hành", { line: NAVY, align: "left", name: "metric-performance" });
  block(s, met.x, 3.55, met.w, 0.98, "Lão hóa pin", "suy giảm dung lượng từ mô hình lão hóa, theo số chu kỳ", { line: WARM, titleColor: WARM, align: "left", name: "metric-aging" });
  const nsga = { x: 6.3, y: 5.7, w: 2.75, h: 0.86 };
  block(s, nsga.x, nsga.y, nsga.w, nsga.h, "NSGA-II", ["tối ưu đa mục tiêu", "ngoại tuyến"], { line: WARM, dash: "dash", lineWidth: 1.5, titleColor: WARM, titleSize: 16, name: "nsga2" });

  // summing junction
  s.addShape(pres.shapes.OVAL, { x: sigma.cx - sigma.r, y: sigma.cy - sigma.r, w: 2 * sigma.r, h: 2 * sigma.r, fill: { color: WHITE }, line: { color: NAVY, width: 1.5 }, objectName: nm("sum-junction") });
  seg(s, sigma.cx - 0.13, sigma.cy, sigma.cx + 0.13, sigma.cy, { color: NAVY, width: 1, name: "sum-h" });
  seg(s, sigma.cx, sigma.cy - 0.13, sigma.cx, sigma.cy + 0.13, { color: NAVY, width: 1, name: "sum-v" });
  text(s, "+", 1.98, 2.8, 0.2, 0.25, { fontSize: 14, bold: true, name: "sum-plus" });
  text(s, "−", 2.12, 2.58, 0.2, 0.25, { fontSize: 14, bold: true, name: "sum-minus" });

  // real-time control loop (navy)
  seg(s, 1.92, sigma.cy, sigma.cx - sigma.r, sigma.cy, { arrow: true, name: "ref-to-sum" });
  seg(s, sigma.cx + sigma.r, sigma.cy, ctrl.x, sigma.cy, { arrow: true, name: "error-to-ctrl" });
  text(s, "e", 2.67, 2.85, 0.2, 0.25, { fontSize: 14, color: NAVY, name: "error-label" });
  seg(s, ctrl.x + ctrl.w, 2.68, inP.x, 2.68, { arrow: true, name: "torque-cmd" });
  text(s, "T_{ref}", 5.72, 2.36, 0.5, 0.25, { fontSize: 13, color: NAVY, name: "torque-label" });
  const vY = 3.22;
  seg(s, inP.x + inP.w, vY, jx, vY, { name: "speed-out" });
  dot(s, jx, vY, 0.05, NAVY, "speed-junction");
  path(s, [[jx, vY], [jx, fbY], [sigma.cx, fbY], [sigma.cx, sigma.cy - sigma.r]], { name: "speed-feedback" });
  text(s, "v đo được", 5.0, fbY - 0.3, 1.4, 0.25, { fontSize: 13, color: NAVY, align: "center", name: "speed-feedback-label" });
  seg(s, jx, vY, met.x, vY, { arrow: true, name: "speed-to-metrics" });

  // battery signals (grey): to aging metric and to SoH estimator
  const iY = 3.76;
  seg(s, inP.x + inP.w, iY, met.x, iY, { color: OUTLINE, width: 1.25, arrow: true, name: "battery-to-aging" });
  text(s, "I(t), SoC(t)", 9.05, iY + 0.04, 0.85, 0.25, { fontSize: 11, color: GREY, name: "battery-signal-label" });
  seg(s, 7.0, 3.99, 7.0, lowY, { color: OUTLINE, width: 1.25, arrow: true, name: "battery-to-ekf" });
  text(s, "V, I pin", 7.1, 4.24, 0.9, 0.25, { fontSize: 12, color: GREY, name: "battery-vi-label" });

  // adaptive SoH path (teal)
  seg(s, inP.x, lowY + lowH / 2, inC.x + inC.w, lowY + lowH / 2, { color: TEAL, width: 1.75, arrow: true, name: "soh-to-scheduling" });
  text(s, "SoH", 5.6, lowY + 0.03, 0.66, 0.25, { fontSize: 12, bold: true, color: TEAL, align: "center", name: "soh-label" });
  seg(s, 3.75, lowY, 3.75, 3.96, { color: TEAL, width: 1.75, arrow: true, name: "scheduling-to-adaptive" });

  // outer, offline NSGA-II loop (warm, dashed)
  path(s, [[11.32, 4.53], [11.32, optY], [nsga.x + nsga.w, optY]], { color: WARM, width: 1.5, dash: "dash", name: "objectives-to-nsga" });
  text(s, rich([["J_{1}: Wh/km", { fontSize: 12, color: WARM }], ["J_{2}: suy giảm dung lượng", { fontSize: 12, color: WARM }]]), 9.2, 5.6, 2.05, 0.45, { name: "objectives-label" });
  path(s, [[nsga.x, optY], [3.75, optY], [3.75, lowY + lowH]], { color: WARM, width: 1.5, dash: "dash", name: "nsga-to-weights" });
  text(s, "bộ trọng số Q, R ứng viên", 3.88, optY - 0.32, 2.35, 0.25, { fontSize: 12, color: WARM, name: "weights-label" });
  text(s, "ràng buộc: ổn định · bám tốc độ", 3.88, optY + 0.08, 2.35, 0.25, { fontSize: 11, color: GREY, name: "constraints-label" });

  // legend
  const lg = [[NAVY, null, "Vòng điều khiển thời gian thực"], [TEAL, null, "Nhánh thích nghi theo SoH"], [WARM, "dash", "Vòng tối ưu ngoại tuyến"]];
  lg.forEach(([color, dash, label], i) => {
    const y = 5.62 + i * 0.3;
    seg(s, 0.6, y + 0.12, 1.0, y + 0.12, { color, width: 1.75, dash, name: "legend-line" });
    text(s, label, 1.1, y, 2.5, 0.25, { fontSize: 11, color: GREY, name: "legend-text" });
  });

  s.addNotes(
    "Đường xanh đậm là vòng điều khiển thời gian thực. Chu trình lái cho vận tốc tham chiếu; sai số với vận tốc đo được đi vào bộ điều khiển. Bộ điều khiển có hai phương án cùng giao diện: LQR hệ số cố định làm đối chứng, và LQR thích nghi. Đầu ra là mô-men tham chiếu cho hệ truyền động, gồm động cơ, động lực học dọc của xe và mô hình pin mạch tương đương.\n\nĐường xanh lục là nhánh thích nghi: điện áp và dòng pin đi vào bộ ước lượng SoH dùng EKF; SoH ước lượng dùng để lập lịch Q, R, giải phương trình Riccati rời rạc và cập nhật hệ số K. SoH thay đổi rất chậm so với chu kỳ điều khiển; bộ điều khiển không đo suy giảm dung lượng tại mỗi bước.\n\nBên phải là các chỉ số tính từ quỹ đạo mô phỏng: hiệu năng điều khiển, năng lượng trên mỗi ki-lô-mét, và tách riêng là suy giảm dung lượng từ mô hình lão hóa. Đường nét đứt là vòng tối ưu ngoại tuyến: NSGA-II đề xuất bộ trọng số ứng viên, chạy mô phỏng, nhận hai mục tiêu năng lượng và lão hóa, rồi lặp lại. Vòng này không chạy trong bộ điều khiển thời gian thực."
  );
}

// ================================================================= SLIDE 4 — validation workflow
pres.addSection({ title: "Kiểm chứng" });
{
  const s = content("Kiểm chứng", "Phương pháp kiểm chứng", "Quy trình kiểm chứng định lượng");

  const colW = 2.85, gap = 0.243, x0 = 0.6, spineY = 2.0, r = 0.25;
  const steps = [
    ["Xác định mô hình và điều kiện", [
      "Mô hình xe, động cơ, pin",
      "SoC, SoH ban đầu; giả định tường minh",
      "Nguồn gốc từng tham số",
      "Một biên tính năng lượng thống nhất",
    ]],
    ["So sánh công bằng", [
      "LQR cố định ↔ LQR thích nghi",
      "Cùng đối tượng, chu trình lái, điều kiện đầu và ràng buộc",
      "Bộ điều khiển khác chỉ khi có cài đặt đầy đủ",
    ]],
    ["Tính chỉ số riêng biệt", null],
    ["Bền vững và tái lập", [
      "NEDC · WLTP · CLTC · VUC, khi có dữ liệu rõ nguồn",
      "Độ nhạy theo kế hoạch lấy mẫu đã định",
      "Lưu dữ liệu thô, tham số, nhật ký",
      "Thống kê chỉ khi thiết kế mẫu cho phép",
    ]],
  ];

  steps.forEach(([title, lines], i) => {
    const x = x0 + i * (colW + gap);
    s.addText(String(i + 1), { shape: pres.shapes.OVAL, x, y: spineY - r, w: 2 * r, h: 2 * r, fill: { color: WHITE }, line: { color: NAVY, width: 1.5 },
      fontSize: 16, bold: true, color: TEAL, align: "center", valign: "middle", margin: 0, objectName: nm("step-node") });
    if (i < steps.length - 1) seg(s, x + 2 * r + 0.12, spineY, x + colW + gap - 0.12, spineY, { color: OUTLINE, width: 1.25, arrow: true, name: "step-arrow" });
    text(s, title, x, 2.5, colW, 0.75, { fontSize: 18, bold: true, color: NAVY, name: "step-title" });
    if (lines) {
      text(s, lines.map((l, k) => ({ text: l, options: { breakLine: k < lines.length - 1 } })), x, 3.28, colW, 2.4,
        { fontSize: 15, color: GREY, paraSpaceAfter: 7, lineSpacingMultiple: 1.0, name: "step-body" });
    }
  });

  // step 3: three separate metrics, visually separated
  const x3 = x0 + 2 * (colW + gap);
  const metrics = [
    [NAVY, "Sai số bám tốc độ", "RMSE, m/s"],
    [TEAL, "Năng lượng", "Wh/km, biên tính rõ ràng"],
    [WARM, "Suy giảm dung lượng", "từ mô hình lão hóa đã cài đặt"],
  ];
  metrics.forEach(([color, t, sub], k) => {
    const y = 3.28 + k * 0.72;
    if (k > 0) seg(s, x3, y - 0.1, x3 + colW, y - 0.1, { color: DIVIDER, width: 1, name: "metric-divider" });
    dot(s, x3 + 0.08, y + 0.14, 0.07, color, "metric-dot");
    text(s, rich([[t, { fontSize: 15, bold: true, color: NAVY }], [sub, { fontSize: 13, color: GREY }]]), x3 + 0.27, y, colW - 0.27, 0.6, { name: "metric-item" });
  });

  // reference line: values reported in the thesis
  const by = 5.86, bh = 0.98;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: by, w: 12.13, h: bh, fill: { color: PANEL }, line: { color: PANEL, width: 0.5 }, objectName: nm("reference-band") });
  text(s, rich([["Đối chiếu định lượng", { fontSize: 14, bold: true, color: TEAL }],
    ["Giá trị do luận văn báo cáo: mốc đối chiếu, không phải mục tiêu tinh chỉnh", { fontSize: 11, color: GREY }]]),
    0.85, by + 0.14, 2.75, 0.78, { valign: "middle", name: "reference-label" });
  const figs = [
    [3.85, TEAL, "12,5% ± 2,1%", "về hiệu quả năng lượng", 2.6],
    [7.05, WARM, "15,3% ± 2,8%", "về giảm suy giảm dung lượng qua 1.000 chu kỳ", 5.4],
  ];
  figs.forEach(([x, color, num, label, w]) => {
    dot(s, x + 0.07, by + 0.37, 0.07, color, "reference-dot");
    text(s, rich([[num, { fontSize: 22, bold: true, color: NAVY }], [label, { fontSize: 13, color: GREY }]]), x + 0.25, by + 0.18, w, 0.7, { name: "reference-figure" });
  });
  seg(s, 6.75, by + 0.2, 6.75, by + bh - 0.2, { color: SOFT, width: 1, name: "reference-separator" });

  s.addNotes(
    "Kiến trúc chỉ có giá trị khi được kiểm chứng bằng một quy trình công bằng và tái lập được.\n\nBước một: cố định mô hình xe, động cơ, pin và điều kiện ban đầu; ghi rõ nguồn gốc tham số, giả định, và một biên tính năng lượng duy nhất. Bước hai: so sánh LQR cố định với LQR thích nghi trên cùng đối tượng, cùng chu trình lái, cùng điều kiện đầu và giới hạn; bộ điều khiển khác chỉ đưa vào khi có cài đặt đầy đủ. Bước ba: tính riêng sai số bám tốc độ, năng lượng theo Wh/km và suy giảm dung lượng; năng lượng và lão hóa không thay thế cho nhau. Bước bốn: mở rộng sang NEDC, WLTP, CLTC và VUC khi có hồ sơ vận tốc rõ nguồn gốc, phân tích độ nhạy, và lưu toàn bộ dữ liệu thô, tham số, nhật ký.\n\nHai con số cuối trang là giá trị luận văn đã báo cáo: mười hai phẩy năm phần trăm về hiệu quả năng lượng, và mười lăm phẩy ba phần trăm về giảm suy giảm dung lượng qua một nghìn chu kỳ. Các con số này chưa được tái lập độc lập, nên em trình bày chúng như mốc đối chiếu, không phải kết quả đã khẳng định. Quy trình không tinh chỉnh mô hình để đạt mốc; kết quả được báo cáo đúng như thu được."
  );
}

// ================================================================= SLIDE 5 — conclusion
pres.addSection({ title: "Kết luận" });
{
  const s = content("Kết luận", "Kết luận", "Kết luận và hướng phát triển");

  text(s, "Khung điều khiển hướng tới tích hợp trạng thái sức khỏe pin, hiệu quả năng lượng và tối ưu hóa đa mục tiêu cho Micro-EV.",
    0.6, 1.75, 10.6, 1.05, { fontSize: 24, bold: true, color: NAVY, lineSpacingMultiple: 1.1, name: "conclusion-statement" });

  text(s, "HƯỚNG PHÁT TRIỂN", 0.6, 3.22, 6, 0.3, { fontSize: 12, bold: true, color: TEAL, charSpacing: 1, name: "future-label" });
  const colW = 3.75, gap = 0.4, x0 = 0.6, lineY = 3.78;
  seg(s, x0, lineY, 12.73, lineY, { color: OUTLINE, width: 1.25, arrow: true, name: "future-progress" });
  const items = [
    ["Kiểm chứng mô phỏng", "So sánh công bằng LQR cố định và LQR thích nghi trong các điều kiện lái và vận hành xác định"],
    ["Kiểm chứng lão hóa pin", "Củng cố cơ sở mô hình lão hóa, tham số hóa và đánh giá suy giảm dung lượng theo chu kỳ"],
    ["Mở rộng kỹ thuật", "Mở rộng phân tích đa mục tiêu, tiến tới HIL (phần cứng trong vòng lặp) hoặc thực nghiệm"],
  ];
  items.forEach(([t, d], i) => {
    const x = x0 + i * (colW + gap);
    dot(s, x + 0.09, lineY, 0.09, TEAL, "future-node");
    text(s, `0${i + 1}`, x, 4.05, 0.6, 0.35, { fontSize: 15, bold: true, color: TEAL, name: "future-num" });
    text(s, t, x, 4.42, colW - 0.1, 0.4, { fontSize: 19, bold: true, color: NAVY, name: "future-title" });
    text(s, d, x, 4.9, colW - 0.1, 1.1, { fontSize: 16, color: GREY, name: "future-body" });
  });

  seg(s, 0.6, 6.18, 12.73, 6.18, { color: DIVIDER, width: 1, name: "takeaway-divider" });
  text(s, "Giá trị của khung điều khiển được xác lập bằng so sánh công bằng, chỉ số tách biệt và dữ liệu có thể tái lập.",
    0.6, 6.32, 12.1, 0.4, { fontSize: 17, color: NAVY, name: "takeaway" });

  s.addNotes(
    "Tóm lại, đề tài xây dựng một khung điều khiển hướng tới tích hợp trạng thái sức khỏe pin, hiệu quả năng lượng và tối ưu hóa đa mục tiêu.\n\nBước tiếp theo gồm ba hướng: hoàn thiện kiểm chứng mô phỏng với so sánh công bằng giữa hai bộ điều khiển; củng cố mô hình lão hóa pin, từ tham số hóa đến đánh giá suy giảm dung lượng theo chu kỳ; và mở rộng phân tích đa mục tiêu, tiến tới kiểm chứng HIL hoặc thực nghiệm.\n\nEm xin cảm ơn Hội đồng và rất mong nhận được câu hỏi, góp ý."
  );
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
