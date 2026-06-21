/**
 * 智能搜索引擎
 * - 中英文混合分词
 * - 多维度相关性评分
 * - 模糊匹配
 * - 结果排名
 */
const db = require('../db');

class SearchEngine {
  /**
   * 分词：将搜索字符串拆分为有意义的词元
   * 中文：单字 + 双字组合（bigram）
   * 英文：按空格和标点分词，去除停用词
   * 数字/混合：整体保留
   */
  static tokenize(text) {
    if (!text || !text.trim()) return [];
    const raw = text.trim().toLowerCase();
    const tokens = new Set();

    // 提取英文单词和数字
    const enWords = raw.match(/[a-z0-9]+/g) || [];
    enWords.forEach(w => {
      if (w.length >= 1 && !this.isStopWord(w)) {
        tokens.add(w);
      }
    });

    // 提取中文片段（连续的中文字符）
    const zhSegments = raw.match(/[一-鿿]+/g) || [];
    zhSegments.forEach(seg => {
      // 单字
      for (let i = 0; i < seg.length; i++) {
        tokens.add(seg[i]);
      }
      // 双字 bigram（提升精确度）
      for (let i = 0; i < seg.length - 1; i++) {
        tokens.add(seg[i] + seg[i + 1]);
      }
      // 完整片段（精确匹配）
      if (seg.length >= 2) {
        tokens.add(seg);
      }
    });

    // 原始整体查询（用于精确短语匹配加分）
    return { tokens: [...tokens], original: raw };
  }

  static isStopWord(word) {
    const stops = new Set([
      'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been',
      'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
      'and', 'or', 'not', 'but', 'if', 'than', 'then', 'so',
      'it', 'its', 'this', 'that', 'these', 'those',
      'what', 'which', 'who', 'how', 'when', 'where',
      'can', 'will', 'would', 'could', 'should', 'may',
      '的', '了', '在', '是', '我', '有', '和', '就',
      '不', '人', '都', '一', '一个', '上', '也', '很',
      '到', '说', '要', '去', '你', '会', '着', '没有',
      '看', '好', '自己', '这'
    ]);
    return stops.has(word);
  }

  /**
   * 计算单条问答与搜索词的匹配分数
   */
  static score(item, tokens, originalQuery) {
    const question = (item.question || '').toLowerCase();
    const answer = (item.answer || '').toLowerCase();
    const tags = (item.tags || []).join(' ').toLowerCase();

    let score = 0;
    const matchedTokens = new Set();
    const matchDetails = [];

    for (const token of tokens) {
      let tokenScore = 0;
      let matchField = '';

      // 问题标题匹配（权重最高）
      const qIdx = question.indexOf(token);
      if (qIdx !== -1) {
        tokenScore += 15;
        matchField = 'question';
        // 问题开头匹配加分
        if (qIdx === 0) tokenScore += 10;
        // 完整词边界匹配加分
        if (this.isWordBoundary(question, qIdx, token.length)) tokenScore += 5;
      }

      // 答案内容匹配
      const aIdx = answer.indexOf(token);
      if (aIdx !== -1) {
        tokenScore += 5;
        matchField = matchField || 'answer';
        // 答案中出现多次加分
        let count = 0, pos = answer.indexOf(token);
        while (pos !== -1) { count++; pos = answer.indexOf(token, pos + 1); }
        if (count > 1) tokenScore += Math.min(count, 5) * 2;
      }

      // 标签匹配
      if (tags.includes(token)) {
        tokenScore += 8;
        matchField = matchField || 'tags';
      }

      if (tokenScore > 0) {
        matchedTokens.add(token);
        score += tokenScore;
        matchDetails.push({ token, field: matchField });
      }
    }

    // 完整短语匹配（大幅加分）
    if (originalQuery.length >= 2) {
      if (question.includes(originalQuery)) score += 25;
      else if (answer.includes(originalQuery)) score += 10;
    }

    // 所有词都匹配到的加分
    if (matchedTokens.size === tokens.length && tokens.length > 0) {
      score += 20;
    }

    // 问题越短越精准（在匹配的情况下）
    if (matchedTokens.size > 0 && question.length < 30) {
      score += 5;
    }

    return {
      score,
      matchedTokens: matchedTokens.size,
      totalTokens: tokens.length,
      matchDetails
    };
  }

  static isWordBoundary(text, idx, len) {
    const before = idx === 0 || /[\s，。！？,.!?\-—]/.test(text[idx - 1]);
    const after = idx + len >= text.length || /[\s，。！？,.!?\-—]/.test(text[idx + len]);
    return before || after;
  }

  /**
   * 主搜索方法
   */
  static search(keyword, options = {}) {
    const { limit = 50, category } = options;

    if (!keyword || !keyword.trim()) return [];
    const { tokens, original } = this.tokenize(keyword);
    if (tokens.length === 0) return [];

    // 第一阶段：用 LIKE 从数据库捞出候选集（多词 OR 匹配）
    let whereConditions = [];
    let params = [];

    for (const token of tokens) {
      const like = `%${token}%`;
      whereConditions.push(`(q.question LIKE ? OR q.answer LIKE ? OR q.tags LIKE ?)`);
      params.push(like, like, like);
    }

    let whereClause = `WHERE (${whereConditions.join(' OR ')})`;
    if (category) {
      whereClause += ` AND q.category_id = ?`;
      params.push(parseInt(category));
    }

    // 限制候选集大小，避免太多数据
    const candidates = db.all(`
      SELECT q.*, c.name as category_name
      FROM qa_entries q
      LEFT JOIN categories c ON q.category_id = c.id
      ${whereClause}
      LIMIT 200
    `, params);

    // 第二阶段：JavaScript 精确打分
    candidates.forEach(item => {
      try { item.tags = JSON.parse(item.tags); } catch { item.tags = []; }
      const { score, matchedTokens, totalTokens, matchDetails } = this.score(item, tokens, original);
      item._score = score;
      item._matchedTokens = matchedTokens;
      item._totalTokens = totalTokens;
    });

    // 第三阶段：排序、截断
    const results = candidates
      .filter(c => c._score > 0)                    // 至少有一个词匹配
      .sort((a, b) => b._score - a._score)           // 按分数降序
      .slice(0, limit);

    return results;
  }

  /**
   * 搜索建议/自动补全
   */
  static suggest(keyword, limit = 8) {
    if (!keyword || !keyword.trim() || keyword.trim().length < 1) return [];
    const kw = keyword.trim();
    const like = `${kw}%`;
    const likeMiddle = `%${kw}%`;

    const items = db.all(`
      SELECT DISTINCT question FROM qa_entries
      WHERE question LIKE ? OR question LIKE ?
      ORDER BY question LIKE ? DESC, updated_at DESC
      LIMIT ?
    `, [like, likeMiddle, like, limit]);

    return items.map(i => i.question);
  }

  /**
   * 生成搜索结果摘要（包含关键词上下文）
   */
  static generateSnippet(answer, tokens, maxLen = 120) {
    if (!answer) return '';

    const lowerAnswer = answer.toLowerCase();
    let bestPos = -1;
    let bestToken = '';

    // 找到第一个匹配位置
    for (const token of tokens) {
      const pos = lowerAnswer.indexOf(token);
      if (pos !== -1 && (bestPos === -1 || pos < bestPos)) {
        bestPos = pos;
        bestToken = token;
      }
    }

    if (bestPos === -1) {
      return answer.length > maxLen ? answer.slice(0, maxLen) + '...' : answer;
    }

    const tokenLen = bestToken.length;
    const contextLen = Math.floor((maxLen - tokenLen) / 2);
    let start = Math.max(0, bestPos - contextLen);
    let end = Math.min(answer.length, bestPos + tokenLen + contextLen);

    // 调整到词边界
    if (start > 0) {
      const boundary = answer.lastIndexOf('。', start);
      if (boundary !== -1 && boundary > start - 20) start = boundary + 1;
    }
    if (end < answer.length) {
      const boundary = answer.indexOf('。', end);
      if (boundary !== -1 && boundary < end + 20) end = boundary;
    }

    let snippet = answer.slice(start, end).trim();
    if (start > 0) snippet = '...' + snippet;
    if (end < answer.length) snippet = snippet + '...';

    return snippet;
  }
}

module.exports = SearchEngine;
