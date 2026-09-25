const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
} = require("docx");
const fs = require("fs");

const PAGE_WIDTH = 12240, PAGE_HEIGHT = 15840; // US Letter

function heading(text) {
  return new Paragraph({
    text,
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 100 },
  });
}
function body(text) {
  return new Paragraph({
    children: [new TextRun({ text, size: 20 })],
    spacing: { after: 100 },
  });
}
function bullet(text) {
  return new Paragraph({
    children: [new TextRun({ text, size: 20 })],
    bullet: { level: 0 },
    spacing: { after: 40 },
  });
}

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: PAGE_WIDTH, height: PAGE_HEIGHT }, margin: { top: 900, bottom: 900, left: 1000, right: 1000 } } },
    children: [
      new Paragraph({
        children: [new TextRun({ text: "SalesSense", bold: true, size: 40, color: "4F46E5" })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 40 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Scalable Sales Prediction & Analytics System", bold: true, size: 24 })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 20 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "One-Page Project Proposal", italics: true, size: 20, color: "666666" })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "4F46E5" } },
      }),

      heading("Problem Statement"),
      body("Retail businesses generate large volumes of transactional sales data, but manually analyzing this data to understand trends and forecast future sales is slow and error-prone. This project develops a scalable system that processes historical sales data using Apache Spark, engineers relevant features, trains a Linear Regression model with Spark MLlib to predict sales, evaluates model performance with standard regression metrics, and presents the results through an interactive web dashboard."),

      heading("Motivation"),
      body("As sales datasets grow, single-machine tools (plain pandas scripts, spreadsheets) struggle to scale. Apache Spark is the industry-standard framework for distributed data processing, and understanding how to build an ML pipeline on top of it is directly relevant to real-world data engineering and data science roles. This project is an opportunity to apply Spark's DataFrame API and MLlib in a complete, end-to-end system rather than an isolated exercise."),

      heading("Objectives"),
      bullet("Process and clean a real-world sales dataset using PySpark's distributed DataFrame API."),
      bullet("Engineer meaningful numerical and categorical features from raw transactional data."),
      bullet("Build a Spark ML Pipeline (StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler, LinearRegression) to predict sales."),
      bullet("Evaluate the trained model using RMSE, MAE, and R² on a held-out test set."),
      bullet("Deliver an interactive Streamlit + Plotly GUI for single/batch prediction and sales analytics."),

      heading("Proposed Methodology"),
      body("The system follows a linear pipeline: raw CSV → Spark-based data cleaning (null/duplicate handling, type casting, date parsing) → feature engineering (date-part extraction, categorical encoding) → an 80/20 train-test split → a Spark ML Pipeline that assembles and scales features and fits a Linear Regression model → evaluation against RMSE/MAE/R² → the trained PipelineModel is persisted and loaded by a Streamlit application that exposes dashboard analytics, single-record prediction, and CSV-based batch prediction."),

      heading("Technologies Used"),
      body("Python 3.11, Apache Spark (PySpark 4.x), Spark MLlib, Pandas, NumPy, Streamlit, Plotly, Git/GitHub."),

      heading("Dataset"),
      body("Sample Superstore dataset, sourced from Kaggle (vivek468/superstore-dataset-final): 9,994 real US retail order line items (2014–2017), 21 original columns, used to predict order Sales from Quantity, Discount, Category/Sub-Category, Segment, Region, Ship Mode, and order date parts."),

      heading("Expected Outcome"),
      body("A working, demonstrable web application that ingests raw sales data, trains and evaluates a Spark MLlib regression model with real, reported metrics, and lets a user obtain single or batch sales predictions along with rich visual analytics of the underlying dataset."),

      heading("Future Scope"),
      body("Extending to non-linear Spark MLlib regressors (Random Forest, GBT), hyperparameter tuning via CrossValidator, deployment on a multi-node Spark cluster with larger datasets, and adding authenticated multi-user access with saved prediction history."),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("SalesSense_Project_Proposal.docx", buf);
  console.log("Proposal written.");
});
