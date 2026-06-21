const fs = require('fs');
const path = require('path');
const db = require('../db');

class ImportService {
  // 从文件导入
  static importFile(filePath, originalName) {
    const ext = path.extname(originalName).toLowerCase();
    const content = fs.readFileSync(filePath, 'utf-8');

    let entries = [];

    if (ext === '.json') {
      entries = this.parseJSON(content);
    } else if (ext === '.md' || ext === '.markdown') {
      entries = this.parseMarkdown(content);
    } else {
      throw new Error(`不支持的文件格式: ${ext}，仅支持 .md 和 .json`);
    }

    if (entries.length === 0) {
      throw new Error('未能从文件中解析出任何问答条目');
    }

    const imported = [];
    const errors = [];

    for (const entry of entries) {
      try {
        if (!entry.question || !entry.answer) {
          errors.push({ entry, error: '问题和答案不能为空' });
          continue;
        }

        // 处理分类
        let categoryId = null;
        if (entry.category) {
          db.run('INSERT OR IGNORE INTO categories (name) VALUES (?)', [entry.category]);
          const cat = db.get('SELECT id FROM categories WHERE name = ?', [entry.category]);
          categoryId = cat ? cat.id : null;
        }

        // 插入问答
        const result = db.run(`
          INSERT INTO qa_entries (question, answer, category_id, tags, source_file)
          VALUES (?, ?, ?, ?, ?)
        `, [
          entry.question.trim(),
          entry.answer.trim(),
          categoryId || null,
          JSON.stringify(entry.tags || []),
          originalName
        ]);

        imported.push({
          id: result.lastInsertRowid,
          question: entry.question.trim(),
          category: entry.category || null
        });
      } catch (err) {
        errors.push({ entry: entry.question || '(无问题)', error: err.message });
      }
    }

    return {
      total: entries.length,
      imported: imported.length,
      errors: errors.length > 0 ? errors : undefined
    };
  }

  // 解析 JSON 格式
  static parseJSON(content) {
    let data;
    try {
      data = JSON.parse(content);
    } catch (e) {
      throw new Error('JSON 格式解析失败: ' + e.message);
    }

    if (!Array.isArray(data)) {
      if (typeof data === 'object' && data.question) {
        data = [data];
      } else {
        throw new Error('JSON 格式要求为数组或包含 question 字段的对象');
      }
    }

    return data.map(item => ({
      question: item.question || item.q || item.title || '',
      answer: item.answer || item.a || item.content || '',
      category: item.category || item.cat || null,
      tags: Array.isArray(item.tags) ? item.tags : [],
    }));
  }

  // 解析 Markdown 格式
  static parseMarkdown(content) {
    const entries = [];
    const lines = content.split('\n');

    let currentCategory = null;
    let currentQuestion = null;
    let currentAnswer = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // # 一级标题：分类名
      if (/^# [^#]/.test(line)) {
        // 如果正在解析一个问题，先保存
        if (currentQuestion) {
          entries.push({
            question: currentQuestion,
            answer: currentAnswer.join('\n').trim(),
            category: currentCategory,
            tags: [],
          });
          currentAnswer = [];
          currentQuestion = null;
        }
        currentCategory = line.replace(/^# /, '').trim();
        continue;
      }

      // ## 二级标题：问题
      if (/^## /.test(line)) {
        // 保存前一个问答
        if (currentQuestion) {
          entries.push({
            question: currentQuestion,
            answer: currentAnswer.join('\n').trim(),
            category: currentCategory,
            tags: [],
          });
          currentAnswer = [];
        }
        currentQuestion = line.replace(/^## /, '').trim();
        continue;
      }

      // 问题下的答案内容
      if (currentQuestion) {
        currentAnswer.push(line);
      }
    }

    // 保存最后一个问答
    if (currentQuestion) {
      entries.push({
        question: currentQuestion,
        answer: currentAnswer.join('\n').trim(),
        category: currentCategory,
        tags: [],
      });
    }

    return entries;
  }

  // 清理上传文件
  static cleanupFile(filePath) {
    try {
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
    } catch (e) {
      console.error('清理文件失败:', e.message);
    }
  }
}

module.exports = ImportService;
