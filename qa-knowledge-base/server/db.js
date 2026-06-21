const initSqlJs = require('sql.js');
const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, 'knowledge_base.db');

let db = null;
let SQL = null;

// 初始化数据库（异步，应用启动时调用一次）
async function initDB() {
  SQL = await initSqlJs();

  if (fs.existsSync(DB_PATH)) {
    const buffer = fs.readFileSync(DB_PATH);
    db = new SQL.Database(buffer);
  } else {
    db = new SQL.Database();
  }

  db.run('PRAGMA foreign_keys = ON');

  // 创建分类表
  db.run(`
    CREATE TABLE IF NOT EXISTS categories (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // 创建问答表
  db.run(`
    CREATE TABLE IF NOT EXISTS qa_entries (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      category_id INTEGER,
      tags TEXT DEFAULT '[]',
      source_file TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (category_id) REFERENCES categories(id)
    )
  `);

  // 创建搜索索引
  db.run(`CREATE INDEX IF NOT EXISTS idx_qa_question ON qa_entries(question)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_qa_category ON qa_entries(category_id)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_qa_updated ON qa_entries(updated_at)`);

  // 插入默认分类
  const count = db.exec('SELECT COUNT(*) as cnt FROM categories');
  if (count[0]?.values[0][0] === 0) {
    const defaults = ['通用', '技术', '生活', '工作', '学习'];
    for (const name of defaults) {
      db.run('INSERT OR IGNORE INTO categories (name) VALUES (?)', [name]);
    }
  }

  // 持久化到磁盘
  saveDB();
  console.log('数据库初始化完成');
}

// 持久化数据库到文件
function saveDB() {
  if (db) {
    const data = db.export();
    const buffer = Buffer.from(data);
    fs.writeFileSync(DB_PATH, buffer);
  }
}

// 获取数据库实例
function getDB() {
  if (!db) throw new Error('数据库未初始化，请先调用 initDB()');
  return db;
}

// ====== 封装查询方法 ======

// 转义字符串（防 SQL 注入）
function escape(str) {
  if (str === null || str === undefined) return 'NULL';
  return `'${String(str).replace(/'/g, "''")}'`;
}

// 执行 SQL 并返回所有行
function all(sql, params = []) {
  const d = getDB();
  let idx = 0;
  const escaped = sql.replace(/\?/g, () => {
    const val = params[idx++];
    if (val === null || val === undefined) return 'NULL';
    if (typeof val === 'number') return String(val);
    return escape(val);
  });
  const results = d.exec(escaped);
  if (results.length === 0) return [];

  const { columns, values } = results[0];
  return values.map(row => {
    const obj = {};
    columns.forEach((col, i) => {
      obj[col] = row[i];
    });
    return obj;
  });
}

// 执行 SQL 并返回第一行
function get(sql, params = []) {
  const rows = all(sql, params);
  return rows.length > 0 ? rows[0] : null;
}

// 执行 SQL（INSERT/UPDATE/DELETE），返回 { changes, lastInsertRowid }
function run(sql, params = []) {
  const d = getDB();
  let idx = 0;
  const escaped = sql.replace(/\?/g, () => {
    const val = params[idx++];
    if (val === null || val === undefined) return 'NULL';
    if (typeof val === 'number') return String(val);
    return escape(val);
  });
  d.run(escaped);
  const lastIdResult = d.exec('SELECT last_insert_rowid() as id');
  const lastId = lastIdResult[0]?.values[0]?.[0] || 0;
  const changes = d.getRowsModified();
  saveDB();
  return { changes, lastInsertRowid: lastId };
}

// 执行多条 SQL（用于 DDL 等）
function exec(sql) {
  const d = getDB();
  const result = d.exec(sql);
  saveDB();
  return result;
}

module.exports = { initDB, getDB, saveDB, all, get, run, exec };
