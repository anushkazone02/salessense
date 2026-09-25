const pptxgen = require("pptxgenjs");
const path = require("path");

const NAVY = "1E2761";
const ICE = "CADCFC";
const WHITE = "FFFFFF";
const ACCENT = "7C3AED";
const INDIGO = "4F46E5";
const DARK_TEXT = "1E293B";
const MUTED = "64748B";
const CARD_BG = "F1F0FB";

const SCREENSHOTS = path.join(__dirname, "..", "assets", "screenshots");

function newDeck() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
  return pres;
}

const pres = newDeck();

function darkBg(slide) {
  slide.background = { color: NAVY };
}
function lightBg(slide) {
  slide.background = { color: WHITE };
}

function footer(slide, num) {
  slide.addText(`SalesSense  |  ${num}`, {
    x: 0.4, y: 7.12, w: 4, h: 0.3, fontSize: 10, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0,
  });
}

// ---------------- Slide 1: Title ----------------
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("SalesSense", {
    x: 0.8, y: 2.3, w: 11.7, h: 1.2, fontSize: 54, bold: true, color: WHITE, fontFace: "Cambria", isTextBox: true, margin: 0,
  });
  s.addText("Scalable Sales Prediction & Analytics System", {
    x: 0.8, y: 3.5, w: 11.7, h: 0.7, fontSize: 24, color: ICE, fontFace: "Calibri", isTextBox: true, margin: 0,
  });
  s.addText("Built with Apache Spark, Spark MLlib & Streamlit", {
    x: 0.8, y: 4.15, w: 11.7, h: 0.5, fontSize: 16, italics: true, color: "9AA5CE", fontFace: "Calibri", isTextBox: true, margin: 0,
  });
  s.addShape(pres.ShapeType.rect, { x: 0.8, y: 5.1, w: 1.6, h: 0.06, fill: { color: ACCENT } });
  s.addText("College Mini Project", {
    x: 0.8, y: 6.55, w: 6, h: 0.4, fontSize: 13, color: "7A85B5", fontFace: "Calibri", isTextBox: true, margin: 0,
  });
}

// ---------------- Slide 2: Problem Statement ----------------
{
  const s = pres.addSlide();
  lightBg(s);
  s.addText("Problem Statement", { x: 0.6, y: 0.5, w: 12, h: 0.8, fontSize: 34, bold: true, color: DARK_TEXT, fontFace: "Cambria", isTextBox: true, margin: 0 });
  s.addText(
    "Retail businesses generate large volumes of transactional sales data, but manually analyzing it to " +
    "understand trends and forecast future sales is slow and error-prone.",
    { x: 0.6, y: 1.6, w: 7.2, h: 1.6, fontSize: 18, color: DARK_TEXT, fontFace: "Calibri", isTextBox: true, margin: 0, valign: "top" }
  );
  s.addText(
    "SalesSense builds a scalable system that processes historical sales data with Apache Spark, engineers " +
    "features, trains a Spark MLlib Linear Regression model to predict sales, evaluates it with standard " +
    "regression metrics, and presents everything through an interactive dashboard.",
    { x: 0.6, y: 3.1, w: 7.2, h: 2.2, fontSize: 16, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0, valign: "top" }
  );
  // Right side stat callout card
  s.addShape(pres.ShapeType.roundRect, { x: 8.3, y: 1.6, w: 4.3, h: 4.3, rectRadius: 0.12, fill: { color: CARD_BG }, line: { type: "none" } });
  s.addText("9,994", { x: 8.3, y: 2.0, w: 4.3, h: 1.0, align: "center", fontSize: 48, bold: true, color: INDIGO, fontFace: "Cambria", isTextBox: true, margin: 0 });
  s.addText("real sales transactions", { x: 8.3, y: 2.95, w: 4.3, h: 0.4, align: "center", fontSize: 14, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0 });
  s.addText("4 years", { x: 8.3, y: 3.6, w: 4.3, h: 0.7, align: "center", fontSize: 30, bold: true, color: ACCENT, fontFace: "Cambria", isTextBox: true, margin: 0 });
  s.addText("of order history (2014-2017)", { x: 8.3, y: 4.25, w: 4.3, h: 0.4, align: "center", fontSize: 14, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0 });
  s.addText("21 columns", { x: 8.3, y: 4.9, w: 4.3, h: 0.7, align: "center", fontSize: 30, bold: true, color: INDIGO, fontFace: "Cambria", isTextBox: true, margin: 0 });
  s.addText("across product, customer & order data", { x: 8.3, y: 5.55, w: 4.3, h: 0.4, align: "center", fontSize: 14, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0 });
  footer(s, 2);
}

// ---------------- Slide 3: Motivation ----------------
{
  const s = pres.addSlide();
  lightBg(s);
  s.addText("Motivation", { x: 0.6, y: 0.5, w: 12, h: 0.8, fontSize: 34, bold: true, color: DARK_TEXT, fontFace: "Cambria", isTextBox: true, margin: 0 });

  const items = [
    ["Scale matters", "Single-machine tools (pandas, spreadsheets) struggle as sales datasets grow; Spark is the industry standard for distributed data processing."],
    ["Industry relevance", "Building an ML pipeline directly on Spark's DataFrame + MLlib APIs mirrors real production data-engineering workflows."],
    ["Beyond the notebook", "A polished, working web application demonstrates a deployable system, not just an isolated analysis script."],
  ];
  let y = 1.7;
  items.forEach(([title, desc]) => {
    s.addShape(pres.ShapeType.ellipse, { x: 0.6, y: y + 0.05, w: 0.45, h: 0.45, fill: { color: INDIGO }, line: { type: "none" } });
    s.addText(title, { x: 1.3, y: y, w: 10.5, h: 0.4, fontSize: 18, bold: true, color: DARK_TEXT, fontFace: "Calibri", isTextBox: true, margin: 0 });
    s.addText(desc, { x: 1.3, y: y + 0.42, w: 10.9, h: 0.7, fontSize: 14, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0 });
    y += 1.55;
  });
  footer(s, 3);
}

// ---------------- Slide 4: Objectives ----------------
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("Objectives", { x: 0.6, y: 0.5, w: 12, h: 0.8, fontSize: 34, bold: true, color: WHITE, fontFace: "Cambria", isTextBox: true, margin: 0 });
  const objs = [
    "Inspect a real dataset & report actual quality metrics",
    "Clean & preprocess data using PySpark's DataFrame API",
    "Engineer features without target leakage",
    "Build a Spark ML Pipeline: Indexer → Encoder → Assembler → Scaler → Regressor",
    "Train & evaluate with RMSE / MAE / R² on real held-out data",
    "Deliver an interactive Streamlit + Plotly GUI",
  ];
  const colW = 5.9;
  objs.forEach((t, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * (colW + 0.3);
    const y = 1.8 + row * 1.55;
    s.addShape(pres.ShapeType.roundRect, { x, y, w: colW, h: 1.3, rectRadius: 0.1, fill: { color: "283073" }, line: { type: "none" } });
    s.addText(String(i + 1).padStart(2, "0"), { x: x + 0.25, y: y + 0.15, w: 1, h: 0.5, fontSize: 22, bold: true, color: ACCENT, fontFace: "Cambria", isTextBox: true, margin: 0 });
    s.addText(t, { x: x + 0.25, y: y + 0.62, w: colW - 0.5, h: 0.6, fontSize: 13.5, color: WHITE, fontFace: "Calibri", isTextBox: true, margin: 0, valign: "top" });
  });
  footer(s, 4);
}

// ---------------- Slide 5: Dataset ----------------
{
  const s = pres.addSlide();
  lightBg(s);
  s.addText("Dataset: Sample Superstore", { x: 0.6, y: 0.5, w: 12, h: 0.8, fontSize: 32, bold: true, color: DARK_TEXT, fontFace: "Cambria", isTextBox: true, margin: 0 });
  s.addText("Source: Kaggle (vivek468/superstore-dataset-final) — inspected, not assumed", { x: 0.6, y: 1.2, w: 12, h: 0.4, fontSize: 15, italics: true, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0 });

  const rows = [
    ["Rows", "9,994"], ["Columns (raw)", "21"], ["Missing values", "0"], ["Duplicate rows", "0"],
    ["Date range", "2014 – 2017"], ["Categories", "3 (Office Supplies, Furniture, Technology)"],
    ["Sub-categories", "17"], ["Regions", "4"],
  ];
  let y = 1.85;
  rows.forEach(([k, v], i) => {
    const col = i % 2, r = Math.floor(i / 2);
    const x = 0.6 + col * 6.2;
    const yy = y + r * 0.85;
    s.addShape(pres.ShapeType.roundRect, { x, y: yy, w: 5.9, h: 0.7, rectRadius: 0.08, fill: { color: CARD_BG }, line: { type: "none" } });
    s.addText(k, { x: x + 0.25, y: yy, w: 3.2, h: 0.7, fontSize: 14, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0, valign: "middle" });
    s.addText(v, { x: x + 2.6, y: yy, w: 3.1, h: 0.7, fontSize: 15, bold: true, color: INDIGO, fontFace: "Calibri", isTextBox: true, margin: 0, valign: "middle", align: "right" });
  });
  s.addText("Target variable: Sales (₹0.44 – ₹22,638). Profit excluded from features — it is derived from Sales (corr. 0.48) and would leak the target.", {
    x: 0.6, y: 5.65, w: 12, h: 0.6, fontSize: 13, italics: true, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0,
  });
  footer(s, 5);
}

// ---------------- Slide 6: Proposed System ----------------
{
  const s = pres.addSlide();
  lightBg(s);
  s.addText("Proposed System", { x: 0.6, y: 0.5, w: 12, h: 0.8, fontSize: 34, bold: true, color: DARK_TEXT, fontFace: "Cambria", isTextBox: true, margin: 0 });
  const layers = [
    ["Data & ML Layer", "Apache Spark cleans data, engineers features, trains & evaluates a Linear Regression model via Spark MLlib.", INDIGO],
    ["Persistence Layer", "The fitted Spark ML Pipeline (all stages) is saved to disk as a single reloadable artifact.", ACCENT],
    ["Application Layer", "Streamlit loads the saved model and exposes dashboard, prediction, and analytics pages.", "2A9D8F"],
  ];
  let x = 0.6;
  const w = 3.9;
  layers.forEach(([title, desc, color], i) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 2.0, w, h: 3.6, rectRadius: 0.12, fill: { color: CARD_BG }, line: { type: "none" } });
    s.addShape(pres.ShapeType.roundRect, { x: x + 0.3, y: 2.3, w: 0.9, h: 0.9, rectRadius: 0.45, fill: { color }, line: { type: "none" } });
    s.addText(String(i + 1), { x: x + 0.3, y: 2.3, w: 0.9, h: 0.9, align: "center", valign: "middle", fontSize: 26, bold: true, color: WHITE, fontFace: "Cambria", isTextBox: true, margin: 0 });
    s.addText(title, { x: x + 0.3, y: 3.4, w: w - 0.6, h: 0.5, fontSize: 17, bold: true, color: DARK_TEXT, fontFace: "Calibri", isTextBox: true, margin: 0 });
    s.addText(desc, { x: x + 0.3, y: 3.95, w: w - 0.6, h: 1.5, fontSize: 12.5, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0, valign: "top" });
    if (i < 2) {
      s.addText("→", { x: x + w, y: 3.5, w: 0.4, h: 0.6, align: "center", fontSize: 26, bold: true, color: MUTED, isTextBox: true, margin: 0 });
    }
    x += w + 0.4;
  });
  footer(s, 6);
}

// ---------------- Slide 7: System Architecture ----------------
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("System Architecture", { x: 0.6, y: 0.45, w: 12, h: 0.7, fontSize: 32, bold: true, color: WHITE, fontFace: "Cambria", isTextBox: true, margin: 0 });
  const steps = [
    "Raw CSV", "Spark: Clean", "Feature\nEngineering", "Spark ML\nPipeline", "Linear\nRegression", "Saved\nModel", "Streamlit\nApp",
  ];
  const n = steps.length;
  const boxW = 1.55, gap = 0.28;
  const totalW = n * boxW + (n - 1) * gap;
  let x = (13.33 - totalW) / 2;
  const y = 3.1;
  steps.forEach((t, i) => {
    const isModel = t.includes("Saved");
    s.addShape(pres.ShapeType.roundRect, {
      x, y, w: boxW, h: 1.2, rectRadius: 0.08,
      fill: { color: isModel ? ACCENT : "283073" }, line: { color: "4A5490", width: 1 },
    });
    s.addText(t, { x, y, w: boxW, h: 1.2, align: "center", valign: "middle", fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri", isTextBox: true, margin: 0 });
    if (i < n - 1) {
      s.addText("→", { x: x + boxW, y, w: gap, h: 1.2, align: "center", valign: "middle", fontSize: 16, bold: true, color: "9AA5CE", isTextBox: true, margin: 0 });
    }
    x += boxW + gap;
  });
  s.addText("Every arrow above is real Spark computation — loading, cleaning, feature transforms, training and inference all run through Spark's DataFrame & MLlib APIs.", {
    x: 0.8, y: 5.0, w: 11.7, h: 0.8, align: "center", fontSize: 14, italics: true, color: "B9C2EC", fontFace: "Calibri", isTextBox: true, margin: 0,
  });
  footer(s, 7);
}

// ---------------- Slide 8: Methodology ----------------
{
  const s = pres.addSlide();
  lightBg(s);
  s.addText("Methodology", { x: 0.6, y: 0.5, w: 12, h: 0.8, fontSize: 34, bold: true, color: DARK_TEXT, fontFace: "Cambria", isTextBox: true, margin: 0 });
  const steps = [
    "Ingest CSV into a Spark DataFrame with schema inference",
    "Clean: handle nulls, duplicates, type casts, date parsing",
    "Engineer features: Order_Month, Order_DayOfWeek",
    "Split 80% train / 20% test (seed = 42)",
    "Fit the full Pipeline on the training set only (no leakage)",
    "Evaluate on the held-out test set with RMSE / MAE / R²",
    "Persist the fitted PipelineModel for reuse at inference time",
  ];
  let y = 1.65;
  steps.forEach((t, i) => {
    s.addShape(pres.ShapeType.roundRect, { x: 0.6, y, w: 0.5, h: 0.5, rectRadius: 0.08, fill: { color: i % 2 === 0 ? INDIGO : ACCENT }, line: { type: "none" } });
    s.addText(String(i + 1), { x: 0.6, y, w: 0.5, h: 0.5, align: "center", valign: "middle", fontSize: 16, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(t, { x: 1.3, y: y + 0.02, w: 11.3, h: 0.5, fontSize: 15, color: DARK_TEXT, fontFace: "Calibri", isTextBox: true, margin: 0, valign: "middle" });
    y += 0.68;
  });
  footer(s, 8);
}

// ---------------- Slide 9: Spark + MLlib Implementation ----------------
{
  const s = pres.addSlide();
  lightBg(s);
  s.addText("Spark + MLlib Implementation", { x: 0.6, y: 0.5, w: 12, h: 0.8, fontSize: 30, bold: true, color: DARK_TEXT, fontFace: "Cambria", isTextBox: true, margin: 0 });

  const pipelineStages = [
    "5× StringIndexer", "5× OneHotEncoder", "VectorAssembler", "StandardScaler", "LinearRegression",
  ];
  let x = 0.6;
  const w = 2.28;
  pipelineStages.forEach((t, i) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.7, w, h: 0.9, rectRadius: 0.1, fill: { color: i === pipelineStages.length - 1 ? ACCENT : INDIGO }, line: { type: "none" } });
    s.addText(t, { x, y: 1.7, w, h: 0.9, align: "center", valign: "middle", fontSize: 12.5, bold: true, color: WHITE, fontFace: "Calibri", isTextBox: true, margin: 0 });
    if (i < pipelineStages.length - 1) {
      s.addText("→", { x: x + w - 0.05, y: 1.7, w: 0.35, h: 0.9, align: "center", valign: "middle", fontSize: 14, bold: true, color: MUTED, isTextBox: true, margin: 0 });
    }
    x += w + 0.28;
  });

  s.addText("Why Spark?", { x: 0.6, y: 3.0, w: 6, h: 0.5, fontSize: 18, bold: true, color: DARK_TEXT, fontFace: "Calibri", isTextBox: true, margin: 0 });
  s.addText(
    "local[*] uses every CPU core on this machine — the exact same code would run unchanged on a " +
    "multi-node cluster by only changing the master URL. Spark performs the CSV load, cleaning, feature " +
    "transforms, aggregations, training AND inference — not just a token import.",
    { x: 0.6, y: 3.5, w: 6, h: 1.9, fontSize: 13.5, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0, valign: "top" }
  );

  s.addShape(pres.ShapeType.roundRect, { x: 7.0, y: 3.0, w: 5.6, h: 3.1, rectRadius: 0.12, fill: { color: CARD_BG }, line: { type: "none" } });
  s.addText("Feature Vector", { x: 7.3, y: 3.2, w: 5, h: 0.4, fontSize: 15, bold: true, color: DARK_TEXT, fontFace: "Calibri", isTextBox: true, margin: 0 });
  s.addText("35 dimensions", { x: 7.3, y: 3.6, w: 5, h: 0.6, fontSize: 30, bold: true, color: INDIGO, fontFace: "Cambria", isTextBox: true, margin: 0 });
  s.addText("4 numeric (Quantity, Discount, Order_Month, Order_DayOfWeek) + 5 one-hot encoded categoricals (Category, Sub_Category, Segment, Region, Ship_Mode)", {
    x: 7.3, y: 4.3, w: 5, h: 1.6, fontSize: 12.5, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0, valign: "top",
  });
  footer(s, 9);
}

// ---------------- Slide 10: GUI / Screenshots ----------------
{
  const s = pres.addSlide();
  lightBg(s);
  s.addText("The Application", { x: 0.6, y: 0.4, w: 12, h: 0.7, fontSize: 32, bold: true, color: DARK_TEXT, fontFace: "Cambria", isTextBox: true, margin: 0 });
  s.addText("Six pages: Dashboard · Prediction · Batch Prediction · Model Performance · Analytics · About", {
    x: 0.6, y: 1.05, w: 12, h: 0.4, fontSize: 14, italics: true, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0,
  });
  s.addImage({ path: path.join(SCREENSHOTS, "01_dashboard.png"), x: 0.6, y: 1.6, w: 6.0, h: 4.1, sizing: { type: "contain", w: 6.0, h: 4.1 } });
  s.addImage({ path: path.join(SCREENSHOTS, "02_prediction.png"), x: 6.8, y: 1.6, w: 6.0, h: 4.1, sizing: { type: "contain", w: 6.0, h: 4.1 } });
  s.addText("Dashboard — live KPIs & trends", { x: 0.6, y: 5.75, w: 6.0, h: 0.35, align: "center", fontSize: 12, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0 });
  s.addText("Sales Prediction — single-record form", { x: 6.8, y: 5.75, w: 6.0, h: 0.35, align: "center", fontSize: 12, color: MUTED, fontFace: "Calibri", isTextBox: true, margin: 0 });
  footer(s, 10);
}

// ---------------- Slide 11: Results & Evaluation ----------------
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("Results & Evaluation", { x: 0.6, y: 0.45, w: 12, h: 0.7, fontSize: 32, bold: true, color: WHITE, fontFace: "Cambria", isTextBox: true, margin: 0 });
  s.addText("Real metrics from an actual training run — 8,042 train / 1,952 test rows, seed = 42", {
    x: 0.6, y: 1.1, w: 12, h: 0.4, fontSize: 14, italics: true, color: "9AA5CE", fontFace: "Calibri", isTextBox: true, margin: 0,
  });

  const metrics = [["RMSE", "536.33", INDIGO], ["MAE", "227.99", ACCENT], ["R²", "0.292", "2A9D8F"]];
  let x = 0.8;
  metrics.forEach(([label, val, color]) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.9, w: 3.7, h: 2.0, rectRadius: 0.12, fill: { color: "283073" }, line: { type: "none" } });
    s.addText(val, { x, y: 2.1, w: 3.7, h: 1.0, align: "center", fontSize: 42, bold: true, color, fontFace: "Cambria", isTextBox: true, margin: 0 });
    s.addText(label, { x, y: 3.15, w: 3.7, h: 0.5, align: "center", fontSize: 15, color: WHITE, fontFace: "Calibri", isTextBox: true, margin: 0 });
    x += 4.0;
  });

  s.addText(
    "Test performance (RMSE 536.33, R² 0.292) is close to — and slightly better than — training " +
    "performance (RMSE 540.82, R² 0.238), showing the model is NOT overfitting. Its modest R² reflects the " +
    "purely linear model applied to a heavily right-skewed Sales target (₹0.44 – ₹22,638), not a data or " +
    "pipeline flaw.",
    { x: 0.8, y: 4.3, w: 11.7, h: 1.4, fontSize: 14, color: "CBD5E1", fontFace: "Calibri", isTextBox: true, margin: 0, valign: "top" }
  );
  s.addText("Training completed in 7.11 seconds on local[*] Spark  ·  Model verified: single & batch prediction tested with real inputs", {
    x: 0.8, y: 6.0, w: 11.7, h: 0.5, fontSize: 12.5, italics: true, color: "7A85B5", fontFace: "Calibri", isTextBox: true, margin: 0,
  });
  footer(s, 11);
}

// ---------------- Slide 12: Conclusion & Future Scope ----------------
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("Conclusion & Future Scope", { x: 0.6, y: 0.5, w: 12, h: 0.8, fontSize: 32, bold: true, color: WHITE, fontFace: "Cambria", isTextBox: true, margin: 0 });

  s.addText("Conclusion", { x: 0.6, y: 1.6, w: 5.8, h: 0.4, fontSize: 18, bold: true, color: ICE, fontFace: "Calibri", isTextBox: true, margin: 0 });
  s.addText(
    "SalesSense delivers a complete, working pipeline — Spark-based cleaning, feature engineering, " +
    "MLlib training/evaluation, and a polished Streamlit GUI — with every stage actually executed and " +
    "verified, not assumed.",
    { x: 0.6, y: 2.05, w: 5.8, h: 2.0, fontSize: 14, color: "CBD5E1", fontFace: "Calibri", isTextBox: true, margin: 0, valign: "top" }
  );

  s.addText("Future Scope", { x: 6.9, y: 1.6, w: 5.8, h: 0.4, fontSize: 18, bold: true, color: ICE, fontFace: "Calibri", isTextBox: true, margin: 0 });
  const future = [
    "Tree-based Spark MLlib models (Random Forest, GBT)",
    "Hyperparameter tuning via CrossValidator",
    "Log-transform the skewed Sales target",
    "Deploy on a real multi-node Spark cluster",
  ];
  let y = 2.05;
  future.forEach((t) => {
    s.addText("• " + t, { x: 6.9, y, w: 5.8, h: 0.5, fontSize: 14, color: "CBD5E1", fontFace: "Calibri", isTextBox: true, margin: 0 });
    y += 0.5;
  });

  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 5.9, w: 12.1, h: 0.02, fill: { color: "3A4488" } });
  s.addText("Thank You", { x: 0.6, y: 6.15, w: 12.1, h: 0.9, align: "center", fontSize: 30, bold: true, color: WHITE, fontFace: "Cambria", isTextBox: true, margin: 0 });
  footer(s, 12);
}

pres.writeFile({ fileName: "SalesSense_Presentation.pptx" }).then(() => console.log("Deck written."));
