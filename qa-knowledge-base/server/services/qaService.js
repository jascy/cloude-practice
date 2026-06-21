const db = require('../db');
const SearchEngine = require('./searchEngine');

class QAService {
  // 获取问答列表（支持分页、搜索、分类筛选）
  static getList({ search, category, page = 1, limit = 20 }) {
    page = Math.max(1, parseInt(page));
    limit = Math.min(100, Math.max(1, parseInt(limit)));
    const offset = (page - 1) * limit;

    // 使用智能搜索
    if (search && search.trim()) {
      const allResults = SearchEngine.search(search, { category, limit: 200 });
      const total = allResults.length;

      // 分页截取
      const list = allResults.slice(offset, offset + limit);

      // 为每个结果生成摘要
      const tokens = SearchEngine.tokenize(search.trim());
      list.forEach(item => {
        item._snippet = SearchEngine.generateSnippet(item.answer, tokens.tokens);
      });

      return {
        list,
        pagination: { page, limit, total, totalPages: Math.ceil(total / limit) }
      };
    }

    // 无搜索词时走简单查询
    let whereClause = 'WHERE 1=1';
    const params = [];

    if (category) {
      whereClause += ` AND q.category_id = ?`;
      params.push(parseInt(category));
    }

    const countRow = db.get(`SELECT COUNT(*) as total FROM qa_entries q ${whereClause}`, params);
    const total = countRow?.total || 0;

    const list = db.all(`
      SELECT q.*, c.name as category_name
      FROM qa_entries q
      LEFT JOIN categories c ON q.category_id = c.id
      ${whereClause}
      ORDER BY q.updated_at DESC
      LIMIT ? OFFSET ?
    `, [...params, limit, offset]);

    list.forEach(item => {
      try { item.tags = JSON.parse(item.tags); } catch { item.tags = []; }
    });

    return {
      list,
      pagination: { page, limit, total, totalPages: Math.ceil(total / limit) }
    };
  }

  // 获取单条问答
  static getById(id) {
    const item = db.get(`
      SELECT q.*, c.name as category_name
      FROM qa_entries q
      LEFT JOIN categories c ON q.category_id = c.id
      WHERE q.id = ?
    `, [parseInt(id)]);

    if (item) {
      try { item.tags = JSON.parse(item.tags); } catch { item.tags = []; }
    }
    return item;
  }

  // 新增问答
  static create({ question, answer, category_id, tags, source_file }) {
    const result = db.run(`
      INSERT INTO qa_entries (question, answer, category_id, tags, source_file)
      VALUES (?, ?, ?, ?, ?)
    `, [
      question,
      answer,
      category_id || null,
      JSON.stringify(tags || []),
      source_file || null
    ]);

    return this.getById(result.lastInsertRowid);
  }

  // 更新问答
  static update(id, { question, answer, category_id, tags }) {
    db.run(`
      UPDATE qa_entries
      SET question = ?, answer = ?, category_id = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `, [question, answer, category_id || null, JSON.stringify(tags || []), parseInt(id)]);

    return this.getById(id);
  }

  // 删除问答
  static delete(id) {
    return db.run('DELETE FROM qa_entries WHERE id = ?', [parseInt(id)]);
  }

  // 智能搜索
  static search(keyword) {
    return SearchEngine.search(keyword, { limit: 50 });
  }

  // 搜索建议
  static suggest(keyword) {
    return SearchEngine.suggest(keyword);
  }

  // 获取所有分类
  static getCategories() {
    return db.all(`
      SELECT c.*, COUNT(q.id) as count
      FROM categories c
      LEFT JOIN qa_entries q ON c.id = q.category_id
      GROUP BY c.id
      ORDER BY c.id
    `);
  }
}

module.exports = QAService;
